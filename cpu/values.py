"""Fixed-width value validation used by R8 v1 component models."""

from typing import Final

NIBBLE_BITS: Final = 4
BYTE_BITS: Final = 8
ADDRESS_BITS: Final = 12

NIBBLE_MASK: Final = 0xF
BYTE_MASK: Final = 0xFF
ADDRESS_MASK: Final = 0xFFF


class InvalidComponentValue(ValueError):
    """Raised when a component receives a value outside its fixed-width range."""


def _validate(value: object, *, name: str, mask: int, maximum: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= mask:
        actual = (
            f"{value:#x}" if isinstance(value, int) and not isinstance(value, bool) else repr(value)
        )
        raise InvalidComponentValue(
            f"{name} must be an integer in range 0x0..{maximum}; got {actual}"
        )
    return value


def validate_nibble(value: object) -> int:
    """Validate and return a 4-bit value."""

    return _validate(value, name="nibble", mask=NIBBLE_MASK, maximum="F")


def validate_byte(value: object) -> int:
    """Validate and return an 8-bit value."""

    return _validate(value, name="byte", mask=BYTE_MASK, maximum="FF")


def validate_address(value: object) -> int:
    """Validate and return a 12-bit address value."""

    return _validate(value, name="address", mask=ADDRESS_MASK, maximum="FFF")
