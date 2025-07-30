"""Type definitions for Zodic."""

from typing import Any, Dict, List, Optional, TypeVar, Union, Generic, Protocol

try:
    from typing import TypedDict, Literal
except ImportError:
    from typing_extensions import TypedDict, Literal

# Type variables
T = TypeVar("T")
U = TypeVar("U")

# Input/Output types
Input = Any
Output = TypeVar("Output")


# Validation context for error reporting
class ValidationContext:
    """Context information for validation operations."""

    def __init__(self, path: Optional[List[Union[str, int]]] = None) -> None:
        self.path = path or []

    def push(self, key: Union[str, int]) -> "ValidationContext":
        """Create a new context with an additional path element."""
        return ValidationContext(self.path + [key])

    def get_path_string(self) -> str:
        """Get a human-readable path string."""
        if not self.path:
            return "root"

        result = ""
        for i, segment in enumerate(self.path):
            if isinstance(segment, str):
                if i == 0:
                    result = segment
                else:
                    result += f".{segment}"
            else:  # int (array index)
                result += f"[{segment}]"
        return result


# Parse result types
class ParseSuccess(TypedDict, Generic[T]):
    """Successful parse result."""

    success: Literal[True]
    data: T


class ParseFailure(TypedDict):
    """Failed parse result."""

    success: Literal[False]
    error: "ZodError"


# Union type for safe parse results
SafeParseResult = Union[ParseSuccess[T], ParseFailure]
ParseResult = T


# Issue types for error reporting
class ValidationIssue(TypedDict):
    """A single validation issue."""

    code: str
    message: str
    path: List[Union[str, int]]
    received: Any
    expected: Optional[str]


# Protocol for custom validators
class ValidatorProtocol(Protocol[T]):
    """Protocol for custom validator functions."""

    def __call__(self, value: Any, ctx: ValidationContext) -> T:
        """Validate and return the parsed value."""
        ...


# Transform function protocol
class TransformProtocol(Protocol[T, U]):
    """Protocol for transform functions."""

    def __call__(self, value: T) -> U:
        """Transform the input value to output value."""
        ...


# Refinement function protocol
class RefinementProtocol(Protocol[T]):
    """Protocol for refinement/custom validation functions."""

    def __call__(self, value: T) -> bool:
        """Return True if value passes validation."""
        ...
