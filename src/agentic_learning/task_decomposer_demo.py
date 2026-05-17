from agentic_learning.task_decomposer_graph import task_decomposer_graph


def run_graph() -> None:
    result = task_decomposer_graph.invoke({})

    prompt = result.get("prompt")
    structured_response = result.get("structured_response")
    tool_name = result.get("tool_name")
    failure_reason = result.get("failure_reason")
    used_fallback = result.get("used_fallback", False)
    retry_count = result.get("retry_count", 0)
    approval_status = result.get("approval_status")
    review_reason = result.get("review_reason")
    review_summary = result.get("review_summary")

    status = "fallback" if used_fallback else "ok"
    answer = (
        structured_response.model_dump_json(indent=2)
        if structured_response
        else "The response is unavailable"
    )

    print(f"Prompt: {prompt}")
    print(f"Status: {status}")
    print(f"Tool: {tool_name}")
    print(f"Answer: {answer}")
    print(f"Failure reason: {failure_reason}")
    print(f"Retry count: {retry_count}")
    print(f"Approval status: {approval_status}")
    print(f"Review reason: {review_reason}")
    print(f"Review summary: {review_summary}")
    print("---")


def main() -> None:
    run_graph()


if __name__ == "__main__":
    main()
