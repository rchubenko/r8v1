"""Program Counter model for R8 v1."""

from .register import FixedWidthRegister
from .values import ADDRESS_MASK


class ProgramCounter(FixedWidthRegister):
    """A fixed 12-bit byte-addressed program counter."""

    def __init__(self) -> None:
        super().__init__(width=12, reset_value=0x000)

    def increment(self) -> None:
        """Advance by one byte with modulo-4096 wraparound."""

        self._value = (self.value + 1) & ADDRESS_MASK
