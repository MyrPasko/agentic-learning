import unittest

from agentic_learning.evals import load_task_decomposer_eval_dataset
from agentic_learning.evals.task_decomposer_eval_runner import (
    run_task_decomposer_eval_case,
    run_task_decomposer_eval_suite,
)


class TaskDecomposerEvalRunnerTests(unittest.TestCase):
    def test_review_required_case_matches_expected_signals(self) -> None:
        dataset = load_task_decomposer_eval_dataset()
        case = next(
            candidate
            for candidate in dataset.cases
            if candidate.case_id == "validation-portfolio-endpoint"
        )

        result = run_task_decomposer_eval_case(case)

        self.assertTrue(result["passed"])
        self.assertEqual(result["approval_status"], "review_required")
        self.assertEqual(result["review_reason"], "Unknown items detected.")

    def test_full_eval_suite_passes_all_cases(self) -> None:
        summary = run_task_decomposer_eval_suite()

        self.assertEqual(summary["summary_name"], "task_decomposer_eval_summary_v1")
        self.assertEqual(summary["total_cases"], 21)
        self.assertEqual(summary["passed_cases"], 21)
        self.assertEqual(summary["failed_cases"], 0)
        self.assertEqual(summary["failed_case_ids"], [])


if __name__ == "__main__":
    unittest.main()
