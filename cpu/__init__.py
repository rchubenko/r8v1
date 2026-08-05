"""Reusable component primitives for the R8 v1 CPU."""

from .address import AddressSource, select_address
from .alu import ALUMode, ALUResult, evaluate
from .alu_add import AddResult, add
from .alu_sub import SubtractResult, subtract
from .data_bus import DataBusContention, resolve_data_bus
from .instruction_register import InstructionRegister
from .mar import MemoryAddressRegister
from .program_counter import ProgramCounter
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
    "AddResult",
    "AddressSource",
    "ALUMode",
    "ALUResult",
    "BYTE_BITS",
    "BYTE_MASK",
    "DataBusContention",
    "FixedWidthRegister",
    "InstructionRegister",
    "MemoryAddressRegister",
    "NIBBLE_BITS",
    "NIBBLE_MASK",
    "ProgramCounter",
    "SubtractResult",
    "InvalidComponentValue",
    "add",
    "evaluate",
    "resolve_data_bus",
    "select_address",
    "subtract",
    "validate_address",
    "validate_byte",
    "validate_nibble",
]
