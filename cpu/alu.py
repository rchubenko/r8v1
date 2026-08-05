"""Unified stateless 8-bit ALU interface for R8 v1."""

from dataclasses import dataclass
from enum import Enum

from .alu_add import add
from .alu_sub import subtract


class ALUMode(Enum):
    """Operations supported by the public software ALU API."""

    ADD = "add"
    SUB = "sub"


@dataclass(frozen=True, slots=True)
class ALUResult:
    """Immutable unified result and concrete flags returned by the ALU."""

    result: int
    zero: bool
    carry: bool
    sign: bool
    overflow: bool


def evaluate(mode: ALUMode, a: object, b: object) -> ALUResult:
    """Evaluate one explicitly selected ALU operation without storing state."""

    if not isinstance(mode, ALUMode):
        raise TypeError(f"mode must be an ALUMode; got {mode!r}")

    operation = add if mode is ALUMode.ADD else subtract
    operation_result = operation(a, b)
    return ALUResult(
        result=operation_result.result,
        zero=operation_result.zero,
        carry=operation_result.carry,
        sign=operation_result.sign,
        overflow=operation_result.overflow,
    )
