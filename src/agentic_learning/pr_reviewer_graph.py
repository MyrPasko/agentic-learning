from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from agentic_learning.pr_review_human_approval_policy import (
    ApprovalStatus,
    build_human_review_summary,
    need_human_approval,
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
from agentic_learning.structured_pr_consolidation_review_agent_call import (
    run_structured_pr_consolidation_review_from_artifacts,
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

StepOutcome = Literal["ok", "skipped"]
RouteAfterApprovalDecision = Literal["done", "review"]


class StepOutcomes(TypedDict):
    intake: StepOutcome
    architecture_review: StepOutcome
    testing_review: StepOutcome
    risk_review: StepOutcome
    consolidation_review: StepOutcome
    approval_decision: StepOutcome
    review: StepOutcome


class PrReviewerGraphState(TypedDict, total=False):
    intake_result: PrReviewIntakeResult | None
    architecture_result: PrReviewArchitectureResult | None
    testing_result: PrReviewTestingResult | None
    risk_result: PrReviewRiskResult | None
    consolidation_result: PrConsolidationResult | None
    approval_status: ApprovalStatus | None
    review_reason: str | None
    review_summary: str | None
    step_outcomes: StepOutcomes


def run_intake_review(_: PrReviewerGraphState) -> PrReviewerGraphState:
    intake_result = run_structured_pr_review_intake_agent()
    return {
        "intake_result": intake_result,
        "approval_status": None,
        "review_reason": None,
        "review_summary": None,
        "step_outcomes": {
            "intake": "ok",
            "architecture_review": "skipped",
            "testing_review": "skipped",
            "risk_review": "skipped",
            "consolidation_review": "skipped",
            "approval_decision": "skipped",
            "review": "skipped",
        },
    }


def run_architecture_review(state: PrReviewerGraphState) -> PrReviewerGraphState:
    intake_result = state["intake_result"]
    if intake_result is None:
        raise ValueError("Intake result is missing.")

    architecture_result = run_structured_pr_architecture_review_agent(
        intake_result.model_dump_json(indent=2)
    )
    return {
        "architecture_result": architecture_result,
        "step_outcomes": {
            **state["step_outcomes"],
            "architecture_review": "ok",
        },
    }


def run_testing_review(state: PrReviewerGraphState) -> PrReviewerGraphState:
    intake_result = state["intake_result"]
    if intake_result is None:
        raise ValueError("Intake result is missing.")

    testing_result = run_structured_pr_testing_review_agent(
        intake_result.model_dump_json(indent=2)
    )
    return {
        "testing_result": testing_result,
        "step_outcomes": {
            **state["step_outcomes"],
            "testing_review": "ok",
        },
    }


def run_risk_review(state: PrReviewerGraphState) -> PrReviewerGraphState:
    intake_result = state["intake_result"]
    if intake_result is None:
        raise ValueError("Intake result is missing.")

    risk_result = run_structured_pr_risk_review_agent(
        intake_result.model_dump_json(indent=2)
    )
    return {
        "risk_result": risk_result,
        "step_outcomes": {
            **state["step_outcomes"],
            "risk_review": "ok",
        },
    }


def run_consolidation_review(state: PrReviewerGraphState) -> PrReviewerGraphState:
    intake_result = state["intake_result"]
    architecture_result = state["architecture_result"]
    testing_result = state["testing_result"]
    risk_result = state["risk_result"]

    if (
        intake_result is None
        or architecture_result is None
        or testing_result is None
        or risk_result is None
    ):
        raise ValueError("Reviewer artifacts are missing.")

    consolidation_result = run_structured_pr_consolidation_review_from_artifacts(
        intake_result,
        architecture_result,
        testing_result,
        risk_result,
    )
    return {
        "consolidation_result": consolidation_result,
        "step_outcomes": {
            **state["step_outcomes"],
            "consolidation_review": "ok",
        },
    }


def run_human_approval_gate(state: PrReviewerGraphState) -> PrReviewerGraphState:
    intake_result = state["intake_result"]
    consolidation_result = state["consolidation_result"]

    if intake_result is None or consolidation_result is None:
        raise ValueError("Approval gate inputs are missing.")

    approval_status, review_reason = need_human_approval(
        intake_result,
        consolidation_result,
    )
    return {
        "approval_status": approval_status,
        "review_reason": review_reason,
        "step_outcomes": {
            **state["step_outcomes"],
            "approval_decision": "ok",
            "review": "skipped",
        },
    }


def review_output(state: PrReviewerGraphState) -> PrReviewerGraphState:
    intake_result = state["intake_result"]
    consolidation_result = state["consolidation_result"]
    review_reason = state["review_reason"]

    if intake_result is None or consolidation_result is None or review_reason is None:
        raise ValueError("Review summary inputs are missing.")

    return {
        "review_summary": build_human_review_summary(
            intake_result,
            consolidation_result,
            review_reason,
        ),
        "step_outcomes": {
            **state["step_outcomes"],
            "review": "ok",
        },
    }


def route_after_approval_decision(
    state: PrReviewerGraphState,
) -> RouteAfterApprovalDecision:
    approval_status = state.get("approval_status")

    if approval_status == "approved":
        return "done"
    if approval_status == "review_required":
        return "review"

    raise ValueError("Approval status is missing.")


graph_builder = StateGraph(PrReviewerGraphState)
graph_builder.add_node("run_intake_review", run_intake_review)
graph_builder.add_node("run_architecture_review", run_architecture_review)
graph_builder.add_node("run_testing_review", run_testing_review)
graph_builder.add_node("run_risk_review", run_risk_review)
graph_builder.add_node("run_consolidation_review", run_consolidation_review)
graph_builder.add_node("run_human_approval_gate", run_human_approval_gate)
graph_builder.add_node("review_output", review_output)

graph_builder.add_edge(START, "run_intake_review")
graph_builder.add_edge("run_intake_review", "run_architecture_review")
graph_builder.add_edge("run_architecture_review", "run_testing_review")
graph_builder.add_edge("run_testing_review", "run_risk_review")
graph_builder.add_edge("run_risk_review", "run_consolidation_review")
graph_builder.add_edge("run_consolidation_review", "run_human_approval_gate")
graph_builder.add_conditional_edges(
    "run_human_approval_gate",
    route_after_approval_decision,
    {
        "done": END,
        "review": "review_output",
    },
)
graph_builder.add_edge("review_output", END)

pr_reviewer_graph = graph_builder.compile()


def main() -> None:
    result = pr_reviewer_graph.invoke({})
    step_outcomes = result.get("step_outcomes", {})
    print(f"Intake step: {step_outcomes.get('intake')}")
    print(f"Architecture review step: {step_outcomes.get('architecture_review')}")
    print(f"Testing review step: {step_outcomes.get('testing_review')}")
    print(f"Risk review step: {step_outcomes.get('risk_review')}")
    print(f"Consolidation review step: {step_outcomes.get('consolidation_review')}")
    print(f"Approval decision step: {step_outcomes.get('approval_decision')}")
    print(f"Approval status: {result.get('approval_status')}")
    if result.get("review_summary") is not None:
        print(f"Review summary: {result['review_summary']}")

    consolidation_result = result.get("consolidation_result")
    if consolidation_result is not None:
        print(consolidation_result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
