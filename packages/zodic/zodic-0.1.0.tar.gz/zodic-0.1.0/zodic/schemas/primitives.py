"""Primitive type schemas for Zodic."""

from typing import Any, Union, Optional
from ..core.base import Schema
from ..core.types import ValidationContext
from ..core.errors import ZodError, invalid_type_issue, custom_issue


class StringSchema(Schema[str]):
    """Schema for string validation."""

    def __init__(self) -> None:
        super().__init__()
        self._min_length: Optional[int] = None
        self._max_length: Optional[int] = None

    def _parse_value(self, value: Any, ctx: ValidationContext) -> str:
        """Parse and validate a string value."""
        if not isinstance(value, str):
            raise ZodError([invalid_type_issue(value, "string", ctx)])

        # Length validations
        if self._min_length is not None and len(value) < self._min_length:
            raise ZodError(
                [
                    custom_issue(
                        f"String must be at least {self._min_length} characters long",
                        ctx,
                        value,
                    )
                ]
            )

        if self._max_length is not None and len(value) > self._max_length:
            raise ZodError(
                [
                    custom_issue(
                        f"String must be at most {self._max_length} characters long",
                        ctx,
                        value,
                    )
                ]
            )

        return value

    def min(self, length: int) -> "StringSchema":
        """Set minimum length constraint."""
        new_schema = self._clone()
        new_schema._min_length = length
        return new_schema

    def max(self, length: int) -> "StringSchema":
        """Set maximum length constraint."""
        new_schema = self._clone()
        new_schema._max_length = length
        return new_schema

    def length(self, length: int) -> "StringSchema":
        """Set exact length constraint."""
        return self.min(length).max(length)

    def _clone(self) -> "StringSchema":
        """Create a copy of this schema."""
        new_schema = super()._clone()
        new_schema._min_length = self._min_length
        new_schema._max_length = self._max_length
        return new_schema


class NumberSchema(Schema[Union[int, float]]):
    """Schema for number validation."""

    def __init__(self) -> None:
        super().__init__()
        self._min_value: Optional[float] = None
        self._max_value: Optional[float] = None
        self._int_only = False

    def _parse_value(self, value: Any, ctx: ValidationContext) -> Union[int, float]:
        """Parse and validate a number value."""
        if not isinstance(value, (int, float)):
            raise ZodError([invalid_type_issue(value, "number", ctx)])

        # Check for NaN and infinity
        if isinstance(value, float):
            if value != value:  # NaN check
                raise ZodError([custom_issue("Number cannot be NaN", ctx, value)])
            if value == float("inf") or value == float("-inf"):
                raise ZodError([custom_issue("Number cannot be infinite", ctx, value)])

        # Integer constraint
        if self._int_only and not isinstance(value, int):
            if isinstance(value, float) and value.is_integer():
                value = int(value)
            else:
                raise ZodError([custom_issue("Expected integer", ctx, value)])

        # Range validations
        if self._min_value is not None and value < self._min_value:
            raise ZodError(
                [
                    custom_issue(
                        f"Number must be greater than or equal to {self._min_value}",
                        ctx,
                        value,
                    )
                ]
            )

        if self._max_value is not None and value > self._max_value:
            raise ZodError(
                [
                    custom_issue(
                        f"Number must be less than or equal to {self._max_value}",
                        ctx,
                        value,
                    )
                ]
            )

        return value

    def min(self, value: float) -> "NumberSchema":
        """Set minimum value constraint."""
        new_schema = self._clone()
        new_schema._min_value = value
        return new_schema

    def max(self, value: float) -> "NumberSchema":
        """Set maximum value constraint."""
        new_schema = self._clone()
        new_schema._max_value = value
        return new_schema

    def int(self) -> "NumberSchema":
        """Require the number to be an integer."""
        new_schema = self._clone()
        new_schema._int_only = True
        return new_schema

    def positive(self) -> "NumberSchema":
        """Require the number to be positive (> 0)."""
        return self.min(0.000001)  # Slightly above 0 to exclude 0

    def negative(self) -> "NumberSchema":
        """Require the number to be negative (< 0)."""
        return self.max(-0.000001)  # Slightly below 0 to exclude 0

    def nonnegative(self) -> "NumberSchema":
        """Require the number to be non-negative (>= 0)."""
        return self.min(0)

    def _clone(self) -> "NumberSchema":
        """Create a copy of this schema."""
        new_schema = super()._clone()
        new_schema._min_value = self._min_value
        new_schema._max_value = self._max_value
        new_schema._int_only = self._int_only
        return new_schema


class BooleanSchema(Schema[bool]):
    """Schema for boolean validation."""

    def _parse_value(self, value: Any, ctx: ValidationContext) -> bool:
        """Parse and validate a boolean value."""
        if not isinstance(value, bool):
            raise ZodError([invalid_type_issue(value, "boolean", ctx)])
        return value


class NoneSchema(Schema[None]):
    """Schema for None/null validation."""

    def _parse_value(self, value: Any, ctx: ValidationContext) -> None:
        """Parse and validate a None value."""
        if value is not None:
            raise ZodError([invalid_type_issue(value, "null", ctx)])
        return None


# Factory functions (following Zod's API)
def string() -> StringSchema:
    """Create a string schema."""
    return StringSchema()


def number() -> NumberSchema:
    """Create a number schema."""
    return NumberSchema()


def boolean() -> BooleanSchema:
    """Create a boolean schema."""
    return BooleanSchema()


def none() -> NoneSchema:
    """Create a None schema."""
    return NoneSchema()
