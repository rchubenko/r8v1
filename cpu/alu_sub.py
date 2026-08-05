"""Stateless 8-bit SUB operation for R8 v1."""

from dataclasses import dataclass

from .values import BYTE_MASK, validate_byte


@dataclass(frozen=True, slots=True)
class SubtractResult:
    """Immutable result and concrete flags produced by an 8-bit SUB."""

    result: int
    zero: bool
    carry: bool
    sign: bool
    overflow: bool


def subtract(a: object, b: object) -> SubtractResult:
    """Subtract two validated bytes and return the result with concrete flags."""

    a_value = validate_byte(a)
    b_value = validate_byte(b)
    wide_difference = a_value - b_value
    result = wide_difference & BYTE_MASK
    a_sign = (a_value >> 7) & 1
    b_sign = (b_value >> 7) & 1
    result_sign = (result >> 7) & 1

    return SubtractResult(
        result=result,
        zero=result == 0,
        carry=a_value >= b_value,
        sign=bool(result_sign),
        overflow=bool((a_sign ^ b_sign) and (a_sign ^ result_sign)),
    )
