from agentic_learning.agents.arithmetic_agent import arithmetic_agent

prompt = (
    "Please use the multiply_numbers tool to multiply 137.42 and 58.09. "
    "Return the tool result."
)

response = arithmetic_agent.invoke(
    {"messages": [{"role": "user", "content": prompt}]}
)
messages = response["messages"]

tool_call_message = next(
    message for message in messages if getattr(message, "tool_calls", None)
)
tool_call = tool_call_message.tool_calls[0]
tool_result_message = next(
    message
    for message in messages
    if getattr(message, "type", None) == "tool"
    and message.tool_call_id == tool_call["id"]
)
final_message = messages[-1]

print(f"Prompt: {prompt}")
print(f"Tool used: {tool_call['name']}")
print(f"Tool args: {tool_call['args']}")
print(f"Tool result: {tool_result_message.content}")
print(f"Final answer: {final_message.content}")
