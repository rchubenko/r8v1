"""Reusable component primitives for the R8 v1 CPU."""

from .mar import MemoryAddressRegister
from .register import FixedWidthRegister
from .values import (
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

__all__ = [
    "ADDRESS_BITS",
    "ADDRESS_MASK",
    "BYTE_BITS",
    "BYTE_MASK",
    "FixedWidthRegister",
    "MemoryAddressRegister",
    "NIBBLE_BITS",
    "NIBBLE_MASK",
    "InvalidComponentValue",
    "validate_address",
    "validate_byte",
    "validate_nibble",
]
