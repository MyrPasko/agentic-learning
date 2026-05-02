from typing import Any

from agentic_learning.helpers.ToolCall import ToolCall

AgentResult = dict[str, Any] | Any


def ok_output(prompt: str, result: AgentResult) -> ToolCall:
    messages = result["messages"]

    tool_call_message = next(
        (message for message in messages if getattr(message, "tool_calls", None)), None
    )

    tool_calls = getattr(tool_call_message, "tool_calls", [])

    tool_name = None

    if tool_calls:
        tools_call_message = next(
            message for message in messages if getattr(message, "tool_calls", None)
        )
        first_tool_call = tools_call_message.tool_calls[0]
        tool_name = (
            first_tool_call["name"]
            if isinstance(first_tool_call, dict)
            else getattr(first_tool_call, "name", None)
        )

    final_message = getattr(messages[-1], "content", "")

    return ToolCall(prompt, "ok", tool_name, final_message, None)
