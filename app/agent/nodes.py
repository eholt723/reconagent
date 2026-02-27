import asyncio
import json
import logging
from functools import partial

from groq import AsyncGroq
from tavily import TavilyClient
from groq import RateLimitError
from tenacity import retry, retry_if_not_exception_type, stop_after_attempt, wait_exponential

from app.agent.prompts import (
    PLANNER_SYSTEM,
    PLANNER_USER,
    REFLECTION_SYSTEM,
    REFLECTION_USER,
    SYNTHESIS_SYSTEM,
    SYNTHESIS_USER,
)
from app.agent.state import AgentState
from app.config import settings

logger = logging.getLogger(__name__)

groq_client = AsyncGroq(api_key=settings.groq_api_key)
tavily_client = TavilyClient(api_key=settings.tavily_api_key)


@retry(
    retry=retry_if_not_exception_type(RateLimitError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
async def _call_llm(messages: list, json_mode: bool = False) -> str:
    kwargs = {
        "model": settings.groq_model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 2048,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = await groq_client.chat.completions.create(**kwargs)
    return response.choices[0].message.content


async def _search_web(query: str) -> list:
    result = await asyncio.to_thread(
        partial(tavily_client.search, query, max_results=5)
    )
    return result.get("results", [])


async def planner_node(state: AgentState) -> dict:
    topic = state["topic"]
    logger.info("Planning queries for: %s", topic)

    try:
        response = await _call_llm(
            [
                {"role": "system", "content": PLANNER_SYSTEM},
                {"role": "user", "content": PLANNER_USER.format(topic=topic)},
            ],
            json_mode=True,
        )
        data = json.loads(response)
        queries = data.get("queries", [])[:5]
    except Exception as exc:
        logger.error("Planner error: %s", exc)
        queries = [f"{topic} overview", f"{topic} research", f"{topic} analysis"]

    events = [
        {"type": "planning", "content": f"Planning research strategy for: {topic}"},
        {"type": "planning", "content": f"Generated {len(queries)} search queries:"},
        *[{"type": "planning", "content": f'  → "{q}"'} for q in queries],
    ]

    return {
        "planned_queries": queries,
        "iteration_count": 0,
        "events": events,
    }


async def search_node(state: AgentState) -> dict:
    queries = state.get("planned_queries", [])
    existing_results = state.get("search_results", [])
    logger.info("Searching with %d queries", len(queries))

    events = [{"type": "searching", "content": f"Executing {len(queries)} web searches..."}]
    new_results = []

    for query in queries:
        events.append({"type": "searching", "content": f'Searching: "{query}"'})
        try:
            results = await _search_web(query)
            new_results.extend(results)
            events.append({"type": "searching", "content": f"  → Found {len(results)} results"})
        except Exception as exc:
            logger.error("Search error for '%s': %s", query, exc)
            events.append({"type": "searching", "content": f"  → Search failed: {str(exc)[:60]}"})

    total = len(existing_results) + len(new_results)
    events.append({"type": "searching", "content": f"Total results gathered: {total}"})

    return {
        "search_results": existing_results + new_results,
        "planned_queries": [],
        "events": events,
    }


async def reflection_node(state: AgentState) -> dict:
    topic = state["topic"]
    results = state.get("search_results", [])
    iteration = state.get("iteration_count", 0)
    logger.info("Reflecting on %d results (iteration %d)", len(results), iteration)

    results_summary = "\n".join(
        f"- [{r.get('title', 'No title')}] {r.get('content', r.get('snippet', ''))[:300]}"
        for r in results[:12]
    )

    events = [
        {"type": "reflecting", "content": f"Evaluating {len(results)} search results for adequacy..."},
    ]

    try:
        response = await _call_llm(
            [
                {"role": "system", "content": REFLECTION_SYSTEM},
                {"role": "user", "content": REFLECTION_USER.format(
                    topic=topic,
                    results_summary=results_summary,
                    result_count=len(results),
                    iteration=iteration,
                )},
            ],
            json_mode=True,
        )
        data = json.loads(response)
        decision = data.get("decision", "sufficient")
        reasoning = data.get("reasoning", "")
        refined_queries = data.get("refined_queries", [])
    except RateLimitError:
        logger.error("Reflection hit rate limit after retries")
        decision = "sufficient"
        reasoning = "Rate limit reached — proceeding with available results"
        refined_queries = []
    except Exception as exc:
        logger.error("Reflection error: %s", exc)
        decision = "sufficient"
        reasoning = "Proceeding with available results"
        refined_queries = []

    if decision == "refine" and iteration < 2 and refined_queries:
        events.append({"type": "reflecting", "content": f"Results need improvement: {reasoning}"})
        events.append({"type": "reflecting", "content": f"Refining search with {len(refined_queries)} new queries..."})
        return {
            "iteration_count": iteration + 1,
            "reflection_sufficient": False,
            "planned_queries": refined_queries[:5],
            "events": events,
        }

    events.append({"type": "reflecting", "content": f"Results are sufficient: {reasoning}"})
    events.append({"type": "reflecting", "content": "Proceeding to report synthesis..."})
    return {
        "iteration_count": iteration + 1,
        "reflection_sufficient": True,
        "planned_queries": [],
        "events": events,
    }


async def synthesis_node(state: AgentState) -> dict:
    topic = state["topic"]
    results = state.get("search_results", [])
    logger.info("Synthesizing report from %d results", len(results))

    # Deduplicate by URL
    seen_urls: set = set()
    unique_results = []
    for r in results:
        url = r.get("url", "")
        if url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(r)

    sources_text = "\n\n".join(
        f"Title: {r.get('title', 'Unknown')}\n"
        f"URL: {r.get('url', '')}\n"
        f"Content: {r.get('content', r.get('snippet', ''))[:600]}"
        for r in unique_results[:15]
    )

    events = [
        {"type": "synthesizing", "content": f"Synthesizing report from {len(unique_results)} unique sources..."},
    ]

    try:
        report = await _call_llm(
            [
                {"role": "system", "content": SYNTHESIS_SYSTEM},
                {"role": "user", "content": SYNTHESIS_USER.format(topic=topic, sources=sources_text)},
            ],
            json_mode=False,
        )
    except RateLimitError:
        logger.error("Synthesis hit rate limit")
        events.append({"type": "error", "content": "Groq free-tier rate limit reached. This demo runs on llama-3.3-70b-versatile via Groq's free API — swapping to a paid tier or a different model removes this restriction. Please wait ~60 seconds and try again."})
        return {"final_report": "", "events": events}
    except Exception as exc:
        logger.error("Synthesis error: %s", exc)
        events.append({"type": "error", "content": "Unexpected error generating report. Please try again."})
        return {"final_report": "", "events": events}

    events.append({"type": "synthesizing", "content": "Report complete."})
    events.append({"type": "report", "content": report})

    return {
        "final_report": report,
        "events": events,
    }
