from langchain_core.tools import StructuredTool


def _add_numbers(a: float, b: float) -> float:
    """Add two numeric values and return the sum."""
    return a + b


add_numbers: StructuredTool = StructuredTool.from_function(
    func=_add_numbers,
    name="add_numbers",
    description="Add two numeric values and return the sum.",
)
