from dataclasses import FrozenInstanceError
from enum import Enum

import pytest

from cpu import (
    AddResult,
    ALUMode,
    ALUResult,
    InvalidComponentValue,
    add,
    evaluate,
    subtract,
)


def test_alu_mode_contains_only_add_and_sub() -> None:
    assert list(ALUMode) == [ALUMode.ADD, ALUMode.SUB]
    assert ALUMode.ADD.value == "add"
    assert ALUMode.SUB.value == "sub"


@pytest.mark.parametrize(
    ("a", "b"),
    [(0x00, 0x00), (0x7F, 0x01), (0xFF, 0x01), (0x80, 0x80)],
)
def test_add_dispatch_matches_existing_implementation(a: int, b: int) -> None:
    expected = add(a, b)

    assert evaluate(ALUMode.ADD, a, b) == ALUResult(
        result=expected.result,
        zero=expected.zero,
        carry=expected.carry,
        sign=expected.sign,
        overflow=expected.overflow,
    )


@pytest.mark.parametrize(
    ("a", "b"),
    [(0x00, 0x01), (0x80, 0x01), (0x7F, 0xFF), (0x01, 0x01)],
)
def test_sub_dispatch_matches_existing_implementation(a: int, b: int) -> None:
    expected = subtract(a, b)

    assert evaluate(ALUMode.SUB, a, b) == ALUResult(
        result=expected.result,
        zero=expected.zero,
        carry=expected.carry,
        sign=expected.sign,
        overflow=expected.overflow,
    )


@pytest.mark.parametrize("invalid_mode", [0, 1, 2, True, "add", None, AddResult])
def test_raw_or_invalid_mode_is_rejected(invalid_mode: object) -> None:
    with pytest.raises(TypeError, match="mode must be an ALUMode"):
        evaluate(invalid_mode, 0x00, 0x00)  # type: ignore[arg-type]


@pytest.mark.parametrize("invalid", [-1, 0x100, True, False, "0x12", None])
def test_invalid_first_operand_matches_existing_validation(invalid: object) -> None:
    with pytest.raises(InvalidComponentValue):
        evaluate(ALUMode.ADD, invalid, 0x00)

    with pytest.raises(InvalidComponentValue):
        evaluate(ALUMode.SUB, invalid, 0x00)


@pytest.mark.parametrize("invalid", [-1, 0x100, True, False, "0x12", None])
def test_invalid_second_operand_matches_existing_validation(invalid: object) -> None:
    with pytest.raises(InvalidComponentValue):
        evaluate(ALUMode.ADD, 0x00, invalid)

    with pytest.raises(InvalidComponentValue):
        evaluate(ALUMode.SUB, 0x00, invalid)


def test_evaluate_always_returns_unified_immutable_result() -> None:
    add_result = evaluate(ALUMode.ADD, 0x7F, 0x01)
    sub_result = evaluate(ALUMode.SUB, 0x80, 0x01)

    assert type(add_result) is ALUResult
    assert type(sub_result) is ALUResult
    assert add_result == ALUResult(result=0x80, zero=False, carry=False, sign=True, overflow=True)
    assert sub_result == ALUResult(result=0x7F, zero=False, carry=True, sign=False, overflow=True)

    with pytest.raises(FrozenInstanceError):
        add_result.result = 0x00  # type: ignore[misc]


def test_unified_result_contract_matches_legacy_result_fields() -> None:
    add_result = evaluate(ALUMode.ADD, 0x12, 0x34)
    legacy_add = add(0x12, 0x34)
    sub_result = evaluate(ALUMode.SUB, 0x80, 0x01)
    legacy_sub = subtract(0x80, 0x01)

    assert add_result == ALUResult(
        result=legacy_add.result,
        zero=legacy_add.zero,
        carry=legacy_add.carry,
        sign=legacy_add.sign,
        overflow=legacy_add.overflow,
    )
    assert sub_result == ALUResult(
        result=legacy_sub.result,
        zero=legacy_sub.zero,
        carry=legacy_sub.carry,
        sign=legacy_sub.sign,
        overflow=legacy_sub.overflow,
    )


def test_evaluate_is_stateless_across_modes() -> None:
    first = evaluate(ALUMode.ADD, 0x12, 0x34)
    second = evaluate(ALUMode.SUB, 0x00, 0x01)
    third = evaluate(ALUMode.ADD, 0xFF, 0x01)

    assert first.result == 0x46
    assert second.result == 0xFF
    assert third.result == 0x00
    assert first.result == 0x46


def test_alu_mode_is_an_enum_not_control_word_decoder() -> None:
    assert issubclass(ALUMode, Enum)
    assert not hasattr(ALUMode, "decode")
