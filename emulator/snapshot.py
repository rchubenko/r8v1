"""Immutable architectural observations for R8 v1."""

from dataclasses import dataclass

from cpu import (
    SRAM_SIZE,
    FlagsDefinedMask,
    FlagsSnapshot,
    validate_address,
    validate_byte,
)


@dataclass(frozen=True, slots=True)
class ArchitecturalStateSnapshot:
    """Immutable architectural state with optional full SRAM observation."""

    a: int
    pc: int
    irh: int
    irl: int
    flags: FlagsSnapshot
    flags_defined_mask: FlagsDefinedMask
    halt_state: bool
    memory: bytes | None = None

    def __post_init__(self) -> None:
        validate_byte(self.a)
        validate_address(self.pc)
        validate_byte(self.irh)
        validate_byte(self.irl)
        if not isinstance(self.flags, FlagsSnapshot):
            raise TypeError(f"flags must be a FlagsSnapshot; got {self.flags!r}")
        if not isinstance(self.flags_defined_mask, FlagsDefinedMask):
            raise TypeError(
                f"flags_defined_mask must be a FlagsDefinedMask; got {self.flags_defined_mask!r}"
            )
        if type(self.halt_state) is not bool:
            raise TypeError(f"halt_state must be a bool; got {self.halt_state!r}")
        if self.memory is not None:
            if not isinstance(self.memory, bytes):
                raise TypeError(f"memory must be bytes or None; got {self.memory!r}")
            if len(self.memory) != SRAM_SIZE:
                raise ValueError(
                    f"memory must contain exactly {SRAM_SIZE} bytes; got {len(self.memory)}"
                )
