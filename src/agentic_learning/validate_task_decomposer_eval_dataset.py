from collections import Counter

from agentic_learning.evals import load_task_decomposer_eval_dataset


def main() -> None:
    dataset = load_task_decomposer_eval_dataset()
    approval_counts = Counter(
        case.expected_approval_status for case in dataset.cases
    )
    review_reason_counts = Counter(
        case.expected_review_reason or "approved" for case in dataset.cases
    )

    print(f"Dataset: {dataset.dataset_name}")
    print(f"Total cases: {len(dataset.cases)}")
    print(f"Approved cases: {approval_counts['approved']}")
    print(f"Review-required cases: {approval_counts['review_required']}")
    print("Review reasons:")
    for review_reason, count in sorted(review_reason_counts.items()):
        print(f"- {review_reason}: {count}")


if __name__ == "__main__":
    main()
