"""Instruction Register model for R8 v1."""

from .register import FixedWidthRegister


class InstructionRegister:
    """Two independent 8-bit instruction bytes with derived views."""

    def __init__(self) -> None:
        self._high = FixedWidthRegister(width=8, reset_value=0x00)
        self._low = FixedWidthRegister(width=8, reset_value=0x00)

    @property
    def high(self) -> int:
        """Return the stored IRH byte."""

        return self._high.value

    @property
    def low(self) -> int:
        """Return the stored IRL byte."""

        return self._low.value

    @property
    def opcode(self) -> int:
        """Return IRH bits 7..4 as a 4-bit opcode value."""

        return (self.high >> 4) & 0xF

    @property
    def operand(self) -> int:
        """Return the 12-bit operand assembled from IRH and IRL."""

        return ((self.high & 0xF) << 8) | self.low

    def load_high(self, value: object) -> None:
        """Validate and load IRH without changing IRL."""

        self._high.load(value)

    def load_low(self, value: object) -> None:
        """Validate and load IRL without changing IRH."""

        self._low.load(value)

    def reset(self) -> None:
        """Reset both instruction bytes to zero."""

        self._high.reset()
        self._low.reset()
