# Agentic Learning

Practice repository for building controlled, observable, and evaluable agentic systems with LangChain, LangGraph, and LangSmith.

This repository follows the 10-week agentic learning roadmap tracked in the Obsidian vault at:

`/Users/myroslavpasko/obsidian/main/AI/AGENTIC_LEARNING`

## Week 1 Goal

Create the first runnable Python project and establish repeatable setup before adding agent behavior, structured outputs, and validation.

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

Do not commit `.env`.

## Run

Run the Day 1 environment sanity check:

```bash
python -m agentic_learning.main
```

Expected output:

```text
Agentic learning environment is ready.
```

Run the Day 2 direct tool call demo:

```bash
.venv/bin/python -m agentic_learning.direct_tool_call
```

Run the Day 2 Anthropic agent tool call demo:

```bash
export ANTHROPIC_API_KEY="..."
.venv/bin/python -m agentic_learning.agent_tool_call
```

Run the Day 3 deterministic schema validation demo:

```bash
.venv/bin/python -m agentic_learning.validate_arithmetic_result
```

Run the Day 3 structured output agent demo:

```bash
export ANTHROPIC_API_KEY="..."
.venv/bin/python -m agentic_learning.structured_agent_tool_call
```

Do not commit real API keys. Use `.env` or shell environment variables locally.

## Current Dependencies

- LangChain
- LangChain Anthropic
- LangGraph
- LangSmith
- Pydantic

## Notes

Day 1 intentionally avoids model calls. The first artifact is a stable project skeleton.

Day 2 adds a typed multiplication tool and an Anthropic agent that calls it.

Day 3 adds a validated `ArithmeticResult` schema, a deterministic validation script, and a structured output agent path that returns a typed object instead of relying on `messages[-1]`.
