"""Basic fixed-width register model for R8 v1 components."""

from collections.abc import Callable

from .values import (
    InvalidComponentValue,
    validate_address,
    validate_byte,
    validate_nibble,
)

_Validator = Callable[[object], int]
_WIDTH_VALIDATORS: dict[int, _Validator] = {
    4: validate_nibble,
    8: validate_byte,
    12: validate_address,
}


class FixedWidthRegister:
    """A stateful register supporting only the approved R8 v1 widths."""

    def __init__(self, width: object, reset_value: object) -> None:
        if isinstance(width, bool) or not isinstance(width, int) or width not in _WIDTH_VALIDATORS:
            raise InvalidComponentValue(f"register width must be one of 4, 8, 12; got {width!r}")

        self._width = width
        self._validator = _WIDTH_VALIDATORS[width]
        self._reset_value = self._validator(reset_value)
        self._value = self._reset_value

    @property
    def width(self) -> int:
        """Return the register width in bits."""

        return self._width

    @property
    def reset_value(self) -> int:
        """Return the configured value restored by reset."""

        return self._reset_value

    @property
    def value(self) -> int:
        """Return the current register value."""

        return self._value

    def load(self, value: object) -> None:
        """Validate and explicitly load a new value."""

        self._value = self._validator(value)

    def reset(self) -> None:
        """Restore the configured reset value."""

        self._value = self._reset_value
