from agentic_learning.evals.task_decomposer_eval_runner import (
    TASK_DECOMPOSER_EVAL_SUMMARY_PATH,
    write_task_decomposer_eval_summary,
)


def main() -> None:
    summary = write_task_decomposer_eval_summary()
    print(f"Summary: {summary['summary_name']}")
    print(f"Dataset: {summary['dataset_name']}")
    print(f"Total cases: {summary['total_cases']}")
    print(f"Passed cases: {summary['passed_cases']}")
    print(f"Failed cases: {summary['failed_cases']}")
    print(f"Wrote summary: {TASK_DECOMPOSER_EVAL_SUMMARY_PATH}")


if __name__ == "__main__":
    main()
