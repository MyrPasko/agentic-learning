from pathlib import Path

from agentic_learning.schemas.pr_review_intake_result import PrReviewIntakeResult
from agentic_learning.structured_pr_review_intake_agent import (
    get_pr_review_intake_agent,
)

INPUT_FILE_PATH = (
    Path(__file__).resolve().parents[2]
    / "src/examples/input_pr_review_backend_endpoint.md"
)


def run_structured_pr_review_intake_agent() -> PrReviewIntakeResult:
    pr_review_input = INPUT_FILE_PATH.read_text(encoding="utf-8").strip()

    result = get_pr_review_intake_agent().invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Classify the following PR review input and return only the "
                        "structured review-intake result:\n\n"
                        f"{pr_review_input}"
                    ),
                }
            ]
        }
    )

    structured_response = result["structured_response"]

    return PrReviewIntakeResult.model_validate(structured_response)


def main() -> None:
    result = run_structured_pr_review_intake_agent()
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
