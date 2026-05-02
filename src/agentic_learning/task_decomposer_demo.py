from pathlib import Path

from agentic_learning.helpers.fallback_output import fallback_output
from agentic_learning.helpers.ok_output import ok_output
from agentic_learning.helpers.ToolCall import ToolCall
from agentic_learning.structured_task_decomposer_agent_call import (
    task_decomposer_structured_agent,
)

INPUT_FILE_PATH = (
    Path(__file__).resolve().parent.parent / "examples" / "input_backend_endpoint.md"
)


def get_tool_call(prompt: str) -> ToolCall:
    try:
        result = task_decomposer_structured_agent.invoke(
            {"messages": [{"role": "user", "content": prompt}]}
        )
        return ok_output(prompt, result)
    except Exception as e:
        return fallback_output(prompt, e)


def run_prompt(prompt: str) -> None:
    tool_call = get_tool_call(prompt)
    print(f"Prompt: {tool_call.prompt}")
    print(f"Status: {tool_call.status}")
    print(f"Tool: {tool_call.tool_name}")
    print(f"Answer: {tool_call.answer}")
    print(f"Failure reason: {tool_call.failure_reason}")
    print("---")


def read_task_prompt() -> str:
    return INPUT_FILE_PATH.read_text(encoding="utf-8").strip()


def main() -> None:
    run_prompt(read_task_prompt())


if __name__ == "__main__":
    main()
