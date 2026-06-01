# Agentic Learning

Practice repository for building controlled, observable, and evaluable agentic systems with LangChain, LangGraph, and LangSmith.

This repository follows the 10-week agentic learning roadmap tracked in the Obsidian vault at:

`/Users/myroslavpasko/obsidian/main/AI/AGENTIC_LEARNING`

## What This Project Is

This is a learning repo, not a product repo. Its purpose is to build small runnable slices that prove specific agent engineering concepts one by one:

- typed tools,
- model-driven tool use,
- structured output validation,
- prompt-level routing constraints,
- tracing and observability,
- deterministic fallback behavior.

Week 1 intentionally uses a narrow arithmetic demo so the focus stays on agent mechanics rather than product scope.

Week 2 starts Project 1: `AI Task Decomposer`. The first slice is intentionally contract-first: sample task inputs, a typed decomposition schema, deterministic validation, and one minimal structured-output agent path.

## What Week 1 Proves

By the end of Week 1, this repo proves the following:

- a Python agent project can be created with repeatable local setup and documented run commands;
- the model can be constrained to use different tools for addition and multiplication;
- structured output can be validated as application data instead of trusted as prose;
- unsupported requests can be separated from runtime failures;
- runtime failures can return deterministic fallback output instead of crashing normal demo output;
- the agent workflow can be traced in LangSmith and inspected as nested runs.

## Week 1 Progression

- Day 1: project skeleton, environment setup, and first runnable command.
- Day 2: first typed tool and first live agent tool call.
- Day 3: structured output schema plus deterministic validation.
- Day 4: second tool and explicit routing rules.
- Day 5: LangSmith tracing and first trace inspection.
- Day 6: fallback output contract for runtime failures.

## Project 1 Progression

- Day 8: first `AI Task Decomposer` contract slice with sample inputs, typed output schema, deterministic validation, and one minimal structured-output run.
- Day 9: harden the decomposer contract with nested typed items, stricter validation, trimmed input normalization, duplicate checks for `done_criteria`, and a stronger structured-output prompt.
- Day 10: replace the hardcoded decomposer prompt with one explicit file-ingestion path that reads a sample task from `src/examples/input_backend_endpoint.md`.
- Day 11: add one narrow `analyze_task_risks` tool path and a demo entrypoint that makes tool use visible alongside the final structured decomposition.
- Day 12: move the Day 10-11 decomposer path into the first explicit LangGraph workflow, which later became the current `read_input -> run_decomposer_draft -> run_risk_analysis` path.
- Day 13: add one forced-failure trigger for `analyze_task_risks` plus one bounded retry and fallback branch around the graph-backed decomposer run.
- Day 15: add the first approval checkpoint so risky or incomplete outputs no longer pass straight through by default.
- Day 16: turn the review path into the first deterministic review artifact with `review_summary`.
- Day 17: split risk analysis into its own explicit graph node boundary.
- Day 18: split approval into its own explicit workflow node after risk analysis.
- Day 19: add explicit workflow `step_outcomes` so end-state reporting stops inferring state from loose fields.
- Day 20: add focused deterministic tests for routes, policy, fallback, review, and step outcomes.
- Day 21: add compiled-graph deterministic tests for review and fallback end states.
- Day 22: add the compiled-graph approved-path test so terminal-state coverage reaches approved, review, and fallback.
- Day 23: add `analyze_task_unknowns` as a separate deterministic clarity-analysis step before risk analysis so Project 1 now uses at least two meaningful domain tool paths.
- Day 24: add the first formal eval dataset contract and a checked-in 21-case corpus.
- Day 25: add the deterministic eval runner and machine-readable JSON summary artifact.
- Day 26: add the failure-log generator and the short portfolio-facing eval note.
- Day 27: add the repo-facing `Project 1 Eval Surface` explanation layer in `README.md`.
- Day 28: add the compact workflow and architecture note.
- Day 29: add the final prompt-contracts and failure-modes note, closing the last missing Project 1 documentation artifact.

