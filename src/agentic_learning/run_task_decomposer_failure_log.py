from agentic_learning.evals.task_decomposer_failure_log import (
    write_task_decomposer_failure_artifacts,
)


def main() -> None:
    result = write_task_decomposer_failure_artifacts()
    summary = result["summary"]
    print(f"Summary cases: {summary['passed_cases']}/{summary['total_cases']}")
    print(f"Failure log: {result['failure_log_path']}")
    print(f"Eval note: {result['eval_note_path']}")


if __name__ == "__main__":
    main()
