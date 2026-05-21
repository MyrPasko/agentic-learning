import json

from agentic_learning.schemas.task_decomposer_result import (
    RiskItem,
    TaskDecomposerResult,
)
from agentic_learning.structured_task_decomposer_agent_call import (
    get_task_decomposer_draft_agent,
)
from agentic_learning.task_decomposer_workflow.helpers.build_task_decomposer_graph_state import (
    build_task_decomposer_graph_state,
)
from agentic_learning.task_decomposer_workflow.policy import (
    build_review_summary,
    need_for_approval,
)
from agentic_learning.task_decomposer_workflow.state import (
    INPUT_FILE_PATH,
    TaskDecomposerState,
)
from agentic_learning.tools.analyze_task_risks import analyze_task_risks


def read_input(_: TaskDecomposerState) -> TaskDecomposerState:
    prompt = INPUT_FILE_PATH.read_text(encoding="utf-8").strip()
    return build_task_decomposer_graph_state(prompt=prompt)


def run_decomposer_draft(state: TaskDecomposerState) -> TaskDecomposerState:
    prompt = state.get("prompt")
    retry_count = state.get("retry_count", 0)

    if not prompt:
        return build_task_decomposer_graph_state(
            state,
            draft_response=None,
            structured_response=None,
            tool_name=None,
            failure_reason="Prompt is missing.",
            retry_count=retry_count + 1,
            used_fallback=False,
            approval_status=None,
            review_reason=None,
            review_summary=None,
            step_outcomes={
                **state.get("step_outcomes", {}),
                "draft": "failed",
            },
        )

    try:
        result = get_task_decomposer_draft_agent().invoke(
            {"messages": [{"role": "user", "content": prompt}]}
        )
        draft_response = result["structured_response"]

        return build_task_decomposer_graph_state(
            state,
            prompt=prompt,
            draft_response=draft_response,
            structured_response=None,
            tool_name=None,
            failure_reason=None,
            approval_status=None,
            review_reason=None,
            review_summary=None,
            used_fallback=False,
            step_outcomes={
                **state.get("step_outcomes", {}),
                "draft": "ok",
                "risk_analysis": "skipped",
                "approval_decision": "skipped",
                "review": "skipped",
            },
        )
    except Exception as error:
        return build_task_decomposer_graph_state(
            state,
            prompt=prompt,
            draft_response=None,
            structured_response=None,
            tool_name=None,
            failure_reason=str(error),
            retry_count=retry_count + 1,
            approval_status=None,
            review_reason=None,
            review_summary=None,
            used_fallback=False,
            step_outcomes={
                **state.get("step_outcomes", {}),
                "draft": "failed",
            },
        )


def run_risk_analysis(state: TaskDecomposerState) -> TaskDecomposerState:
    prompt = state.get("prompt")
    draft_response = state.get("draft_response")
    retry_count = state.get("retry_count", 0)

    if not prompt or not draft_response:
        return build_task_decomposer_graph_state(
            state,
            prompt=prompt,
            draft_response=draft_response,
            structured_response=None,
            tool_name=None,
            failure_reason="Draft response is missing.",
            retry_count=retry_count + 1,
            approval_status=None,
            review_reason=None,
            review_summary=None,
            used_fallback=False,
            step_outcomes={
                **state.get("step_outcomes", {}),
                "risk_analysis": "failed",
            },
        )

    try:
        raw_risks = analyze_task_risks.invoke({"task": prompt})
        risk_dicts = json.loads(raw_risks)
        risks = [RiskItem.model_validate(item) for item in risk_dicts]

        structured_response = TaskDecomposerResult(
            original_task=draft_response.original_task,
            plan_summary=draft_response.plan_summary,
            implementation_tasks=draft_response.implementation_tasks,
            risks=risks,
            test_ideas=draft_response.test_ideas,
            unknowns=draft_response.unknowns,
        )

        return build_task_decomposer_graph_state(
            state,
            prompt=prompt,
            draft_response=draft_response,
            structured_response=structured_response,
            tool_name="analyze_task_risks",
            failure_reason=None,
            approval_status=None,
            review_reason=None,
            review_summary=None,
            used_fallback=False,
            step_outcomes={
                **state.get("step_outcomes", {}),
                "risk_analysis": "ok",
                "approval_decision": "skipped",
                "review": "skipped",
            },
        )
    except Exception as error:
        return build_task_decomposer_graph_state(
            state,
            prompt=prompt,
            draft_response=draft_response,
            structured_response=None,
            tool_name="analyze_task_risks",
            failure_reason=str(error),
            retry_count=retry_count + 1,
            approval_status=None,
            review_reason=None,
            review_summary=None,
            used_fallback=False,
            step_outcomes={
                **state.get("step_outcomes", {}),
                "risk_analysis": "failed",
            },
        )


def run_approval_decision(state: TaskDecomposerState) -> TaskDecomposerState:
    prompt = state.get("prompt")
    draft_response = state.get("draft_response")
    structured_response = state.get("structured_response")
    retry_count = state.get("retry_count", 0)

    if not structured_response:
        return build_task_decomposer_graph_state(
            state,
            prompt=prompt,
            draft_response=draft_response,
            structured_response=None,
            tool_name=None,
            failure_reason="Structured response is missing.",
            retry_count=retry_count + 1,
            approval_status=None,
            review_reason=None,
            review_summary=None,
            used_fallback=False,
            step_outcomes={
                **state.get("step_outcomes", {}),
                "approval_decision": "failed",
            },
        )

    try:
        approval_status, review_reason = need_for_approval(structured_response)

        return build_task_decomposer_graph_state(
            state,
            prompt=prompt,
            draft_response=draft_response,
            structured_response=structured_response,
            tool_name="analyze_task_risks",
            failure_reason=None,
            approval_status=approval_status,
            review_reason=review_reason,
            review_summary=None,
            used_fallback=False,
            step_outcomes={
                **state.get("step_outcomes", {}),
                "approval_decision": "ok",
                "review": "skipped",
            },
        )
    except Exception as error:
        return build_task_decomposer_graph_state(
            state,
            prompt=prompt,
            draft_response=draft_response,
            structured_response=None,
            tool_name="analyze_task_risks",
            failure_reason=str(error),
            retry_count=retry_count + 1,
            approval_status=None,
            review_reason=None,
            review_summary=None,
            used_fallback=False,
            step_outcomes={
                **state.get("step_outcomes", {}),
                "approval_decision": "failed",
            },
        )


def build_fallback(state: TaskDecomposerState) -> TaskDecomposerState:
    return build_task_decomposer_graph_state(
        state,
        prompt=state.get("prompt"),
        draft_response=state.get("draft_response"),
        structured_response=None,
        tool_name=state.get("tool_name"),
        failure_reason=state.get("failure_reason"),
        retry_count=state.get("retry_count", 0),
        used_fallback=True,
        approval_status=None,
        review_reason=None,
        review_summary=None,
    )


def review_output(state: TaskDecomposerState) -> TaskDecomposerState:
    structured_response = state.get("structured_response")
    if structured_response is None:
        return build_task_decomposer_graph_state(
            state,
            step_outcomes={
                **state.get("step_outcomes", {}),
                "review": "failed",
            },
        )

    return build_task_decomposer_graph_state(
        state,
        review_summary=build_review_summary(structured_response),
        step_outcomes={
            **state.get("step_outcomes", {}),
            "review": "ok",
        },
    )
