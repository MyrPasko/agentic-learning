from langchain_core.tools import StructuredTool


def _multiply_numbers(a: float, b: float) -> float:
    """Multiply two numeric values and return the product."""
    return a * b


multiply_numbers: StructuredTool = StructuredTool.from_function(
    func=_multiply_numbers,
    name="multiply_numbers",
    description="Multiply two numeric values and return the product.",
)
