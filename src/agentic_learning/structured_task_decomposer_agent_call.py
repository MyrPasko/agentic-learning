from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from agentic_learning.schemas.task_decomposer_result import TaskDecomposerResult

load_dotenv()

MODEL_NAME = "claude-haiku-4-5-20251001"

model = init_chat_model(
    MODEL_NAME,
    temperature=0,
)

system_prompt = """You are an expert at task decomposition.

Return the final result as structured output matching the required schema."""

task_decomposer_structured_agent = create_agent(
    model, system_prompt=system_prompt, response_format=TaskDecomposerResult
)

prompt = "Add /api/portfolio endpoint with validation, error handling, and tests."

response = task_decomposer_structured_agent.invoke(
    {"messages": [{"role": "user", "content": prompt}]}
)

structured_response = response["structured_response"]

print(f"Prompt: {prompt}")
print(structured_response.model_dump_json(indent=2))
