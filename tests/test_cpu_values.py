from collections.abc import Callable

import pytest

from cpu import (
    ADDRESS_BITS,
    ADDRESS_MASK,
    BYTE_BITS,
    BYTE_MASK,
    NIBBLE_BITS,
    NIBBLE_MASK,
    InvalidComponentValue,
    validate_address,
    validate_byte,
    validate_nibble,
)


@pytest.mark.parametrize(
    ("bits", "mask", "expected_bits", "expected_mask"),
    [
        (NIBBLE_BITS, NIBBLE_MASK, 4, 0xF),
        (BYTE_BITS, BYTE_MASK, 8, 0xFF),
        (ADDRESS_BITS, ADDRESS_MASK, 12, 0xFFF),
    ],
)
def test_width_constants_have_approved_values(
    bits: int,
    mask: int,
    expected_bits: int,
    expected_mask: int,
) -> None:
    assert bits == expected_bits
    assert mask == expected_mask


@pytest.mark.parametrize("value", [0x0, 0x1, 0xF])
def test_validate_nibble_accepts_boundary_values(value: int) -> None:
    assert validate_nibble(value) == value


@pytest.mark.parametrize("value", [-1, 0x10, "1", None, True, False])
def test_validate_nibble_rejects_invalid_values(value: object) -> None:
    with pytest.raises(InvalidComponentValue, match="nibble.*0x0..F"):
        validate_nibble(value)


@pytest.mark.parametrize("value", [0x00, 0x01, 0x7F, 0x80, 0xFF])
def test_validate_byte_accepts_boundary_values(value: int) -> None:
    assert validate_byte(value) == value


@pytest.mark.parametrize("value", [-1, 0x100, "1", None, True, False])
def test_validate_byte_rejects_invalid_values(value: object) -> None:
    with pytest.raises(InvalidComponentValue, match="byte.*0x0..FF"):
        validate_byte(value)


@pytest.mark.parametrize("value", [0x000, 0x001, 0x7FF, 0xFFF])
def test_validate_address_accepts_boundary_values(value: int) -> None:
    assert validate_address(value) == value


@pytest.mark.parametrize("value", [-1, 0x1000, "1", None, True, False])
def test_validate_address_rejects_invalid_values(value: object) -> None:
    with pytest.raises(InvalidComponentValue, match="address.*0x0..FFF"):
        validate_address(value)


@pytest.mark.parametrize(
    ("validator", "value", "expected"),
    [
        (validate_nibble, 0xF, 0xF),
        (validate_byte, 0xFF, 0xFF),
        (validate_address, 0xFFF, 0xFFF),
    ],
)
def test_valid_values_are_returned_unchanged(
    validator: Callable[[object], int], value: int, expected: int
) -> None:
    assert validator(value) == expected


def test_error_message_includes_actual_value() -> None:
    with pytest.raises(InvalidComponentValue, match="0x100") as error:
        validate_byte(0x100)

    assert "byte" in str(error.value)
