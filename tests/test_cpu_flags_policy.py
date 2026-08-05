from dataclasses import FrozenInstanceError

import pytest

from cpu import (
    AddResult,
    ALUResult,
    Flag,
    FlagsDefinedMask,
    FlagsSnapshot,
    FlagValues,
    InvalidComponentValue,
    latch_flags_for_alu_write,
    latch_flags_for_non_alu_write,
    preserve_flags,
)


@pytest.mark.parametrize(
    "alu_result",
    [
        ALUResult(result=0x00, zero=True, carry=False, sign=False, overflow=False),
        ALUResult(result=0x00, zero=True, carry=True, sign=False, overflow=True),
        ALUResult(result=0x7F, zero=False, carry=False, sign=False, overflow=False),
        ALUResult(result=0x80, zero=False, carry=False, sign=True, overflow=True),
        ALUResult(result=0xFF, zero=False, carry=True, sign=True, overflow=False),
    ],
)
def test_alu_write_produces_concrete_all_defined_snapshot(alu_result: ALUResult) -> None:
    snapshot = latch_flags_for_alu_write(alu_result)

    assert snapshot.values == FlagValues(
        zero=alu_result.result == 0x00,
        carry=alu_result.carry,
        sign=bool(alu_result.result & 0x80),
        overflow=alu_result.overflow,
    )
    assert snapshot.defined == FlagsDefinedMask.all()


def test_alu_write_derives_zero_and_sign_from_result_byte() -> None:
    inconsistent = ALUResult(result=0x80, zero=False, carry=True, sign=False, overflow=True)

    snapshot = latch_flags_for_alu_write(inconsistent)

    assert snapshot.values.zero is False
    assert snapshot.values.sign is True
    assert snapshot.values.carry is True
    assert snapshot.values.overflow is True


def test_alu_write_does_not_mutate_input_result() -> None:
    alu_result = ALUResult(result=0x80, zero=False, carry=True, sign=True, overflow=False)

    snapshot = latch_flags_for_alu_write(alu_result)

    assert alu_result == ALUResult(result=0x80, zero=False, carry=True, sign=True, overflow=False)
    with pytest.raises(FrozenInstanceError):
        snapshot.values.zero = True  # type: ignore[misc]


@pytest.mark.parametrize(
    ("a_value", "expected_zero", "expected_sign"),
    [
        (0x00, True, False),
        (0x01, False, False),
        (0x7F, False, False),
        (0x80, False, True),
        (0xFF, False, True),
    ],
)
@pytest.mark.parametrize("alu_carry", [False, True])
@pytest.mark.parametrize("alu_overflow", [False, True])
def test_non_alu_write_derives_zero_sign_and_concrete_alu_flags(
    a_value: int,
    expected_zero: bool,
    expected_sign: bool,
    alu_carry: bool,
    alu_overflow: bool,
) -> None:
    snapshot = latch_flags_for_non_alu_write(
        a_value,
        alu_carry=alu_carry,
        alu_overflow=alu_overflow,
    )

    assert snapshot.values == FlagValues(
        zero=expected_zero,
        carry=alu_carry,
        sign=expected_sign,
        overflow=alu_overflow,
    )
    assert snapshot.defined == FlagsDefinedMask.zero_and_sign()
    assert snapshot.defined.is_defined(Flag.ZERO)
    assert snapshot.defined.is_defined(Flag.SIGN)


def test_non_alu_write_keeps_concrete_undefined_carry_and_overflow() -> None:
    snapshot = latch_flags_for_non_alu_write(0x80, alu_carry=True, alu_overflow=True)

    assert snapshot.values.carry is True
    assert snapshot.values.overflow is True
    assert snapshot.defined.is_defined(Flag.ZERO)
    assert snapshot.defined.is_defined(Flag.SIGN)
    assert snapshot.defined.none_defined is False
    assert snapshot.defined.all_defined is False


@pytest.mark.parametrize(
    "snapshot",
    [
        FlagsSnapshot.reset(),
        FlagsSnapshot(FlagValues(True, False, True, True), FlagsDefinedMask.zero_and_sign()),
    ],
)
def test_preserve_returns_same_immutable_snapshot(snapshot: FlagsSnapshot) -> None:
    preserved = preserve_flags(snapshot)

    assert preserved is snapshot
    assert preserved == snapshot


def test_reset_policy_uses_canonical_snapshot() -> None:
    reset = FlagsSnapshot.reset()
    changed = latch_flags_for_non_alu_write(0xFF, alu_carry=True, alu_overflow=True)

    assert reset == FlagsSnapshot.reset()
    assert reset != changed
    assert reset.values == FlagValues(False, False, False, False)
    assert reset.defined == FlagsDefinedMask.all()


@pytest.mark.parametrize("invalid", [-1, 0x100, True, False, "0x80", None])
def test_non_alu_write_rejects_invalid_a_value(invalid: object) -> None:
    with pytest.raises(InvalidComponentValue):
        latch_flags_for_non_alu_write(invalid, alu_carry=False, alu_overflow=False)


@pytest.mark.parametrize("name", ["alu_carry", "alu_overflow"])
@pytest.mark.parametrize("invalid", [0, 1, "true", None])
def test_non_alu_write_rejects_non_bool_alu_outputs(name: str, invalid: object) -> None:
    with pytest.raises(TypeError, match=f"{name} must be a bool"):
        if name == "alu_carry":
            latch_flags_for_non_alu_write(0x80, alu_carry=invalid, alu_overflow=False)
        else:
            latch_flags_for_non_alu_write(0x80, alu_carry=False, alu_overflow=invalid)


@pytest.mark.parametrize(
    "invalid",
    [None, AddResult(0, True, False, False, False), (0, False, False, False, False), {}],
)
def test_alu_write_rejects_non_unified_result_types(invalid: object) -> None:
    with pytest.raises(TypeError, match="alu_result must be an ALUResult"):
        latch_flags_for_alu_write(invalid)


@pytest.mark.parametrize("invalid", [None, "snapshot", object()])
def test_preserve_rejects_invalid_snapshot(invalid: object) -> None:
    with pytest.raises(TypeError, match="snapshot must be a FlagsSnapshot"):
        preserve_flags(invalid)


def test_validation_order_checks_a_value_before_non_alu_outputs() -> None:
    with pytest.raises(InvalidComponentValue):
        latch_flags_for_non_alu_write(-1, alu_carry=0, alu_overflow=0)


def test_validation_order_checks_result_type_before_result_fields() -> None:
    with pytest.raises(TypeError, match="alu_result must be an ALUResult"):
        latch_flags_for_alu_write(None)


def test_policy_is_stateless_across_full_partial_failed_and_preserved_calls() -> None:
    full = latch_flags_for_alu_write(
        ALUResult(result=0x7F, zero=False, carry=True, sign=False, overflow=False)
    )
    partial = latch_flags_for_non_alu_write(0x80, alu_carry=False, alu_overflow=True)

    with pytest.raises(InvalidComponentValue):
        latch_flags_for_non_alu_write(0x100, alu_carry=False, alu_overflow=False)

    assert full.defined == FlagsDefinedMask.all()
    assert partial.values == FlagValues(False, False, True, True)
    assert partial.defined == FlagsDefinedMask.zero_and_sign()
    assert preserve_flags(full) is full
