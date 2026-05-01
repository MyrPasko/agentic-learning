from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from agentic_learning.schemas.task_decomposer_result import TaskDecomposerResult

load_dotenv()

INPUT_FILE_PATH = (
    Path(__file__).resolve().parent.parent / "examples" / "input_backend_endpoint.md"
)

MODEL_NAME = "claude-haiku-4-5-20251001"

model = init_chat_model(
    MODEL_NAME,
    temperature=0,
)

system_prompt = """You are an expert at decomposing short engineering tasks into a compact implementation plan.

Return the final result as structured output matching the required schema.

Follow these rules:
- Keep the decomposition concise and practical.
- Return only the most relevant items.
- Do not invent code snippets, file paths, or implementation details that are not justified by the task.
- `implementation_tasks` must be a list of objects with: `title`, `description`, and `done_criteria`.
- `risks` must be a list of objects with: `risk`, `impact`, and `mitigation`.
- `test_ideas` must be a list of objects with: `test_type`, `scenario`, and `expected_behavior`.
- `unknowns` must be a list of objects with: `question` and `why_it_matters`.
- Use only these impact values: `high`, `medium`, `low`.
- Use only these test types: `unit`, `component`, `integration`, `e2e`.
- Keep `unknowns` as an empty list when the task is sufficiently clear.
- Prefer a small number of strong items over many weak or repetitive ones."""

task_decomposer_structured_agent = create_agent(
    model, system_prompt=system_prompt, response_format=TaskDecomposerResult
)


def read_task_prompt() -> str:
    return INPUT_FILE_PATH.read_text(encoding="utf-8").strip()


def main() -> None:
    prompt = read_task_prompt()
    response = task_decomposer_structured_agent.invoke(
        {"messages": [{"role": "user", "content": prompt}]}
    )
    structured_response = response["structured_response"]

    print(f"Prompt: {prompt}")
    print(structured_response.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
