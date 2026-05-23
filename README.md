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

## Week 2 Progression

- Day 8: first `AI Task Decomposer` contract slice with sample inputs, typed output schema, deterministic validation, and one minimal structured-output run.
- Day 9: harden the decomposer contract with nested typed items, stricter validation, trimmed input normalization, duplicate checks for `done_criteria`, and a stronger structured-output prompt.
- Day 10: replace the hardcoded decomposer prompt with one explicit file-ingestion path that reads a sample task from `src/examples/input_backend_endpoint.md`.
- Day 11: add one narrow `analyze_task_risks` tool path and a demo entrypoint that makes tool use visible alongside the final structured decomposition.
- Day 12: move the Day 10-11 decomposer path into the first explicit LangGraph workflow, which later became the current `read_input -> run_decomposer_draft -> run_risk_analysis` path.
- Day 13: add one forced-failure trigger for `analyze_task_risks` plus one bounded retry and fallback branch around the graph-backed decomposer run.
- Day 23: add `analyze_task_unknowns` as a separate deterministic clarity-analysis step before risk analysis so Project 1 now uses at least two meaningful domain tool paths.

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

Week 2 canonical demo set:

- contract validation:

```bash
make validate-task
```

- workflow-control tests:

```bash
make test
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

## Tracing

Week 1 tracing was verified in LangSmith with:

- project: `agentic-learning-week1`
- root trace: `LangGraph`
- nested runs including `ChatAnthropic`, `tools`, `add_numbers`, and `multiply_numbers`

If traces do not appear on this machine, verify local LangSmith configuration, including `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, and `LANGSMITH_ENDPOINT` when a non-default endpoint is required.

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

Day 12 introduced the first explicit LangGraph workflow boundary. The current version has evolved that path into `read_input -> run_decomposer_draft -> run_risk_analysis`, where the draft agent and the risk-analysis tool now live in separate workflow nodes.

Day 13 kept the graph boundary, added one forced-failure trigger for `analyze_task_risks`, one bounded retry before fallback, and visible retry-count evidence in the demo output so the degraded path could be exercised deliberately instead of inferred. The current graph keeps that degraded-path evidence while modeling the risk-analysis step as its own node.
