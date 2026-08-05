"""Stateless FLAGS write policy for R8 v1."""

from .alu import ALUResult
from .flags import FlagsDefinedMask, FlagsSnapshot, FlagValues
from .values import validate_byte


def _validate_bool(value: object, *, name: str) -> bool:
    if type(value) is not bool:
        raise TypeError(f"{name} must be a bool; got {value!r}")
    return value


def latch_flags_for_alu_write(alu_result: object) -> FlagsSnapshot:
    """Create a fully defined FLAGS snapshot from one unified ALU result."""

    if not isinstance(alu_result, ALUResult):
        raise TypeError(f"alu_result must be an ALUResult; got {alu_result!r}")

    result = validate_byte(alu_result.result)
    carry = _validate_bool(alu_result.carry, name="alu_result.carry")
    overflow = _validate_bool(alu_result.overflow, name="alu_result.overflow")
    return FlagsSnapshot(
        values=FlagValues(
            zero=result == 0x00,
            carry=carry,
            sign=bool(result & 0x80),
            overflow=overflow,
        ),
        defined=FlagsDefinedMask.all(),
    )


def latch_flags_for_non_alu_write(
    a_value: object,
    *,
    alu_carry: object,
    alu_overflow: object,
) -> FlagsSnapshot:
    """Create a partially defined FLAGS snapshot for a non-ALU A write."""

    value = validate_byte(a_value)
    carry = _validate_bool(alu_carry, name="alu_carry")
    overflow = _validate_bool(alu_overflow, name="alu_overflow")
    return FlagsSnapshot(
        values=FlagValues(
            zero=value == 0x00,
            carry=carry,
            sign=bool(value & 0x80),
            overflow=overflow,
        ),
        defined=FlagsDefinedMask.zero_and_sign(),
    )


def preserve_flags(snapshot: object) -> FlagsSnapshot:
    """Preserve an immutable FLAGS snapshot without recalculating it."""

    if not isinstance(snapshot, FlagsSnapshot):
        raise TypeError(f"snapshot must be a FlagsSnapshot; got {snapshot!r}")
    return snapshot
