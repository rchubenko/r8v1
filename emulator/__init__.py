"""Typed ISA decode values for the R8 v1 reference emulator."""

from .instruction import DecodedInstruction, Opcode, decode_instruction

__all__ = ["DecodedInstruction", "Opcode", "decode_instruction"]
