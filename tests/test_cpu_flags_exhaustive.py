from dataclasses import FrozenInstanceError

import pytest

from cpu import (
    ALUMode,
    ALUResult,
    Flag,
    FlagsDefinedMask,
    FlagsSnapshot,
    FlagValues,
    InvalidComponentValue,
    evaluate,
    latch_flags_for_alu_write,
    latch_flags_for_non_alu_write,
    preserve_flags,
)


def test_exhaustive_add_to_flags_policy() -> None:
    for a in range(0x100):
        for b in range(0x100):
            wide = a + b
            expected_result = wide & 0xFF
            expected_zero = expected_result == 0x00
            expected_carry = wide > 0xFF
            expected_sign = bool(expected_result & 0x80)
            expected_overflow = bool(((a ^ b) & 0x80) == 0 and ((a ^ expected_result) & 0x80) != 0)

            alu_result = evaluate(ALUMode.ADD, a, b)
            snapshot = latch_flags_for_alu_write(alu_result)

            assert alu_result.result == expected_result
            assert alu_result.zero is expected_zero
            assert alu_result.carry is expected_carry
            assert alu_result.sign is expected_sign
            assert alu_result.overflow is expected_overflow
            assert snapshot.values == FlagValues(
                zero=expected_zero,
                carry=expected_carry,
                sign=expected_sign,
                overflow=expected_overflow,
            )
            assert snapshot.defined == FlagsDefinedMask.all()


def test_exhaustive_sub_to_flags_policy() -> None:
    for a in range(0x100):
        for b in range(0x100):
            wide = a - b
            expected_result = wide & 0xFF
            expected_zero = expected_result == 0x00
            expected_carry = a >= b
            expected_sign = bool(expected_result & 0x80)
            expected_overflow = bool(((a ^ b) & 0x80) != 0 and ((a ^ expected_result) & 0x80) != 0)

            alu_result = evaluate(ALUMode.SUB, a, b)
            snapshot = latch_flags_for_alu_write(alu_result)

            assert alu_result.result == expected_result
            assert alu_result.zero is expected_zero
            assert alu_result.carry is expected_carry
            assert alu_result.sign is expected_sign
            assert alu_result.overflow is expected_overflow
            assert snapshot.values == FlagValues(
                zero=expected_zero,
                carry=expected_carry,
                sign=expected_sign,
                overflow=expected_overflow,
            )
            assert snapshot.defined == FlagsDefinedMask.all()


def test_exhaustive_non_alu_writes_preserve_concrete_alu_outputs() -> None:
    for value in range(0x100):
        expected_zero = value == 0x00
        expected_sign = bool(value & 0x80)
        for carry in (False, True):
            for overflow in (False, True):
                snapshot = latch_flags_for_non_alu_write(
                    value,
                    alu_carry=carry,
                    alu_overflow=overflow,
                )

                assert snapshot.values == FlagValues(
                    zero=expected_zero,
                    carry=carry,
                    sign=expected_sign,
                    overflow=overflow,
                )
                assert snapshot.defined == FlagsDefinedMask.zero_and_sign()
                assert snapshot.defined.is_defined(Flag.ZERO)
                assert snapshot.defined.is_defined(Flag.SIGN)
                assert not snapshot.defined.is_defined(Flag.CARRY)
                assert not snapshot.defined.is_defined(Flag.OVERFLOW)


@pytest.mark.parametrize(
    ("starting", "transition", "expected_mask"),
    [
        (FlagsSnapshot.reset(), "full", FlagsDefinedMask.all()),
        (FlagsSnapshot.reset(), "partial", FlagsDefinedMask.zero_and_sign()),
        (
            FlagsSnapshot(FlagValues(False, True, True, True), FlagsDefinedMask.zero_and_sign()),
            "full",
            FlagsDefinedMask.all(),
        ),
        (
            FlagsSnapshot(FlagValues(True, True, False, True), FlagsDefinedMask.all()),
            "partial",
            FlagsDefinedMask.zero_and_sign(),
        ),
    ],
)
def test_defined_mask_transitions_are_new_snapshot_states(
    starting: FlagsSnapshot,
    transition: str,
    expected_mask: FlagsDefinedMask,
) -> None:
    if transition == "full":
        result = latch_flags_for_alu_write(
            ALUResult(result=0x80, zero=False, carry=True, sign=True, overflow=True)
        )
    else:
        result = latch_flags_for_non_alu_write(0x00, alu_carry=True, alu_overflow=True)

    assert starting.defined != result.defined or starting.values != result.values
    assert result.defined == expected_mask


@pytest.mark.parametrize(
    "snapshot",
    [
        FlagsSnapshot.reset(),
        FlagsSnapshot(FlagValues(True, True, False, False), FlagsDefinedMask.all()),
        FlagsSnapshot(FlagValues(False, True, True, True), FlagsDefinedMask.zero_and_sign()),
        FlagsSnapshot(FlagValues(False, True, True, True), FlagsDefinedMask.none()),
    ],
)
def test_preserve_keeps_values_mask_and_identity(snapshot: FlagsSnapshot) -> None:
    first = preserve_flags(snapshot)
    second = preserve_flags(first)

    assert first is snapshot
    assert second is snapshot
    assert first.values == snapshot.values
    assert first.defined == snapshot.defined


def test_reset_is_canonical_after_full_and_partial_sequences() -> None:
    _ = latch_flags_for_alu_write(
        ALUResult(result=0xFF, zero=False, carry=True, sign=True, overflow=False)
    )
    _ = latch_flags_for_non_alu_write(0x80, alu_carry=True, alu_overflow=True)

    first = FlagsSnapshot.reset()
    second = FlagsSnapshot.reset()

    assert first == second
    assert first.values == FlagValues(False, False, False, False)
    assert first.defined == FlagsDefinedMask.all()
    with pytest.raises(FrozenInstanceError):
        first.values = FlagValues.reset()  # type: ignore[misc]


def test_validation_regression_for_policy_inputs() -> None:
    with pytest.raises(InvalidComponentValue):
        latch_flags_for_non_alu_write(True, alu_carry=False, alu_overflow=False)
    with pytest.raises(TypeError):
        latch_flags_for_non_alu_write(0x00, alu_carry=1, alu_overflow=False)
    with pytest.raises(TypeError):
        latch_flags_for_non_alu_write(0x00, alu_carry=False, alu_overflow=1)
    with pytest.raises(TypeError):
        latch_flags_for_alu_write((0, False, False, False, False))


def test_failed_policy_call_does_not_affect_following_valid_call() -> None:
    with pytest.raises(InvalidComponentValue):
        latch_flags_for_non_alu_write(0x100, alu_carry=False, alu_overflow=False)

    snapshot = latch_flags_for_non_alu_write(0x7F, alu_carry=True, alu_overflow=False)

    assert snapshot.values == FlagValues(False, True, False, False)
    assert snapshot.defined == FlagsDefinedMask.zero_and_sign()
