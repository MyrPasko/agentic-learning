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

Day 1 sanity check:

```bash
python -m agentic_learning.main
```

Expected output:

```text
Agentic learning environment is ready.
```

Day 2 direct tool call demo:

```bash
.venv/bin/python -m agentic_learning.direct_tool_call
```

Day 2 live agent tool call demo:

```bash
export ANTHROPIC_API_KEY="..."
.venv/bin/python -m agentic_learning.agent_tool_call
```

Day 3 deterministic schema validation demo:

```bash
.venv/bin/python -m agentic_learning.validate_arithmetic_result
```

Day 3 structured output agent demo:

```bash
export ANTHROPIC_API_KEY="..."
.venv/bin/python -m agentic_learning.structured_agent_tool_call
```

Day 4 and Day 6 routing plus fallback demo:

```bash
export ANTHROPIC_API_KEY="..."
.venv/bin/python -m agentic_learning.agent_tool_routing_demo
```

Day 8 deterministic task-decomposer contract demo:

```bash
.venv/bin/python -m agentic_learning.validate_task_decomposer_result
```

Day 8 structured task-decomposer demo:

```bash
export ANTHROPIC_API_KEY="..."
.venv/bin/python -m agentic_learning.structured_task_decomposer_agent_call
```

Current Day 8 limitation:

- this slice validates one narrow decomposition contract and demonstrates one structured-output run;
- it does not use LangGraph state, review nodes, retries, or approval checkpoints yet.

## Tracing

Week 1 tracing was verified in LangSmith with:

- project: `agentic-learning-week1`
- root trace: `LangGraph`
- nested runs including `ChatAnthropic`, `tools`, `add_numbers`, and `multiply_numbers`

If traces do not appear on this machine, verify local LangSmith configuration, including `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, and `LANGSMITH_ENDPOINT` when a non-default endpoint is required.

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