## Project 1 Closeout Status

Project 1 is closed as a portfolio-ready learning slice.

Current artifact set:

- README repo overview and eval-surface summary
- sample task inputs under `src/examples/`
- deterministic schema validation
- explicit LangGraph workflow with approval/review/fallback paths
- two meaningful domain tool paths: `analyze_task_unknowns` and `analyze_task_risks`
- eval dataset, eval summary, failure log, and short eval note
- workflow architecture note
- prompt contracts and failure modes note

Remaining honesty note:

- the repo demonstrates Project 1 well enough to move on;
- the one thing not curated as a portfolio asset inside the repo surface is a dedicated Project 1 trace link or screenshot;
- that gap is visible on purpose rather than being smoothed over.

## Project 2 Start

Project 2 starts with a narrow contract-first slice for `PR Review Copilot Workflow`.

The first slice is intentionally pre-graph:

- one controlled PR-summary input artifact;
- one typed review-intake classification schema;
- one structured agent path that reads the sample input and returns validated output;
- one deterministic validator for the intake contract.

This keeps the trust boundary explicit before architecture, testing, risk, consolidate, or HITL nodes are introduced.

## Current Behavior Guarantees

The routing demo currently guarantees:

- add requests return `status: ok` and use `add_numbers`;
- multiply requests return `status: ok` and use `multiply_numbers`;
- unsupported divide requests return `status: ok` with no tool selected;
- runtime exceptions return `status: fallback` with a fallback answer and short failure reason.

The fallback output shape is:

- `prompt`
- `status`
- `tool`
- `answer`
- `failure_reason`

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Create local environment variables:

```bash
cp .env.example .env
```

Do not commit `.env` or real API keys.

## Run

Preferred daily launcher surface:

```bash
make help
```

Most useful shortcuts:

```bash
make test
make test-workflow
make validate-task
make validate-task-eval-dataset
make validate-pr-review-intake
make eval-task
make eval-task-failure-log
make demo-pr-review-intake
make demo-task
make demo-task-fallback
```

The `make` targets use `./.venv/bin/python` directly. For model-backed demos they also load variables from `.env` automatically, so you do not need to re-type `export ANTHROPIC_API_KEY=...` each time.

Day 1 sanity check:

```bash
make sanity
```

Expected output:

```text
Agentic learning environment is ready.
```

Day 2 direct tool call demo:

```bash
make demo-direct
```

Day 2 live agent tool call demo:

```bash
make demo-agent
```

Day 3 deterministic schema validation demo:

```bash
make validate-arithmetic
```

Day 3 structured output agent demo:

```bash
make demo-structured
```

Day 4 and Day 6 routing plus fallback demo:

```bash
make demo-routing
```

Day 8 and Day 9 deterministic task-decomposer contract demo:

```bash
make validate-task
```

Day 30 deterministic Project 2 intake-contract demo:

```bash
make validate-pr-review-intake
```

Day 30 structured PR-review intake demo:

```bash
make demo-pr-review-intake
```

Day 31 deterministic Project 2 architecture-review contract demo:

```bash
make validate-pr-review-architecture
```

Day 31 structured PR architecture-review demo:

```bash
make demo-pr-review-architecture
```

Week 2 canonical demo set:

- contract validation:

```bash
make validate-task
```

- workflow-control tests:

```bash
make test
```

- eval dataset validation:

```bash
make validate-task-eval-dataset
```

- deterministic eval runner plus JSON summary:

```bash
make eval-task
```

- failure log plus portfolio-facing eval note:

```bash
make eval-task-failure-log
```

- normal graph-backed decomposer run:

```bash
make demo-task
```

- forced-failure retry/fallback run:

```bash
make demo-task-fallback
```

Day 8 to Day 11 direct structured task-decomposer agent path:

