from dataclasses import FrozenInstanceError

import pytest

from cpu import Flag, FlagsDefinedMask, FlagsSnapshot, FlagValues


def test_flag_enum_contains_only_four_symbolic_flags() -> None:
    assert list(Flag) == [Flag.ZERO, Flag.CARRY, Flag.SIGN, Flag.OVERFLOW]
    assert [flag.value for flag in Flag] == ["z", "c", "s", "o"]
    assert all(not isinstance(flag.value, int) for flag in Flag)


@pytest.mark.parametrize(
    "values",
    [
        (False, False, False, False),
        (True, False, False, False),
        (False, True, False, False),
        (False, False, True, False),
        (False, False, False, True),
        (True, True, True, True),
    ],
)
def test_flag_values_store_all_concrete_fields(values: tuple[bool, bool, bool, bool]) -> None:
    flags = FlagValues(*values)

    assert (flags.zero, flags.carry, flags.sign, flags.overflow) == values


def test_flag_values_have_deterministic_equality() -> None:
    assert FlagValues(True, False, True, False) == FlagValues(True, False, True, False)
    assert FlagValues(True, False, True, False) != FlagValues(True, False, False, False)


def test_flag_values_are_immutable() -> None:
    flags = FlagValues(False, False, False, False)

    with pytest.raises(FrozenInstanceError):
        flags.zero = True  # type: ignore[misc]


@pytest.mark.parametrize("field", ["zero", "carry", "sign", "overflow"])
@pytest.mark.parametrize("invalid", [0, 1, "false", None])
def test_flag_values_reject_non_bool_fields(field: str, invalid: object) -> None:
    values: dict[str, object] = {
        "zero": False,
        "carry": False,
        "sign": False,
        "overflow": False,
    }
    values[field] = invalid

    with pytest.raises(TypeError, match=f"{field} must be a bool"):
        FlagValues(**values)  # type: ignore[arg-type]


def test_flag_values_reset_is_zero_and_independent() -> None:
    first = FlagValues.reset()
    second = FlagValues.reset()

    assert first == FlagValues(False, False, False, False)
    assert first == second
    assert first is not second


def test_all_defined_mask_defines_every_flag() -> None:
    mask = FlagsDefinedMask.all()

    assert mask.all_defined is True
    assert mask.none_defined is False
    assert all(mask.is_defined(flag) for flag in Flag)
    assert mask.defined_flags == frozenset(Flag)


def test_zero_and_sign_mask_defines_only_z_and_s() -> None:
    mask = FlagsDefinedMask.zero_and_sign()

    assert mask.is_defined(Flag.ZERO) is True
    assert mask.is_defined(Flag.SIGN) is True
    assert mask.is_defined(Flag.CARRY) is False
    assert mask.is_defined(Flag.OVERFLOW) is False
    assert mask == FlagsDefinedMask((Flag.ZERO, Flag.SIGN))


def test_none_defined_mask_has_no_defined_flags() -> None:
    mask = FlagsDefinedMask.none()

    assert mask.none_defined is True
    assert mask.all_defined is False
    assert mask.defined_flags == frozenset()
    assert all(mask.is_defined(flag) is False for flag in Flag)


@pytest.mark.parametrize("invalid", ["z", "zero", 0, 1, None, True])
def test_mask_lookup_rejects_invalid_flag(invalid: object) -> None:
    with pytest.raises(TypeError, match="flag must be a Flag"):
        FlagsDefinedMask.all().is_defined(invalid)  # type: ignore[arg-type]


@pytest.mark.parametrize("invalid", [["z"], [0], [None], [True]])
def test_mask_construction_rejects_invalid_members(invalid: list[object]) -> None:
    with pytest.raises(TypeError, match="flag must be a Flag"):
        FlagsDefinedMask(invalid)  # type: ignore[arg-type]


def test_mask_copies_mutable_input_and_exposes_immutable_flags() -> None:
    source = [Flag.ZERO]
    mask = FlagsDefinedMask(source)
    source.append(Flag.CARRY)

    assert mask.defined_flags == frozenset({Flag.ZERO})
    with pytest.raises(AttributeError):
        mask.defined_flags.add(Flag.CARRY)  # type: ignore[attr-defined]


def test_mask_is_immutable() -> None:
    mask = FlagsDefinedMask.zero_and_sign()

    with pytest.raises(FrozenInstanceError):
        mask._defined = frozenset()  # type: ignore[misc]


def test_flags_snapshot_reset_contains_zero_values_and_all_defined_mask() -> None:
    snapshot = FlagsSnapshot.reset()

    assert snapshot.values == FlagValues(False, False, False, False)
    assert snapshot.defined == FlagsDefinedMask.all()
    assert snapshot.defined.all_defined is True


def test_flags_snapshot_is_immutable_and_equal() -> None:
    values = FlagValues(True, False, True, False)
    defined = FlagsDefinedMask.zero_and_sign()
    first = FlagsSnapshot(values, defined)
    second = FlagsSnapshot(FlagValues(True, False, True, False), FlagsDefinedMask.zero_and_sign())

    assert first == second
    with pytest.raises(FrozenInstanceError):
        first.values = FlagValues.reset()  # type: ignore[misc]


@pytest.mark.parametrize("invalid", [None, (False, False, False, False), object()])
def test_flags_snapshot_rejects_invalid_values_object(invalid: object) -> None:
    with pytest.raises(TypeError, match="values must be a FlagValues"):
        FlagsSnapshot(invalid, FlagsDefinedMask.all())  # type: ignore[arg-type]


@pytest.mark.parametrize("invalid", [None, frozenset(), object()])
def test_flags_snapshot_rejects_invalid_mask_object(invalid: object) -> None:
    with pytest.raises(TypeError, match="defined must be a FlagsDefinedMask"):
        FlagsSnapshot(FlagValues.reset(), invalid)  # type: ignore[arg-type]
