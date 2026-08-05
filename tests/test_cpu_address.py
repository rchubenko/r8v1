from enum import Enum

import pytest

from cpu import AddressSource, InvalidComponentValue, select_address


def test_address_source_contains_only_pc_and_ir_operand() -> None:
    assert list(AddressSource) == [AddressSource.PC, AddressSource.IR_OPERAND]
    assert AddressSource.PC.value == "pc"
    assert AddressSource.IR_OPERAND.value == "ir_operand"
    assert all(not isinstance(source.value, int) for source in AddressSource)
    assert issubclass(AddressSource, Enum)


@pytest.mark.parametrize(
    ("pc", "ir_operand", "expected"),
    [
        (0x000, 0xFFF, 0x000),
        (0x001, 0xABC, 0x001),
        (0x7FF, 0x800, 0x7FF),
        (0xFFF, 0x000, 0xFFF),
    ],
)
def test_pc_source_returns_exact_pc_value(pc: int, ir_operand: int, expected: int) -> None:
    assert select_address(AddressSource.PC, pc=pc, ir_operand=ir_operand) == expected


@pytest.mark.parametrize(
    ("pc", "ir_operand", "expected"),
    [
        (0xFFF, 0x000, 0x000),
        (0xABC, 0x001, 0x001),
        (0x800, 0x7FF, 0x7FF),
        (0x000, 0xFFF, 0xFFF),
    ],
)
def test_ir_operand_source_returns_exact_operand_value(
    pc: int, ir_operand: int, expected: int
) -> None:
    assert select_address(AddressSource.IR_OPERAND, pc=pc, ir_operand=ir_operand) == expected


@pytest.mark.parametrize("invalid_source", [0, 1, "pc", "ir_operand", True, None])
def test_invalid_source_is_rejected_before_address_validation(invalid_source: object) -> None:
    with pytest.raises(TypeError, match="source must be an AddressSource"):
        select_address(invalid_source, pc=0x1000, ir_operand=0x1000)  # type: ignore[arg-type]


@pytest.mark.parametrize("invalid", [-1, 0x1000, True, False, "0xABC", None])
def test_invalid_pc_is_rejected(invalid: object) -> None:
    with pytest.raises(InvalidComponentValue):
        select_address(AddressSource.PC, pc=invalid, ir_operand=0x123)


@pytest.mark.parametrize("invalid", [-1, 0x1000, True, False, "0xABC", None])
def test_invalid_ir_operand_is_rejected(invalid: object) -> None:
    with pytest.raises(InvalidComponentValue):
        select_address(AddressSource.IR_OPERAND, pc=0x123, ir_operand=invalid)


def test_unselected_invalid_pc_is_still_rejected() -> None:
    with pytest.raises(InvalidComponentValue):
        select_address(AddressSource.IR_OPERAND, pc=0x1000, ir_operand=0x123)


def test_unselected_invalid_ir_operand_is_still_rejected() -> None:
    with pytest.raises(InvalidComponentValue):
        select_address(AddressSource.PC, pc=0x123, ir_operand=0x1000)


def test_validation_order_checks_source_then_both_candidates() -> None:
    with pytest.raises(TypeError, match="source must be an AddressSource"):
        select_address(0, pc=-1, ir_operand=0x1000)  # type: ignore[arg-type]

    with pytest.raises(InvalidComponentValue, match="address"):
        select_address(AddressSource.PC, pc=-1, ir_operand=0x1000)


def test_selector_does_not_mix_candidate_values() -> None:
    assert select_address(AddressSource.PC, pc=0x123, ir_operand=0x456) == 0x123
    assert select_address(AddressSource.IR_OPERAND, pc=0x123, ir_operand=0x456) == 0x456


def test_selector_is_stateless_across_valid_and_invalid_calls() -> None:
    assert select_address(AddressSource.PC, pc=0x123, ir_operand=0x456) == 0x123

    with pytest.raises(InvalidComponentValue):
        select_address(AddressSource.PC, pc=0x1000, ir_operand=0x456)

    assert select_address(AddressSource.IR_OPERAND, pc=0x123, ir_operand=0x456) == 0x456
    assert select_address(AddressSource.IR_OPERAND, pc=0x123, ir_operand=0x456) == 0x456
