from langgraph.graph import END, START, StateGraph

from agentic_learning.task_decomposer_workflow import (
    TaskDecomposerState,
    build_fallback,
    read_input,
    review_output,
    route_after_draft,
    route_after_risk_analysis,
    run_decomposer_draft,
    run_risk_analysis,
)

graph_builder = StateGraph(TaskDecomposerState)
graph_builder.add_node("read_input", read_input)
graph_builder.add_node("run_decomposer_draft", run_decomposer_draft)
graph_builder.add_node("run_risk_analysis", run_risk_analysis)
graph_builder.add_node("build_fallback", build_fallback)
graph_builder.add_node("review_output", review_output)

graph_builder.add_edge(START, "read_input")
graph_builder.add_edge("read_input", "run_decomposer_draft")
graph_builder.add_conditional_edges(
    "run_decomposer_draft",
    route_after_draft,
    {
        "run_risk_analysis": "run_risk_analysis",
        "retry": "run_decomposer_draft",
        "fallback": "build_fallback",
    },
)
graph_builder.add_conditional_edges(
    "run_risk_analysis",
    route_after_risk_analysis,
    {
        "done": END,
        "retry": "run_risk_analysis",
        "fallback": "build_fallback",
        "review": "review_output",
    },
)
graph_builder.add_edge("build_fallback", END)
graph_builder.add_edge("review_output", END)

task_decomposer_graph = graph_builder.compile()
