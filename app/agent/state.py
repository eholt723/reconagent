import operator
from typing import Annotated, List, TypedDict


class AgentState(TypedDict):
    topic: str
    planned_queries: List[str]
    search_results: List[dict]
    iteration_count: int
    reflection_sufficient: bool
    final_report: str
    events: Annotated[List[dict], operator.add]
