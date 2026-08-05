"""Stateless 8-bit ADD operation for R8 v1."""

from dataclasses import dataclass

from .values import BYTE_MASK, validate_byte


@dataclass(frozen=True, slots=True)
class AddResult:
    """Immutable result and concrete flags produced by an 8-bit ADD."""

    result: int
    zero: bool
    carry: bool
    sign: bool
    overflow: bool


def add(a: object, b: object) -> AddResult:
    """Add two validated bytes and return the result with concrete flags."""

    a_value = validate_byte(a)
    b_value = validate_byte(b)
    wide_sum = a_value + b_value
    result = wide_sum & BYTE_MASK
    a_sign = (a_value >> 7) & 1
    b_sign = (b_value >> 7) & 1
    result_sign = (result >> 7) & 1

    return AddResult(
        result=result,
        zero=result == 0,
        carry=wide_sum > BYTE_MASK,
        sign=bool(result_sign),
        overflow=bool((not (a_sign ^ b_sign)) and (a_sign ^ result_sign)),
    )
