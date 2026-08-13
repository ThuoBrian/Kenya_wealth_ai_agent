"""Shared domain validators for Kenya Wealth Agent.

Validators in this module are intentionally small, pure, and reusable across
services.  They raise `ValueError` with clear messages so that boundary layers
(FastAPI, CLI) can translate them into user-friendly errors.
"""

from typing import TypeVar

T = TypeVar("T", int, float)


def require_non_negative(value: T, name: str) -> T:
    """Ensure a numeric value is non-negative.

    Args:
        value: Numeric amount to validate.
        name: Human-readable name of the field (used in error messages).

    Returns:
        The original value if valid.

    Raises:
        ValueError: If ``value`` is negative or not a number.
    """
    if value is None:
        raise ValueError(f"{name} is required")
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number, got {value!r}") from exc
    if numeric < 0:
        raise ValueError(f"{name} cannot be negative (got {numeric})")
    return value


def require_positive(value: T, name: str) -> T:
    """Ensure a numeric value is strictly positive.

    Args:
        value: Numeric amount to validate.
        name: Human-readable name of the field.

    Returns:
        The original value if valid.

    Raises:
        ValueError: If ``value`` is zero, negative, or not a number.
    """
    if value is None:
        raise ValueError(f"{name} is required")
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number, got {value!r}") from exc
    if numeric <= 0:
        raise ValueError(f"{name} must be positive (got {numeric})")
    return value
