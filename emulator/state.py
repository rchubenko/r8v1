"""Emulator-owned architectural state for R8 v1."""

from cpu import (
    SRAM,
    SRAM_SIZE,
    ALUMode,
    FixedWidthRegister,
    Flag,
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
from .policy import (
    Diagnostic,
    DiagnosticIdentifier,
    DiagnosticSeverity,
    ExecutionPolicy,
    resolve_conditional_flag,
)
from .result import StepResult
from .snapshot import ArchitecturalStateSnapshot


class ArchitecturalState:
    """Persistent ISA state and the atomic ISA execution boundary."""

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

    def step(
        self,
        *,
        policy: ExecutionPolicy | None = None,
        include_memory: bool = False,
    ) -> StepResult:
        """Run one atomic transition and return detached pre/post observations."""

        pre_state = self.snapshot(include_memory=include_memory)
        if self.halt_state:
            return StepResult(None, pre_state, pre_state, None)
        instruction = self.fetch_instruction()
        diagnostic = self.execute_instruction(instruction, policy=policy)
        post_state = self.snapshot(include_memory=include_memory)
        return StepResult(instruction, pre_state, post_state, diagnostic)

    def execute_instruction(
        self,
        instruction: DecodedInstruction,
        *,
        policy: ExecutionPolicy | None = None,
    ) -> Diagnostic | None:
        """Dispatch one fetched instruction through its atomic ISA semantics."""

        if not isinstance(instruction, DecodedInstruction):
            raise TypeError(f"instruction must be a DecodedInstruction; got {instruction!r}")
        if instruction.opcode is Opcode.NOP:
            return None
        if instruction.opcode is Opcode.LDI:
            self._a.load(instruction.operand & 0xFF)
            self._flags = latch_flags_for_non_alu_write(
                self._a.value,
                alu_carry=self._flags.values.carry,
                alu_overflow=self._flags.values.overflow,
            )
            return None
        if instruction.opcode is Opcode.LDA:
            self._a.load(self._memory.read(instruction.operand))
            self._flags = latch_flags_for_non_alu_write(
                self._a.value,
                alu_carry=self._flags.values.carry,
                alu_overflow=self._flags.values.overflow,
            )
            return None
        if instruction.opcode is Opcode.ADD:
            alu_result = evaluate(
                ALUMode.ADD,
                self._a.value,
                self._memory.read(instruction.operand),
            )
            self._a.load(alu_result.result)
            self._flags = latch_flags_for_alu_write(alu_result)
            return None
        if instruction.opcode is Opcode.SUB:
            alu_result = evaluate(
                ALUMode.SUB,
                self._a.value,
                self._memory.read(instruction.operand),
            )
            self._a.load(alu_result.result)
            self._flags = latch_flags_for_alu_write(alu_result)
            return None
        if instruction.opcode is Opcode.STA:
            self._memory.write(instruction.operand, self._a.value)
            return None
        if instruction.opcode is Opcode.JMP:
            self._pc.load(instruction.operand)
            return None
        if instruction.opcode is Opcode.JZ:
            if self._flags.values.zero:
                self._pc.load(instruction.operand)
            return None
        if instruction.opcode is Opcode.JN:
            if self._flags.values.sign:
                self._pc.load(instruction.operand)
            return None
        if instruction.opcode is Opcode.HLT:
            self._halt.latch()
            return None
        if instruction.opcode in (
            Opcode.RESERVED_B,
            Opcode.RESERVED_C,
            Opcode.RESERVED_D,
            Opcode.RESERVED_E,
        ):
            self._halt.latch()
            return Diagnostic(
                identifier=DiagnosticIdentifier.ILLEGAL_OPCODE,
                severity=DiagnosticSeverity.ERROR,
                opcode=instruction.opcode,
            )
        if instruction.opcode in (Opcode.JC, Opcode.JV):
            if policy is None:
                raise TypeError("policy is required for JC and JV execution")
            flag = Flag.CARRY if instruction.opcode is Opcode.JC else Flag.OVERFLOW
            resolution = resolve_conditional_flag(flag, self._flags, policy)
            if resolution.branch_allowed and resolution.value:
                self._pc.load(instruction.operand)
            return resolution.diagnostic
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
