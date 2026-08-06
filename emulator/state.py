"""Emulator-owned architectural state for R8 v1."""

from cpu import (
    SRAM,
    SRAM_SIZE,
    FixedWidthRegister,
    FlagsDefinedMask,
    FlagsSnapshot,
    HaltLatch,
    InstructionRegister,
    ProgramCounter,
)


class ArchitecturalState:
    """Persistent ISA state without execution orchestration or policy."""

    def __init__(self) -> None:
        self._a = FixedWidthRegister(width=8, reset_value=0x00)
        self._pc = ProgramCounter()
        self._ir = InstructionRegister()
        self._flags = FlagsSnapshot.reset()
        self._memory = SRAM()
        self._halt = HaltLatch()

    @property
    def a(self) -> int:
        """Return the accumulator value."""

        return self._a.value

    @property
    def pc(self) -> int:
        """Return the 12-bit program counter value."""

        return self._pc.value

    @property
    def irh(self) -> int:
        """Return the high instruction byte."""

        return self._ir.high

    @property
    def irl(self) -> int:
        """Return the low instruction byte."""

        return self._ir.low

    @property
    def opcode(self) -> int:
        """Return the raw 4-bit opcode view supplied by the IR component."""

        return self._ir.opcode

    @property
    def operand(self) -> int:
        """Return the 12-bit operand view supplied by the IR component."""

        return self._ir.operand

    @property
    def flags(self) -> FlagsSnapshot:
        """Return the immutable concrete FLAGS snapshot."""

        return self._flags

    @property
    def flags_defined_mask(self) -> FlagsDefinedMask:
        """Return the immutable software-defined FLAGS mask."""

        return self._flags.defined

    @property
    def halt_state(self) -> bool:
        """Return whether HALT_STATE is latched."""

        return self._halt.is_halted

    @property
    def memory_image(self) -> bytes:
        """Return a detached read-only copy of the complete SRAM image."""

        return bytes(self._memory.read(address) for address in range(SRAM_SIZE))