```bash
make demo-structured
```

Day 10 structured-input source:

- `src/examples/input_backend_endpoint.md`

Day 11 to Day 13 graph-backed task-decomposer demo:

```bash
make demo-task
```

Forced-failure demo for Day 13:

```bash
make demo-task-fallback
```

Expected normal Day 13 demo output includes:

- `Prompt: ...`
- `Status: ok`
- `Draft step: ok`
- `Unknown analysis step: ok` or `Unknown analysis step: skipped`
- `Risk analysis step: ok`
- `Approval decision step: ok`
- `Review step: ok` or `Review step: skipped`
- `Tool: analyze_task_risks`
- final structured decomposition in the answer payload

Expected forced-failure Day 13 demo output includes:

- `Status: fallback`
- `Unknown analysis step: ok` or `Unknown analysis step: failed`
- `Risk analysis step: failed`
- `Approval decision step: skipped`
- `Review step: skipped`
- `Failure reason: Forced failure for analyze_task_risks.`
- `Retry count: 2`

Current workflow limitations:

- this slice now routes through one explicit LangGraph workflow with separate draft-generation, unknown-analysis, risk-analysis, approval-decision, and review boundaries before completion or fallback;
- it still reads one fixed markdown task input and exposes narrow `unknown` and `risk` analysis tool paths;
- retry is modeled separately for the draft-generation node and the risk-analysis node;
- it does not support CLI-selected files, multi-source ingestion, multi-tool planning, or broader review/approval policies yet.
- the first eval artifact is a deterministic local dataset at `src/agentic_learning/evals/data/task_decomposer_eval_dataset_v1.json`; it stores draft fixtures plus expected unknown, risk, approval, and quality signals so evaluation can stay reproducible without depending on live model output.
- the deterministic eval runner writes `artifacts/evals/task_decomposer_eval_summary_v1.json` by invoking the real compiled graph against dataset-provided draft, unknown, and risk fixtures, so graph/policy behavior stays reproducible without live model drift or keyword-heuristic coupling.
- the current failure-analysis surface is generated locally into `artifacts/evals/task_decomposer_failure_log_v1.md` and `artifacts/evals/task_decomposer_eval_note_v1.md`; it records current guarded review buckets, the harness proof boundary, and the current portfolio-facing explanation of the eval surface.

## Project 1 Eval Surface

If you want the shortest honest read on Project 1 today, start here instead of opening the raw JSON first.

Current deterministic snapshot:

- eval cases: 21
- passing cases: 21/21
- approved outcomes: 6
- review-required outcomes: 15
- unknown-driven review cases: 11
- high-risk review cases: 4

Why this matters:

- the repo now proves more than schema shape; it proves compiled-graph routing, approval decisions, review branching, and a narrow set of output-quality checks against a fixed corpus;
- `review_required` is not treated as an eval failure here; it is an expected guarded workflow outcome when unknowns or high-risk signals are present;
- the current failure log separates real mismatches from expected review states so the artifact does not confuse control behavior with regression.

What the current deterministic harness proves:

- the compiled graph still reaches stable `approved` and `review_required` end states;
- approval logic matches the dataset-provided unknown and risk signals;
- workflow step outcomes remain explicit across draft, unknown analysis, risk analysis, approval decision, and review;
- basic structured-output checks stay stable: implementation task count, test idea count, unknown count, risk count, and done-criteria uniqueness.

What it does not prove yet:

- live model draft quality or prompt drift, because the draft edge is fixture-driven in the eval harness;
- real unknown/risk tool heuristic quality, because those analysis edges are also fixture-driven in the eval run;
- fallback behavior inside the eval suite, because forced-failure proof still lives in separate workflow tests and demo commands;
- trace quality, latency, cost, or network sensitivity.

Artifact map:

