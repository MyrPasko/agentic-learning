from agentic_learning.helpers.ToolCall import ToolCall


def fallback_output(prompt: str, error: Exception) -> ToolCall:
    return ToolCall(prompt, "fallback", None, "The response is unavailable", str(error))
