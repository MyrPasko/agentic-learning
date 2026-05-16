from pathlib import Path
from typing import Any, TypedDict, Literal

from langgraph.graph import END, START, StateGraph

from agentic_learning.schemas.task_decomposer_result import TaskDecomposerResult
from agentic_learning.structured_task_decomposer_agent_call import (
    task_decomposer_structured_agent,
)

INPUT_FILE_PATH = (
    Path(__file__).resolve().parent.parent / "examples" / "input_backend_endpoint.md"
)

MAX_RETRY_COUNT = 1


class TaskDecomposerState(TypedDict, total=False):
    prompt: str | None
    structured_response: TaskDecomposerResult | None
    tool_name: str | None
    failure_reason: str | None
    retry_count: int
    used_fallback: bool


def read_input(_: TaskDecomposerState) -> TaskDecomposerState:
    prompt = INPUT_FILE_PATH.read_text(encoding="utf-8").strip()
    return {
        "prompt": prompt,
        "structured_response": None,
        "tool_name": None,
        "failure_reason": None,
        "retry_count": 0,
        "used_fallback": False,
    }


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

def route_after_decomposer(state: TaskDecomposerState) -> Literal["done", "retry", "fallback"]:
    failure_reason = state.get("failure_reason")
    retry_count = state.get("retry_count", 0)

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

graph_builder = StateGraph(TaskDecomposerState)
graph_builder.add_node("read_input", read_input)
graph_builder.add_node("run_decomposer", run_decomposer)
graph_builder.add_node("build_fallback", build_fallback)

graph_builder.add_edge(START, "read_input")
graph_builder.add_edge("read_input", "run_decomposer")
graph_builder.add_conditional_edges("run_decomposer", route_after_decomposer,
                                    {
                                        "done": END,
                                        "retry": "run_decomposer",
                                        "fallback": "build_fallback"
                                    })
graph_builder.add_edge("build_fallback", END)

task_decomposer_graph = graph_builder.compile()
