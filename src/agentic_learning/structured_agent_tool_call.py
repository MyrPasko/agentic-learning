from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from agentic_learning.schemas.arithmetic_result import ArithmeticResult
from agentic_learning.tools.multiply_numbers import multiply_numbers

load_dotenv()

MODEL_NAME = "claude-haiku-4-5-20251001"

model = init_chat_model(
    MODEL_NAME,
    temperature=0,
)

system_prompt = """You are an expert at performing arithmetic operations.

You must use the multiply_numbers tool when the user asks to multiply numbers.

Return the final result as structured output matching the required schema.
"""

structured_agent = create_agent(
    model,
    tools=[multiply_numbers],
    system_prompt=system_prompt,
    response_format=ArithmeticResult,
)

prompt = (
    "Please use the multiply_numbers tool to multiply 137.42 and 58.09. "
    "Return the result as structured output."
)

response = structured_agent.invoke(
    {"messages": [{"role": "user", "content": prompt}]}
)

structured_response = response["structured_response"]

print(f"Prompt: {prompt}")
print(structured_response.model_dump_json(indent=2))
