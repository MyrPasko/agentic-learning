# Project 1 Prompt Contracts And Failure Modes

This note closes `Project 1` with one narrow purpose: make the current prompt, tool, and failure boundaries explicit enough that another engineer can review the slice without guessing where behavior comes from.

## Contract Layers

The task decomposer now has three distinct contract layers.

### 1. Draft Contract

Owner:

- `structured_task_decomposer_agent_call.py`
- `TaskDecomposerDraft`

Responsibility:

- turn the input task into a compact implementation draft;
- return `original_task`, `plan_summary`, `implementation_tasks`, `test_ideas`, and provisional `unknowns`;
- avoid producing `risks`, because risk analysis is intentionally moved into a separate workflow step.

Practical rule:

- the draft prompt is allowed to propose structure, but it is not allowed to silently own downstream risk or approval policy.

Why this matters:

- once the draft owns too much, the workflow stops being inspectable;
- separating the draft from risk/policy logic is the main reason the graph is worth having at all.

### 2. Tool Contracts

Owners:

- `analyze_task_unknowns`
- `analyze_task_risks`

Responsibility:

- `analyze_task_unknowns` returns narrow machine-readable unknown candidates for recognized technical signals;
- `analyze_task_risks` returns machine-readable risk candidates with `risk`, `impact`, and `mitigation`.

Practical rule:

- tools own narrow signals, not broad prose summaries;
- both tools are intentionally constrained so the workflow can route on explicit fields instead of reading vibes from a paragraph.

Why this matters:

- `unknowns` directly affect whether output must go to guarded review;
- `risks` directly affect the approval decision when any risk is `high`.

### 3. Policy Contract

Owner:

- `run_approval_decision`

Responsibility:

- `review_required` when unknowns exist;
- `review_required` when any risk is `high`;
- `approved` otherwise.

Practical rule:

- approval is a policy boundary, not a prompt style choice.

Why this matters:

- this keeps the review gate deterministic enough to test;
- it also keeps the workflow honest about incomplete information.

## Current Failure Modes

The current slice has three meaningful failure classes.

### 1. Draft-stage failure

Examples:

- missing prompt;
- model invocation exception;
- malformed structured draft.

Current behavior:

- bounded retry;
- fallback if the retry budget is exhausted;
- `draft` step outcome marked as failed.

### 2. Tool-stage failure

Examples:

- forced `analyze_task_risks` failure;
- malformed tool JSON;
- schema-invalid tool payload.

Current behavior:

- bounded retry around the failing tool stage;
- fallback if the retry budget is exhausted;
- explicit failed step outcome for the affected node.

### 3. Guarded review outcome

Examples:

- unknowns detected;
- at least one high-risk item detected.

Current behavior:

- this is not treated as runtime failure;
- the workflow stays `ok`, but the output is routed through `review_output`;
- `review_required` is intentional control behavior, not regression by itself.

## Current Prompt And Failure Boundaries

What the prompt is allowed to do:

- propose a compact plan;
- propose implementation tasks;
- propose test ideas;
- provide raw draft structure.

What the prompt is not allowed to do:

- decide final approval status;
- replace risk-tool output;
- blur runtime failure with guarded review.

What the workflow is allowed to do:

- retry failed stages;
- degrade into fallback;
- separate approved output from review-required output.

What the workflow still does not prove:

- live prompt robustness across a wider input distribution;
- real unknown/risk heuristic quality inside the deterministic eval harness;
- trace quality, latency, and cost behavior as portfolio evidence.

## Reviewer's Shortcut

If you need the minimum useful artifact set for this project, read them in this order:

1. `README.md`
2. `docs/Project1_Task_Decomposer_Workflow.md`
3. `docs/Project1_Prompt_Contracts_And_Failure_Modes.md`
4. `artifacts/evals/task_decomposer_eval_summary_v1.json`
5. `artifacts/evals/task_decomposer_failure_log_v1.md`

That is enough to understand:

- what the workflow does;
- why the graph exists;
- how approval decisions happen;
- what currently counts as expected guarded review versus actual failure.
