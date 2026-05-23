# Task Decomposer Failure Log v1

- Source summary: `/Users/myroslavpasko/projects/agentic-learning/artifacts/evals/task_decomposer_eval_summary_v1.json`
- Total eval cases: 21
- Passed cases: 21
- Observed eval mismatches: 0
- Important nuance: `review_required` is an expected guarded workflow outcome here, not an eval regression by itself.

## Current Outcome Buckets

- Approved path (6): approved-readme-introduction, approved-dashboard-spacing, approved-rename-parser-helper, approved-date-formatting-cleanup, approved-cli-output-copy, approved-loading-state-classes
- Review-required because of unknowns (11): validation-portfolio-endpoint, validation-api-payload-cleanup, validation-bulk-import-endpoint, validation-form-schema-rules, auth-admin-role-guard, auth-session-permissions, auth-token-ownership-check, dependency-database-migration, dependency-queue-retry-tuning, mixed-auth-endpoint-ownership, mixed-api-database-import
- Review-required because of high risk (4): risk-only-billing-export-tests, risk-only-markdown-renderer-tests, risk-only-pagination-tests, risk-only-search-ranking-tests

## Current Failure Taxonomy Inputs

- Authorization-rule uncertainty (4): auth-admin-role-guard, auth-session-permissions, auth-token-ownership-check, mixed-auth-endpoint-ownership
- Validation or contract uncertainty (6): validation-portfolio-endpoint, validation-api-payload-cleanup, validation-bulk-import-endpoint, validation-form-schema-rules, mixed-auth-endpoint-ownership, mixed-api-database-import
- Dependency or persistence uncertainty (3): dependency-database-migration, dependency-queue-retry-tuning, mixed-api-database-import
- High-risk but no unknowns (4): risk-only-billing-export-tests, risk-only-markdown-renderer-tests, risk-only-pagination-tests, risk-only-search-ranking-tests

## What The Current Deterministic Harness Proves

- The compiled graph still reaches stable `approved` and `review_required` outcomes against fixed fixtures.
- Approval decisions match the dataset-provided unknown and risk signals.
- Step outcomes remain explicit across draft, unknown analysis, risk analysis, approval decision, and review.
- Basic structured-output quality checks remain stable: task count, test count, unknown count, risk count, and done-criteria uniqueness.

## What It Does Not Prove Yet

- Live model draft quality or prompt drift. The draft edge is stubbed.
- Real tool heuristic quality for unknown and risk analysis. Those edges are also fixture-driven inside the eval harness.
- Runtime fallback behavior inside the eval suite. The forced-failure path still lives in separate tests and demo commands.
- Trace quality, latency, cost, or network sensitivity.

## Next Failure-Hunting Targets

- Add explicit fallback-oriented eval artifacts instead of leaving fallback proof only in separate workflow tests and demos.
- Compare real unknown/risk tool heuristics against the fixture expectations so the harness stops assuming the analysis edges are correct.
- Add one failure-note artifact when a future eval run produces mismatches instead of only expected review states.

