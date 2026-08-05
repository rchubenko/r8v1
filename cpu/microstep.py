"""4-bit MICROSTEP counter model for R8 v1."""

from .register import FixedWidthRegister
from .values import NIBBLE_MASK


class MicrostepCounter(FixedWidthRegister):
    """A fixed 4-bit counter for states T0 through T15."""

    def __init__(self) -> None:
        super().__init__(width=4, reset_value=0x0)

    def increment(self) -> None:
        """Advance one microstep with modulo-16 wraparound."""

        self._value = (self.value + 1) & NIBBLE_MASK

    def return_to_t0(self) -> None:
        """Return this counter to T0 without resetting other components."""

        self._value = 0x0
