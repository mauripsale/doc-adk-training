from pydantic import BaseModel


class MathResult(BaseModel):
    status: str
    result: float = 0
    message: str | None = None


def add(a: int, b: int) -> MathResult:
    """
    Adds two numbers together.
    Use this tool when the user asks to find the sum of two numbers.
    """
    return MathResult(status="success", result=a + b)


def subtract(a: int, b: int) -> MathResult:
    """
    Subtracts the second number from the first number.
    """
    return MathResult(status="success", result=a - b)


def multiply(a: int, b: int) -> MathResult:
    """
    Multiplies two numbers together.
    """
    return MathResult(status="success", result=a * b)


def divide(a: int, b: int) -> MathResult:
    """
    Divides the first number by the second number.
    """
    if b == 0:
        return MathResult(status="error", message="Cannot divide by zero.")
    return MathResult(status="success", result=a / b)
