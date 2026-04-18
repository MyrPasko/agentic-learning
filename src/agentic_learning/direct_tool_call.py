from agentic_learning.tools.multiply_numbers import multiply_numbers

print("Running direct multiply_numbers tool call.")
result = multiply_numbers.invoke({"a": 137.42, "b": 58.09})

print(f"Tool name: {multiply_numbers.name}")
print(f"Tool args: {multiply_numbers.args}")
print(f"Result: {result}")
