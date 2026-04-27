from agentic_learning.helpers.ToolCall import ToolCall
from agentic_learning.helpers.fallback_output import fallback_output
from agentic_learning.helpers.ok_output import ok_output


def get_tool_call(prompt: str) -> ToolCall:
    try:
        return ok_output(prompt)
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


def main() -> None:
    run_prompt("Please use the tool to add 12.5 and 7.25.")
    run_prompt("Please use the tool to multiply 12.5 by 7.25.")
    run_prompt("Please use the tool to divide 12.5 by 7.25.")


if __name__ == "__main__":
    main()
