PYTHON ?= ./.venv/bin/python
LOCAL_ENV = env PYTHONDONTWRITEBYTECODE=1 LANGSMITH_TRACING=false LANGCHAIN_TRACING_V2=false

.PHONY: help install sanity test test-workflow validate-arithmetic validate-task validate-task-eval-dataset validate-pr-review-intake eval-task eval-task-failure-log demo-direct demo-agent demo-routing demo-structured demo-pr-review-intake demo-task demo-task-fallback

help:
	@printf "Available targets:\n"
	@printf "  make install              Install the project into the local venv.\n"
	@printf "  make sanity               Run the Day 1 environment check.\n"
	@printf "  make test                 Run the full deterministic test suite.\n"
	@printf "  make test-workflow        Run only the workflow test module.\n"
	@printf "  make validate-arithmetic  Run the arithmetic schema validator.\n"
	@printf "  make validate-task        Run the task-decomposer validator.\n"
	@printf "  make validate-task-eval-dataset  Run the task-decomposer eval dataset validator.\n"
	@printf "  make validate-pr-review-intake  Run the Project 2 intake schema validator.\n"
	@printf "  make eval-task            Run the deterministic task-decomposer eval suite and write its JSON summary.\n"
	@printf "  make eval-task-failure-log  Refresh the eval summary, failure log, and portfolio note artifacts.\n"
	@printf "  make demo-direct          Run the direct tool call demo.\n"
	@printf "  make demo-agent           Run the Day 2 live tool-call demo.\n"
	@printf "  make demo-routing         Run the routing plus fallback demo.\n"
	@printf "  make demo-structured      Run the structured task-decomposer agent path.\n"
	@printf "  make demo-pr-review-intake  Run the Project 2 structured PR intake demo.\n"
	@printf "  make demo-task            Run the graph-backed task decomposer demo.\n"
	@printf "  make demo-task-fallback   Run the forced-failure graph demo.\n"

install:
	$(PYTHON) -m pip install -e .

sanity:
	$(PYTHON) -m agentic_learning.main

test:
	$(LOCAL_ENV) $(PYTHON) -m unittest discover -s tests

test-workflow:
	$(LOCAL_ENV) $(PYTHON) -m unittest tests.test_task_decomposer_workflow

validate-arithmetic:
	$(LOCAL_ENV) $(PYTHON) -m agentic_learning.validate_arithmetic_result

validate-task:
	$(LOCAL_ENV) $(PYTHON) -m agentic_learning.validate_task_decomposer_result

validate-task-eval-dataset:
	$(LOCAL_ENV) $(PYTHON) -m agentic_learning.validate_task_decomposer_eval_dataset

validate-pr-review-intake:
	$(LOCAL_ENV) $(PYTHON) -m agentic_learning.validate_pr_review_intake_result

eval-task:
	$(LOCAL_ENV) $(PYTHON) -m agentic_learning.run_task_decomposer_eval

eval-task-failure-log:
	$(LOCAL_ENV) $(PYTHON) -m agentic_learning.run_task_decomposer_failure_log

demo-direct:
	$(LOCAL_ENV) $(PYTHON) -m agentic_learning.direct_tool_call

demo-agent:
	@test -f .env || { echo ".env is missing. Create it from .env.example first."; exit 1; }
	@set -a; . ./.env; set +a; $(PYTHON) -m agentic_learning.agent_tool_call

demo-routing:
	@test -f .env || { echo ".env is missing. Create it from .env.example first."; exit 1; }
	@set -a; . ./.env; set +a; $(PYTHON) -m agentic_learning.agent_tool_routing_demo

demo-structured:
	@test -f .env || { echo ".env is missing. Create it from .env.example first."; exit 1; }
	@set -a; . ./.env; set +a; $(PYTHON) -m agentic_learning.structured_task_decomposer_agent_call

demo-pr-review-intake:
	@test -f .env || { echo ".env is missing. Create it from .env.example first."; exit 1; }
	@set -a; . ./.env; set +a; $(PYTHON) -m agentic_learning.structured_pr_review_intake_agent_call

demo-task:
	@test -f .env || { echo ".env is missing. Create it from .env.example first."; exit 1; }
	@set -a; . ./.env; set +a; $(PYTHON) -m agentic_learning.task_decomposer_demo

demo-task-fallback:
	@test -f .env || { echo ".env is missing. Create it from .env.example first."; exit 1; }
	@set -a; . ./.env; set +a; FORCE_RISK_TOOL_FAILURE=1 $(PYTHON) -m agentic_learning.task_decomposer_demo
