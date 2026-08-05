"""Unified 4 KiB software SRAM model for R8 v1."""

from typing import Final

from .values import ADDRESS_BITS, validate_address, validate_byte

SRAM_SIZE: Final = 1 << ADDRESS_BITS


class SRAM:
    """A fixed-size, zero-filled, byte-addressable software SRAM."""

    def __init__(self) -> None:
        self._storage = bytearray(SRAM_SIZE)

    def read(self, address: object) -> int:
        """Read one byte from a validated 12-bit address."""

        address_value = validate_address(address)
        return self._storage[address_value]

    def write(self, address: object, value: object) -> None:
        """Validate address and byte, then write exactly one storage location."""

        address_value = validate_address(address)
        value_value = validate_byte(value)
        self._storage[address_value] = value_value
