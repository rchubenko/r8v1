"""Typed ISA decode values for the R8 v1 reference emulator."""

from .instruction import DecodedInstruction, Opcode, decode_instruction
from .state import ArchitecturalState

__all__ = ["ArchitecturalState", "DecodedInstruction", "Opcode", "decode_instruction"]
