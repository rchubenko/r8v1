"""Memory Address Register model for R8 v1."""

from .register import FixedWidthRegister


class MemoryAddressRegister(FixedWidthRegister):
    """A fixed 12-bit register with the architectural MAR reset value."""

    def __init__(self) -> None:
        super().__init__(width=12, reset_value=0x000)
