from langgraph.graph import END, START, StateGraph

from app.agent.nodes import planner_node, reflection_node, search_node, synthesis_node
from app.agent.state import AgentState


def _should_continue(state: AgentState) -> str:
    if state.get("reflection_sufficient", False):
        return "synthesize"
    if state.get("iteration_count", 0) >= 2:
        return "synthesize"
    return "search"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("search", search_node)
    graph.add_node("reflection", reflection_node)
    graph.add_node("synthesis", synthesis_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "search")
    graph.add_edge("search", "reflection")
    graph.add_conditional_edges(
        "reflection",
        _should_continue,
        {"search": "search", "synthesize": "synthesis"},
    )
    graph.add_edge("synthesis", END)

    return graph.compile()


research_graph = build_graph()