- dataset: `src/agentic_learning/evals/data/task_decomposer_eval_dataset_v1.json`
- machine-readable summary: `artifacts/evals/task_decomposer_eval_summary_v1.json`
- failure log: `artifacts/evals/task_decomposer_failure_log_v1.md`
- short eval note: `artifacts/evals/task_decomposer_eval_note_v1.md`
- compact workflow note: `docs/Project1_Task_Decomposer_Workflow.md`
- prompt contracts and failure modes note: `docs/Project1_Prompt_Contracts_And_Failure_Modes.md`

## Tracing

Week 1 tracing was verified in LangSmith with:

- project: `agentic-learning-week1`
- root trace: `LangGraph`
- nested runs including `ChatAnthropic`, `tools`, `add_numbers`, and `multiply_numbers`

Project 1 model-backed runs were also re-verified locally during the later closeout passes, but a dedicated Project 1 trace link or screenshot is not currently curated in the repo surface. If traces do not appear on this machine, verify local LangSmith configuration, including `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, and `LANGSMITH_ENDPOINT` when a non-default endpoint is required.

This repository uses `LANGSMITH_PROJECT=agentic-learning-week1` as the canonical project name for the preserved Week 1 tracing evidence and follow-up local runs. If you change the project name locally, new traces will land in a different bucket and the historical notes in this repo will no longer match what you see in LangSmith.

If your LangSmith API key belongs to multiple workspaces, also set `LANGSMITH_WORKSPACE_ID` explicitly so traces do not disappear into a different workspace than the one you are viewing.

## Current Dependencies

- LangChain
- LangChain Anthropic
- LangGraph
- LangSmith
- Pydantic

## Notes

Day 1 intentionally avoids model calls. The first artifact is a stable project skeleton.

Day 2 adds a typed multiplication tool and an Anthropic agent that calls it.

Day 3 adds a validated `ArithmeticResult` schema, a deterministic validation script, and a structured output agent path that returns a typed object instead of relying on loose final-message parsing.

Day 4 adds a second arithmetic tool, explicit prompt-level routing constraints, and a routing demo that shows supported tool calls and unsupported refusal behavior.

Day 6 adds basic runtime error handling around the routing demo so execution failures produce deterministic fallback output instead of a traceback in normal demo output.

Day 8 starts Project 1 with `TaskDecomposerResult`, a deterministic contract validator, three sample task prompts, and a minimal structured-output path for a narrow engineering-task decomposition case.

Day 9 hardens `TaskDecomposerResult` so the Week 2 contract now uses nested typed models for implementation tasks, risks, test ideas, and unknowns; stricter field and list constraints; normalization of trimmed text; duplicate rejection for `done_criteria`; and a more explicit structured-output prompt that keeps the model aligned with the schema.

Day 10 keeps the same contract and agent prompt, but replaces the hardcoded inline task string with one explicit file read from `src/examples/input_backend_endpoint.md` so the decomposer now consumes a real sample input artifact.

Day 11 keeps the Day 10 ingestion path, adds one explicit `analyze_task_risks` tool, and introduces `task_decomposer_demo` so the repo can show both the final structured result and the tool name used during the run.

Day 12 introduced the first explicit LangGraph workflow boundary. The current version has since evolved into `read_input -> run_decomposer_draft -> run_unknown_analysis -> run_risk_analysis -> run_approval_decision -> review_output|fallback|END`.

Day 13 added one forced-failure trigger for `analyze_task_risks`, one bounded retry before fallback, and visible retry-count evidence in the demo output so the degraded path could be exercised deliberately instead of inferred.

Days 15-23 turned the decomposer from a single structured-output slice into a controlled workflow with explicit approval policy, review artifact, step outcomes, compiled-graph terminal-state tests, and the second meaningful tool path for `unknowns`.

Days 24-29 turned the controlled workflow into a more legible portfolio artifact set: checked-in eval corpus, deterministic eval runner, failure log, repo-facing eval explanation, workflow note, and the final prompt-contracts/failure-modes note.
