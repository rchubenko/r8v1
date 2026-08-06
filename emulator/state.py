"""Emulator-owned architectural state for R8 v1."""

from cpu import (
    SRAM,
    SRAM_SIZE,
    ALUMode,
    FixedWidthRegister,
    FlagsDefinedMask,
    FlagsSnapshot,
    HaltLatch,
    InstructionRegister,
    ProgramCounter,
    evaluate,
    latch_flags_for_alu_write,
    latch_flags_for_non_alu_write,
)

from .instruction import DecodedInstruction, Opcode, decode_instruction
from .snapshot import ArchitecturalStateSnapshot


class ArchitecturalState:
    """Persistent ISA state without execution orchestration or policy."""

    def __init__(self) -> None:
        self._a = FixedWidthRegister(width=8, reset_value=0x00)
        self._pc = ProgramCounter()
        self._ir = InstructionRegister()
        self._flags = FlagsSnapshot.reset()
        self._memory = SRAM()
        self._halt = HaltLatch()

    def reset(self) -> None:
        """Restore architectural state while preserving the SRAM contents."""

        self._a.reset()
        self._pc.reset()
        self._ir.reset()
        self._flags = FlagsSnapshot.reset()
        self._halt.reset()

    def load_image(self, image: object) -> None:
        """Atomically replace SRAM with one complete executable image."""

        self._memory.replace_image(image)

    def fetch_instruction(self) -> DecodedInstruction:
        """Fetch two instruction bytes and return the decoded IR value."""

        high = self._memory.read(self._pc.value)
        self._pc.increment()
        low = self._memory.read(self._pc.value)
        self._pc.increment()
        self._ir.load_high(high)
        self._ir.load_low(low)
        return decode_instruction((self._ir.high << 8) | self._ir.low)

    def execute_instruction(self, instruction: DecodedInstruction) -> None:
        """Execute the currently supported atomic ISA instructions."""

        if not isinstance(instruction, DecodedInstruction):
            raise TypeError(f"instruction must be a DecodedInstruction; got {instruction!r}")
        if instruction.opcode is Opcode.NOP:
            return
        if instruction.opcode is Opcode.LDI:
            self._a.load(instruction.operand & 0xFF)
            self._flags = latch_flags_for_non_alu_write(
                self._a.value,
                alu_carry=self._flags.values.carry,
                alu_overflow=self._flags.values.overflow,
            )
            return
        if instruction.opcode is Opcode.LDA:
            self._a.load(self._memory.read(instruction.operand))
            self._flags = latch_flags_for_non_alu_write(
                self._a.value,
                alu_carry=self._flags.values.carry,
                alu_overflow=self._flags.values.overflow,
            )
            return
        if instruction.opcode is Opcode.ADD:
            alu_result = evaluate(
                ALUMode.ADD,
                self._a.value,
                self._memory.read(instruction.operand),
            )
            self._a.load(alu_result.result)
            self._flags = latch_flags_for_alu_write(alu_result)
            return
        if instruction.opcode is Opcode.SUB:
            alu_result = evaluate(
                ALUMode.SUB,
                self._a.value,
                self._memory.read(instruction.operand),
            )
            self._a.load(alu_result.result)
            self._flags = latch_flags_for_alu_write(alu_result)
            return
        raise ValueError(f"unsupported opcode for execution: {instruction.opcode.value:#x}")

    def snapshot(self, *, include_memory: bool = False) -> ArchitecturalStateSnapshot:
        """Return an immutable architectural observation."""

        return ArchitecturalStateSnapshot(
            a=self.a,
            pc=self.pc,
            irh=self.irh,
            irl=self.irl,
            flags=self.flags,
            flags_defined_mask=self.flags_defined_mask,
            halt_state=self.halt_state,
            memory=self.memory_image if include_memory else None,
        )

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
