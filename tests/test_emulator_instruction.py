from dataclasses import FrozenInstanceError
from enum import Enum

import pytest

from cpu import InvalidComponentValue
from emulator import DecodedInstruction, Opcode, decode_instruction


@pytest.mark.parametrize("value", range(0x10))
def test_all_opcode_values_have_exact_typed_representations(value: int) -> None:
    decoded = decode_instruction(value << 12)

    assert isinstance(decoded.opcode, Opcode)
    assert decoded.opcode.value == value


def test_opcode_representation_is_an_enum_with_all_sixteen_members() -> None:
    assert issubclass(Opcode, Enum)
    assert len(Opcode) == 16
    assert [opcode.value for opcode in Opcode] == list(range(0x10))


@pytest.mark.parametrize("value", [0x0, 0xA, 0xB, 0xC, 0xD, 0xE, 0xF])
def test_named_opcode_values_match_isa(value: int) -> None:
    decoded = decode_instruction(value << 12)

    assert decoded.opcode.value == value


@pytest.mark.parametrize(
    ("instruction", "expected_operand"),
    [
        (0x0000, 0x000),
        (0x0001, 0x001),
        (0x000F, 0x00F),
        (0x00FF, 0x0FF),
        (0x0100, 0x100),
        (0x0ABC, 0xABC),
        (0x0FFE, 0xFFE),
        (0x0FFF, 0xFFF),
    ],
)
def test_operand_extraction_preserves_all_twelve_bits(
    instruction: int, expected_operand: int
) -> None:
    assert decode_instruction(instruction).operand == expected_operand


@pytest.mark.parametrize(
    ("instruction", "expected_opcode", "expected_operand"),
    [
        (0x0000, Opcode.NOP, 0x000),
        (0x10FF, Opcode.LDI, 0x0FF),
        (0x1ABC, Opcode.LDI, 0xABC),
        (0x2FFF, Opcode.LDA, 0xFFF),
        (0x6000, Opcode.JMP, 0x000),
        (0x6FFF, Opcode.JMP, 0xFFF),
        (0xB123, Opcode.RESERVED_B, 0x123),
        (0xC456, Opcode.RESERVED_C, 0x456),
        (0xD789, Opcode.RESERVED_D, 0x789),
        (0xEABC, Opcode.RESERVED_E, 0xABC),
        (0xF000, Opcode.HLT, 0x000),
        (0xFFFF, Opcode.HLT, 0xFFF),
    ],
)
def test_full_instruction_decode(
    instruction: int, expected_opcode: Opcode, expected_operand: int
) -> None:
    assert decode_instruction(instruction) == DecodedInstruction(expected_opcode, expected_operand)


def test_decode_is_deterministic_and_value_based() -> None:
    first = decode_instruction(0x6ABC)
    second = decode_instruction(0x6ABC)

    assert first == second
    assert first is not second


def test_decoded_instruction_is_immutable() -> None:
    decoded = decode_instruction(0x6ABC)

    with pytest.raises(FrozenInstanceError):
        decoded.operand = 0x000  # type: ignore[misc]


@pytest.mark.parametrize("invalid", [-1, 0x10000, True, False, "0xFFFF", None])
def test_decode_rejects_values_outside_sixteen_bits(invalid: object) -> None:
    with pytest.raises(InvalidComponentValue, match="instruction.*0x0..FFFF"):
        decode_instruction(invalid)


def test_decode_does_not_validate_instruction_specific_operand_semantics() -> None:
    decoded = decode_instruction(0x1ABC)

    assert decoded.opcode is Opcode.LDI
    assert decoded.operand == 0xABC
