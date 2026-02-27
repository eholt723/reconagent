import json
import logging

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agent.graph import research_graph

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/research", tags=["research"])


class ResearchRequest(BaseModel):
    topic: str


@router.post("/stream")
async def stream_research(request: Request, body: ResearchRequest):
    async def event_generator():
        initial_state = {
            "topic": body.topic,
            "planned_queries": [],
            "search_results": [],
            "iteration_count": 0,
            "reflection_sufficient": False,
            "final_report": "",
            "events": [],
        }

        try:
            async for chunk in research_graph.astream(initial_state, stream_mode="updates"):
                if await request.is_disconnected():
                    logger.info("Client disconnected during stream")
                    return

                for _node_name, state_update in chunk.items():
                    for event in state_update.get("events", []):
                        yield f"data: {json.dumps(event)}\n\n"

        except Exception as exc:
            logger.error("Agent error: %s", exc, exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'content': str(exc)})}\n\n"

        finally:
            yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
