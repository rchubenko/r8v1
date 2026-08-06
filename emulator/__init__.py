"""Typed ISA decode values for the R8 v1 reference emulator."""

from .instruction import DecodedInstruction, Opcode, decode_instruction
from .policy import (
    ConditionalFlagResolution,
    Diagnostic,
    DiagnosticIdentifier,
    DiagnosticSeverity,
    ExecutionPolicy,
    resolve_conditional_flag,
)
from .snapshot import ArchitecturalStateSnapshot
from .state import ArchitecturalState

__all__ = [
    "ArchitecturalState",
    "ArchitecturalStateSnapshot",
    "DecodedInstruction",
    "ConditionalFlagResolution",
    "Diagnostic",
    "DiagnosticIdentifier",
    "DiagnosticSeverity",
    "ExecutionPolicy",
    "Opcode",
    "decode_instruction",
    "resolve_conditional_flag",
]
