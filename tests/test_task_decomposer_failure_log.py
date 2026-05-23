import tempfile
import unittest
from pathlib import Path

from agentic_learning.evals.task_decomposer_eval_runner import (
    run_task_decomposer_eval_suite,
)
from agentic_learning.evals.task_decomposer_failure_log import (
    build_task_decomposer_eval_note,
    build_task_decomposer_failure_log,
    write_task_decomposer_failure_artifacts,
)


class TaskDecomposerFailureLogTests(unittest.TestCase):
    def test_failure_log_includes_current_bucket_counts(self) -> None:
        summary = run_task_decomposer_eval_suite()

        failure_log = build_task_decomposer_failure_log(summary)

        self.assertIn("Observed eval mismatches: 0", failure_log)
        self.assertIn("Approved path (6)", failure_log)
        self.assertIn("Review-required because of unknowns (11)", failure_log)
        self.assertIn("Review-required because of high risk (4)", failure_log)

    def test_eval_note_mentions_current_scope_and_limits(self) -> None:
        summary = run_task_decomposer_eval_suite()

        eval_note = build_task_decomposer_eval_note(summary)

        self.assertIn("passes `21/21`", eval_note)
        self.assertIn("Approved path coverage: 6 cases.", eval_note)
        self.assertIn("The eval harness freezes draft, unknown, and risk edges", eval_note)

    def test_write_failure_artifacts_writes_both_markdown_files(self) -> None:
        summary = run_task_decomposer_eval_suite()

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            failure_log_path = root / "failure_log.md"
            eval_note_path = root / "eval_note.md"

            result = write_task_decomposer_failure_artifacts(
                failure_log_path=failure_log_path,
                eval_note_path=eval_note_path,
                summary=summary,
            )

            self.assertEqual(result["summary"]["passed_cases"], 21)
            self.assertTrue(failure_log_path.is_file())
            self.assertTrue(eval_note_path.is_file())


if __name__ == "__main__":
    unittest.main()
