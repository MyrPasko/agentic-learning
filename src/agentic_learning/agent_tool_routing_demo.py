from agentic_learning.agents.arithmetic_agent import arithmetic_agent


def run_prompt(prompt: str) -> None:
    result = arithmetic_agent.invoke({"messages": [{"role": "user", "content": prompt}]})
    messages = result["messages"]

    tools_call_message = next((message for message in messages if getattr(message, "tool_calls", None)), None)

    if not tools_call_message:
        final_message = messages[-1]
        print(f"Prompt: {prompt}")
        print("Tool used: none")
        print(f"Final answer: {final_message.content}")
        print("-" * 60)
        return

    tool_call = tools_call_message.tool_calls[0]

    tool_result_message = next(message
                               for message in messages if
                               getattr(message, "type", None) == "tool"
                               and message.tool_call_id == tool_call["id"])

    final_message = messages[-1]

    print(f"Prompt: {prompt}")
    print(f"Tool used: {tool_call['name']}")
    print(f"Tool args: {tool_call['args']}")
    print(f"Tool result: {tool_result_message.content}")
    print(f"Final answer: {final_message.content}")
    print("-" * 60)


def main() -> None:
    run_prompt("Please use the tool to add 12.5 and 7.25.")
    run_prompt("Please use the tool to multiply 12.5 by 7.25.")
    run_prompt("Please use the tool to divide 12.5 by 7.25.")


if __name__ == "__main__":
    main()
