"""
Zodic - A TypeScript Zod-inspired validation library for Python.

Zodic provides a simple, chainable API for validating and parsing data
with excellent type safety and developer experience.

Example:
    >>> import zodic as z
    >>> schema = z.string().min(3).max(10)
    >>> result = schema.parse("hello")  # Returns "hello"
    >>> 
    >>> user_schema = z.object({
    ...     'name': z.string(),
    ...     'age': z.number().int().positive()
    ... })
    >>> user = user_schema.parse({'name': 'John', 'age': 30})
"""

__version__ = "0.1.0"
__author__ = "Zodic Contributors"
__email__ = "contributors@zodic.dev"

from .core.base import Schema
from .core.errors import ZodError, ValidationError
from .schemas.primitives import string, number, boolean, none
from .schemas.collections import object, array
from .schemas.special import optional, nullable, union

# Main API exports - following Zod's naming convention
__all__ = [
    # Core classes
    "Schema",
    "ZodError",
    "ValidationError",
    # Schema constructors
    "string",
    "number",
    "boolean",
    "none",
    "object",
    "array",
    "optional",
    "nullable",
    "union",
    # Version info
    "__version__",
]
