# Task Decomposer Eval Note v1

## Why This Matters

- The current local eval surface runs `21` deterministic cases through the compiled task-decomposer graph and currently passes `21/21`.
- This is not a toy schema check anymore. It verifies graph routing, approval decisions, review outcomes, and a narrow set of output-quality constraints.

## What We Can Show

- Approved path coverage: 6 cases.
- Review path coverage: 15 cases.
- Unknown-driven review cases: 11.
- High-risk review cases: 4.
- The repo contains rerunnable eval inputs, a rerunnable eval runner, a machine-readable JSON summary, and now a readable failure log.

## Current Limits

- The eval harness freezes draft, unknown, and risk edges with fixtures, so it demonstrates workflow control more than live inference quality.
- Fallback behavior, trace review, latency, and cost still need separate evidence surfaces.

## Artifacts

- Summary: `/Users/myroslavpasko/projects/agentic-learning/artifacts/evals/task_decomposer_eval_summary_v1.json`
- Failure log: `/Users/myroslavpasko/projects/agentic-learning/artifacts/evals/task_decomposer_failure_log_v1.md`
- Note: `/Users/myroslavpasko/projects/agentic-learning/artifacts/evals/task_decomposer_eval_note_v1.md`

