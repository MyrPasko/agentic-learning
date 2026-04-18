# Agentic Learning

Practice repository for building controlled, observable, and evaluable agentic systems with LangChain, LangGraph, and LangSmith.

This repository follows the 10-week agentic learning roadmap tracked in the Obsidian vault at:

`/Users/myroslavpasko/obsidian/main/AI/AGENTIC_LEARNING`

## Week 1 Goal

Create the first runnable Python project and establish repeatable setup before adding agent behavior.

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

```bash
python -m agentic_learning.main
```

Expected output:

```text
Agentic learning environment is ready.
```

## Current Dependencies

- LangChain
- LangGraph
- LangSmith

## Notes

Day 1 intentionally avoids model calls. The first artifact is a stable project skeleton. Agent execution, tool calling, and LangSmith traces start after the environment is reproducible.
