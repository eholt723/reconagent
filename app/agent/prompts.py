PLANNER_SYSTEM = (
    "You are a research planning expert. Your job is to generate targeted search queries "
    "that will help gather comprehensive information on a research topic. "
    "Always respond with valid JSON."
)

PLANNER_USER = """Generate 3-5 targeted, specific search queries to research the following topic:

Topic: {topic}

Return a JSON object with this exact structure:
{{
  "queries": ["query 1", "query 2", "query 3"]
}}

Make queries specific and varied to cover different aspects of the topic."""


REFLECTION_SYSTEM = (
    "You are a research quality evaluator. You assess whether search results are "
    "sufficient to write a comprehensive research report, or if more targeted searches are needed. "
    "Always respond with valid JSON."
)

REFLECTION_USER = """Evaluate whether the following search results are sufficient to write a comprehensive report on the topic.

Topic: {topic}

Search Results Summary:
{results_summary}

Number of results: {result_count}
Current iteration: {iteration}

If results are sufficient, return:
{{
  "decision": "sufficient",
  "reasoning": "brief explanation"
}}

If results need improvement (and you can provide better queries), return:
{{
  "decision": "refine",
  "reasoning": "brief explanation of what is missing",
  "refined_queries": ["better query 1", "better query 2", "better query 3"]
}}

Be pragmatic — if there are at least 5-10 relevant results covering the main aspects, mark as sufficient."""


SYNTHESIS_SYSTEM = (
    "You are an expert research analyst. Write clear, well-structured research reports "
    "based on provided source material. Use markdown formatting."
)

SYNTHESIS_USER = """Write a comprehensive research report on the following topic based on the provided sources.

Topic: {topic}

Source Material:
{sources}

Structure your report with these markdown sections:

## Summary
(2-3 paragraph executive summary)

## Key Findings
(bullet points of the most important findings)

## Perspectives & Debate
(different viewpoints or areas of active discussion, if applicable)

## Sources
(list each source with title and URL as a markdown link)

Write in a clear, analytical tone. Synthesize information across sources rather than just summarizing each one."""
