from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

load_dotenv()

MODEL_NAME = "claude-haiku-4-5-20251001"

model = init_chat_model(
    MODEL_NAME,
    temperature=0,
)

system_prompt = """You are an expert at task decomposition."""

task_decomposer_agent = create_agent(model, system_prompt=system_prompt)
