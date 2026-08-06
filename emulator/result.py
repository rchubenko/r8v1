"""Immutable observations returned by one ISA emulator step."""

from dataclasses import dataclass

from .instruction import DecodedInstruction
from .policy import Diagnostic
from .snapshot import ArchitecturalStateSnapshot


@dataclass(frozen=True, slots=True)
class StepResult:
    """Detached architectural observations for one atomic step."""

    instruction: DecodedInstruction | None
    pre_state: ArchitecturalStateSnapshot
    post_state: ArchitecturalStateSnapshot
    diagnostic: Diagnostic | None

    def __post_init__(self) -> None:
        if self.instruction is not None and not isinstance(self.instruction, DecodedInstruction):
            raise TypeError(
                f"instruction must be a DecodedInstruction or None; got {self.instruction!r}"
            )
        if not isinstance(self.pre_state, ArchitecturalStateSnapshot):
            raise TypeError(
                f"pre_state must be an ArchitecturalStateSnapshot; got {self.pre_state!r}"
            )
        if not isinstance(self.post_state, ArchitecturalStateSnapshot):
            raise TypeError(
                f"post_state must be an ArchitecturalStateSnapshot; got {self.post_state!r}"
            )
        if not isinstance(self.diagnostic, (Diagnostic, type(None))):
            raise TypeError(f"diagnostic must be a Diagnostic or None; got {self.diagnostic!r}")
