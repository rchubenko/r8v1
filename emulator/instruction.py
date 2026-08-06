"""Immutable instruction values and stateless ISA decoding for R8 v1."""

from dataclasses import dataclass
from enum import Enum
from typing import Final

from cpu import InvalidComponentValue, validate_address, validate_nibble

INSTRUCTION_MASK: Final = 0xFFFF


class Opcode(Enum):
    """The sixteen four-bit R8 v1 opcode values."""

    NOP = 0x0
    LDI = 0x1
    LDA = 0x2
    ADD = 0x3
    SUB = 0x4
    STA = 0x5
    JMP = 0x6
    JC = 0x7
    JZ = 0x8
    JN = 0x9
    JV = 0xA
    RESERVED_B = 0xB
    RESERVED_C = 0xC
    RESERVED_D = 0xD
    RESERVED_E = 0xE
    HLT = 0xF


def _validate_instruction(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= INSTRUCTION_MASK:
        actual = (
            f"{value:#x}" if isinstance(value, int) and not isinstance(value, bool) else repr(value)
        )
        raise InvalidComponentValue(
            f"instruction must be an integer in range 0x0..FFFF; got {actual}"
        )
    return value


@dataclass(frozen=True, slots=True)
class DecodedInstruction:
    """Immutable opcode and 12-bit operand extracted from one instruction."""

    opcode: Opcode
    operand: int

    def __post_init__(self) -> None:
        if not isinstance(self.opcode, Opcode):
            raise TypeError(f"opcode must be an Opcode; got {self.opcode!r}")
        validate_address(self.operand)


def decode_instruction(instruction: object) -> DecodedInstruction:
    """Decode one validated 16-bit instruction into typed value fields."""

    value = _validate_instruction(instruction)
    opcode_value = validate_nibble(value >> 12)
    operand = validate_address(value & 0xFFF)
    return DecodedInstruction(Opcode(opcode_value), operand)
