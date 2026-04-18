from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from agentic_learning.tools.multiply_numbers import multiply_numbers

load_dotenv()

MODEL_NAME = "claude-haiku-4-5-20251001"

model = init_chat_model(
    MODEL_NAME,
    temperature=0,
)

system_prompt = """You are an expert at performing arithmetic operations.

You have access to the following tools:
- multiply_numbers: Multiply two numbers.

If user asks to multiply two numbers, use the multiply_numbers tool."""

arithmetic_agent = create_agent(
    model,
    tools=[multiply_numbers],
    system_prompt=system_prompt,
)
