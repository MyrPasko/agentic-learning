from agentic_learning.pr_review_consolidation_policy import (
    validate_consolidation_policy,
)
from agentic_learning.schemas.pr_review_architecture_result import (
    PrReviewArchitectureResult,
)
from agentic_learning.schemas.pr_review_consolidation_result import (
    PrConsolidationResult,
)
from agentic_learning.schemas.pr_review_intake_result import PrReviewIntakeResult
from agentic_learning.schemas.pr_review_risk_result import PrReviewRiskResult
from agentic_learning.schemas.pr_review_testing_result import PrReviewTestingResult
from agentic_learning.structured_pr_architecture_review_agent_call import (
    run_structured_pr_architecture_review_agent,
)
from agentic_learning.structured_pr_consolidation_review_agent import (
    get_pr_consolidation_review_agent,
)
from agentic_learning.structured_pr_review_intake_agent_call import (
    run_structured_pr_review_intake_agent,
)
from agentic_learning.structured_pr_risk_review_agent_call import (
    run_structured_pr_risk_review_agent,
)
from agentic_learning.structured_pr_testing_review_agent_call import (
    run_structured_pr_testing_review_agent,
)


def build_consolidation_review_prompt(
    intake_result: PrReviewIntakeResult,
    architecture_result: PrReviewArchitectureResult,
    testing_result: PrReviewTestingResult,
    risk_result: PrReviewRiskResult,
) -> str:
    return (
        "Consolidate the following typed review artifacts and return only the "
        "structured consolidation-review result.\n\n"
        "PR intake result (context only):\n"
        f"{intake_result.model_dump_json(indent=2)}\n\n"
        "Architecture review result (authoritative):\n"
        f"{architecture_result.model_dump_json(indent=2)}\n\n"
        "Testing review result (authoritative):\n"
        f"{testing_result.model_dump_json(indent=2)}\n\n"
        "Risk review result (authoritative):\n"
        f"{risk_result.model_dump_json(indent=2)}"
    )


def run_structured_pr_consolidation_review_agent() -> PrConsolidationResult:
    intake_result = run_structured_pr_review_intake_agent()
    intake_result_json = intake_result.model_dump_json(indent=2)

    architecture_result = run_structured_pr_architecture_review_agent(
        intake_result_json
    )
    testing_result = run_structured_pr_testing_review_agent(intake_result_json)
    risk_result = run_structured_pr_risk_review_agent(intake_result_json)

    result = get_pr_consolidation_review_agent().invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": build_consolidation_review_prompt(
                        intake_result,
                        architecture_result,
                        testing_result,
                        risk_result,
                    ),
                }
            ]
        }
    )

    structured_response = result["structured_response"]
    consolidation_result = PrConsolidationResult.model_validate(structured_response)

    validate_consolidation_policy(
        consolidation_result,
        architecture_result,
        testing_result,
        risk_result,
    )

    return consolidation_result


def main() -> None:
    result = run_structured_pr_consolidation_review_agent()
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
