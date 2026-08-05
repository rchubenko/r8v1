"""Unified 4 KiB software SRAM model for R8 v1."""

from typing import Final

from .values import ADDRESS_BITS, validate_address, validate_byte

SRAM_SIZE: Final = 1 << ADDRESS_BITS


class InvalidMemoryImage(ValueError):
    """Raised when a full SRAM image violates the software image contract."""


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

    def replace_image(self, image: object) -> None:
        """Atomically replace storage with an independent complete SRAM image."""

        if not isinstance(image, (bytes, bytearray)):
            raise TypeError(f"image must be bytes or bytearray; got {image!r}")
        if len(image) != SRAM_SIZE:
            raise InvalidMemoryImage(
                f"image must contain exactly {SRAM_SIZE} bytes; got {len(image)}"
            )

        replacement = bytearray(image)
        self._storage = replacement
