import unittest

from agentic_learning.evals import (
    TASK_DECOMPOSER_EVAL_DATASET_PATH,
    load_task_decomposer_eval_dataset,
)


class TaskDecomposerEvalDatasetTests(unittest.TestCase):
    def test_dataset_file_exists(self) -> None:
        self.assertTrue(TASK_DECOMPOSER_EVAL_DATASET_PATH.is_file())

    def test_dataset_loads_with_minimum_case_count(self) -> None:
        dataset = load_task_decomposer_eval_dataset()

        self.assertEqual(dataset.dataset_name, "task_decomposer_eval_dataset_v1")
        self.assertGreaterEqual(len(dataset.cases), 20)

    def test_dataset_covers_approved_and_review_required_cases(self) -> None:
        dataset = load_task_decomposer_eval_dataset()

        approval_statuses = {case.expected_approval_status for case in dataset.cases}
        self.assertEqual(approval_statuses, {"approved", "review_required"})

    def test_case_quality_counts_match_expected_lists(self) -> None:
        dataset = load_task_decomposer_eval_dataset()

        for case in dataset.cases:
            self.assertEqual(
                case.expected_quality.unknown_count,
                len(case.expected_unknown_questions),
            )
            self.assertEqual(
                case.expected_quality.risk_count,
                len(case.expected_risk_impacts),
            )


if __name__ == "__main__":
    unittest.main()
