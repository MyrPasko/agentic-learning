from dataclasses import dataclass
from typing import Literal


@dataclass
class ToolCall:
    prompt: str
    status: Literal["ok", "fallback"]
    tool_name: str | None
    answer: str
    failure_reason: str | None
