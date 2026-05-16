from pathlib import Path
from typing import Any, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from agentic_learning.schemas.task_decomposer_result import TaskDecomposerResult
from agentic_learning.structured_task_decomposer_agent_call import (
    task_decomposer_structured_agent,
)

INPUT_FILE_PATH = (
    Path(__file__).resolve().parent.parent / "examples" / "input_backend_endpoint.md"
)

MAX_RETRY_COUNT = 1

ApprovalStatus = Literal["approved", "review_required"] | None
ReviewReason = str | None
RouteAfterDecomposer = Literal["done", "retry", "fallback", "review"]


class TaskDecomposerState(TypedDict, total=False):
    prompt: str | None
    structured_response: TaskDecomposerResult | None
    tool_name: str | None
    failure_reason: str | None
    retry_count: int
    used_fallback: bool
    approval_status: ApprovalStatus
    review_reason: ReviewReason


def read_input(_: TaskDecomposerState) -> TaskDecomposerState:
    prompt = INPUT_FILE_PATH.read_text(encoding="utf-8").strip()
    return {
        "prompt": prompt,
        "structured_response": None,
        "tool_name": None,
        "failure_reason": None,
        "retry_count": 0,
        "used_fallback": False,
        "approval_status": None,
        "review_reason": None,
    }


def need_for_approval(
    structured_response: TaskDecomposerResult,
) -> tuple[ApprovalStatus, ReviewReason]:
    unknown_items = getattr(structured_response, "unknowns", [])
    risk_items = getattr(structured_response, "risks", [])
    is_at_least_one_unknown_item = len(unknown_items) > 0
    is_at_least_one_risk_high = any(risk.impact == "high" for risk in risk_items)

    if is_at_least_one_unknown_item:
        return "review_required", "Unknown items detected."

    if is_at_least_one_risk_high:
        return "review_required", "At least one risk item is high."

    return "approved", None


def run_decomposer(state: TaskDecomposerState) -> TaskDecomposerState:
    prompt = state.get("prompt")
    retry_count = state.get("retry_count", 0)

    if not prompt:
        return {
            "prompt": prompt,
            "structured_response": None,
            "tool_name": None,
            "failure_reason": "Prompt is missing.",
            "retry_count": retry_count + 1,
            "used_fallback": False,
        }

    try:
        result = task_decomposer_structured_agent.invoke(
            {"messages": [{"role": "user", "content": prompt}]}
        )

        messages = result["messages"]
        structured_response = result["structured_response"]
        approval_status, review_reason = need_for_approval(structured_response)

        tool_call_message: Any = next(
            (message for message in messages if getattr(message, "tool_calls", None)),
            None,
        )

        tool_name = None
        if tool_call_message:
            first_tool_call = tool_call_message.tool_calls[0]
            tool_name = (
                first_tool_call["name"]
                if isinstance(first_tool_call, dict)
                else getattr(first_tool_call, "name", None)
            )

        return {
            "prompt": prompt,
            "structured_response": structured_response,
            "tool_name": tool_name,
            "failure_reason": None,
            "approval_status": approval_status,
            "review_reason": review_reason,
        }
    except Exception as e:
        return {
            "prompt": prompt,
            "structured_response": None,
            "tool_name": None,
            "failure_reason": str(e),
            "retry_count": retry_count + 1,
            "used_fallback": False,
        }


def route_after_decomposer(
    state: TaskDecomposerState,
) -> RouteAfterDecomposer:
    failure_reason = state.get("failure_reason")
    retry_count = state.get("retry_count", 0)
    approval_status = state.get("approval_status")

    if approval_status == "review_required" and not failure_reason:
        return "review"

    if not failure_reason:
        return "done"

    if retry_count <= MAX_RETRY_COUNT:
        return "retry"

    return "fallback"


def build_fallback(state: TaskDecomposerState) -> TaskDecomposerState:
    return {
        "prompt": state.get("prompt"),
        "structured_response": None,
        "tool_name": state.get("tool_name"),
        "failure_reason": state.get("failure_reason"),
        "retry_count": state.get("retry_count", 0),
        "used_fallback": True,
    }


def review_output(state: TaskDecomposerState) -> TaskDecomposerState:
    return state


graph_builder = StateGraph(TaskDecomposerState)
graph_builder.add_node("read_input", read_input)
graph_builder.add_node("run_decomposer", run_decomposer)
graph_builder.add_node("build_fallback", build_fallback)
graph_builder.add_node("review_output", review_output)

graph_builder.add_edge(START, "read_input")
graph_builder.add_edge("read_input", "run_decomposer")
graph_builder.add_conditional_edges(
    "run_decomposer",
    route_after_decomposer,
    {
        "done": END,
        "retry": "run_decomposer",
        "fallback": "build_fallback",
        "review": "review_output",
    },
)
graph_builder.add_edge("build_fallback", END)
graph_builder.add_edge("review_output", END)

task_decomposer_graph = graph_builder.compile()
