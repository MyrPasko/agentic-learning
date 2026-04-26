from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from agentic_learning.tools.add_numbers import add_numbers
from agentic_learning.tools.multiply_numbers import multiply_numbers

load_dotenv()

MODEL_NAME = "claude-haiku-4-5-20251001"

model = init_chat_model(
    MODEL_NAME,
    temperature=0,
)

system_prompt = """You are an expert at performing arithmetic operations.

You have access to the following tools:
- add_numbers: Add two numbers.
- multiply_numbers: Multiply two numbers.

Routing rules:
- If the user asks to add two numbers, use the add_numbers tool.
- If the user asks to multiply two numbers, use the multiply_numbers tool.
- Do not answer from mental math when a matching tool exists.
- If the request is not supported by the available tools, say that it is unsupported instead of guessing."""

arithmetic_agent = create_agent(
    model,
    tools=[add_numbers, multiply_numbers],
    system_prompt=system_prompt,
)
