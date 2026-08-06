from dataclasses import dataclass

import pytest

from cpu import FlagsDefinedMask, FlagsSnapshot, FlagValues
from emulator import (
    ArchitecturalState,
    DecodedInstruction,
    DiagnosticIdentifier,
    DiagnosticSeverity,
    ExecutionPolicy,
    Opcode,
)


@dataclass(frozen=True, slots=True)
class ConformanceRow:
    opcode: Opcode
    category: str
    effects: tuple[str, ...]
    boundary: str


CONFORMANCE_MATRIX = (
    ConformanceRow(Opcode.NOP, "no-op", ("pc", "ir", "preserve"), "fetch-wrap"),
    ConformanceRow(Opcode.LDI, "data", ("a", "zs", "pc", "ir"), "immediate-low-byte"),
    ConformanceRow(Opcode.LDA, "data", ("a", "zs", "pc", "ir", "memory-read"), "full-address"),
    ConformanceRow(Opcode.ADD, "arithmetic", ("a", "all-flags", "pc", "ir"), "full-address"),
    ConformanceRow(Opcode.SUB, "arithmetic", ("a", "all-flags", "pc", "ir"), "full-address"),
    ConformanceRow(Opcode.STA, "memory-write", ("memory-write", "preserve-flags"), "edge-address"),
    ConformanceRow(Opcode.JMP, "branch", ("pc-target", "preserve"), "odd-target"),
    ConformanceRow(Opcode.JC, "conditional", ("pc-conditional", "diagnostic-policy"), "odd-target"),
    ConformanceRow(Opcode.JZ, "conditional", ("pc-conditional", "preserve"), "odd-target"),
    ConformanceRow(Opcode.JN, "conditional", ("pc-conditional", "preserve"), "odd-target"),
    ConformanceRow(Opcode.JV, "conditional", ("pc-conditional", "diagnostic-policy"), "odd-target"),
    ConformanceRow(Opcode.RESERVED_B, "reserved", ("halt", "illegal-diagnostic"), "reserved-row"),
    ConformanceRow(Opcode.RESERVED_C, "reserved", ("halt", "illegal-diagnostic"), "reserved-row"),
    ConformanceRow(Opcode.RESERVED_D, "reserved", ("halt", "illegal-diagnostic"), "reserved-row"),
    ConformanceRow(Opcode.RESERVED_E, "reserved", ("halt", "illegal-diagnostic"), "reserved-row"),
    ConformanceRow(Opcode.HLT, "halt", ("halt", "preserve"), "halt-row"),
)

ALL_OPCODE_VALUES = tuple(Opcode)
BRANCH_OPCODES = (Opcode.JMP, Opcode.JC, Opcode.JZ, Opcode.JN, Opcode.JV)
RESERVED_OPCODES = (Opcode.RESERVED_B, Opcode.RESERVED_C, Opcode.RESERVED_D, Opcode.RESERVED_E)


def _write_instruction(
    state: ArchitecturalState, address: int, opcode: Opcode, operand: int
) -> None:
    state._memory.write(address, (opcode.value << 4) | ((operand >> 8) & 0x0F))
    state._memory.write((address + 1) & 0xFFF, operand & 0xFF)


def _flags_all_true() -> FlagsSnapshot:
    return FlagsSnapshot(FlagValues(True, True, True, True), FlagsDefinedMask.all())


def test_conformance_manifest_covers_exactly_all_opcode_values_once() -> None:
    manifest_opcodes = tuple(row.opcode for row in CONFORMANCE_MATRIX)

    assert manifest_opcodes == ALL_OPCODE_VALUES
    assert len(manifest_opcodes) == 0x10
    assert len(set(manifest_opcodes)) == 0x10
    assert (
        tuple(row.opcode for row in CONFORMANCE_MATRIX if row.category == "reserved")
        == RESERVED_OPCODES
    )


@pytest.mark.parametrize("row", CONFORMANCE_MATRIX, ids=lambda row: row.opcode.name)
def test_each_opcode_has_public_step_result_contract(row: ConformanceRow) -> None:
    state = ArchitecturalState()
    state._a.load(0x55)
    state._flags = _flags_all_true()
    state._memory.write(0x123, 0xA6)
    _write_instruction(state, 0x000, row.opcode, 0x123)

    result = state.step(policy=ExecutionPolicy.HARDWARE_LIKE, include_memory=True)

    assert result.instruction == DecodedInstruction(row.opcode, 0x123)
    assert result.pre_state.pc == 0x000
    assert result.pre_state.irh == 0x00
    assert result.post_state.irh == (row.opcode.value << 4) | 0x01
    assert result.post_state.irl == 0x23
    assert result.post_state.pc == (0x123 if row.opcode in BRANCH_OPCODES else 0x002)
    assert result.pre_state.memory is not None
    assert result.post_state.memory is not None

    if row.opcode is Opcode.LDI:
        assert result.post_state.a == 0x23
        assert result.post_state.flags_defined_mask == FlagsDefinedMask.zero_and_sign()
    elif row.opcode is Opcode.LDA:
        assert result.post_state.a == 0xA6
        assert result.post_state.flags_defined_mask == FlagsDefinedMask.zero_and_sign()
    elif row.opcode is Opcode.ADD:
        assert result.post_state.a == 0xFB
        assert result.post_state.flags_defined_mask == FlagsDefinedMask.all()
    elif row.opcode is Opcode.SUB:
        assert result.post_state.a == 0xAF
        assert result.post_state.flags_defined_mask == FlagsDefinedMask.all()
    else:
        assert result.post_state.a == 0x55
        assert result.post_state.flags == result.pre_state.flags
        assert result.post_state.flags_defined_mask == result.pre_state.flags_defined_mask

    if row.opcode is Opcode.STA:
        assert result.post_state.memory[0x123] == 0x55
    else:
        assert result.post_state.memory == result.pre_state.memory

    if row.opcode in RESERVED_OPCODES:
        assert result.post_state.halt_state is True
        assert result.diagnostic is not None
        assert result.diagnostic.identifier is DiagnosticIdentifier.ILLEGAL_OPCODE
        assert result.diagnostic.severity is DiagnosticSeverity.ERROR
        assert result.diagnostic.opcode is row.opcode
    elif row.opcode is Opcode.HLT:
        assert result.post_state.halt_state is True
        assert result.diagnostic is None
    else:
        assert result.post_state.halt_state is False
        assert result.diagnostic is None


@pytest.mark.parametrize("opcode", ALL_OPCODE_VALUES, ids=lambda opcode: opcode.name)
@pytest.mark.parametrize("start", [0xFFE, 0xFFF])
def test_each_opcode_has_fetch_boundary_coverage(opcode: Opcode, start: int) -> None:
    state = ArchitecturalState()
    state._pc.load(start)
    state._a.load(0x55)
    state._flags = _flags_all_true()
    state._memory.write(0x123, 0xA6)
    _write_instruction(state, start, opcode, 0x123)

    result = state.step(policy=ExecutionPolicy.HARDWARE_LIKE)

    assert result.instruction == DecodedInstruction(opcode, 0x123)
    assert result.pre_state.pc == start
    assert result.post_state.pc == (
        0x123 if opcode in BRANCH_OPCODES else (0x000 if start == 0xFFE else 0x001)
    )


@pytest.mark.parametrize(
    ("value", "expected_a", "expected_zero", "expected_sign"),
    [
        (0x000, 0x00, True, False),
        (0x001, 0x01, False, False),
        (0x07F, 0x7F, False, False),
        (0x080, 0x80, False, True),
        (0x0FF, 0xFF, False, True),
        (0x100, 0x00, True, False),
        (0xABC, 0xBC, False, True),
        (0xFFF, 0xFF, False, True),
    ],
)
def test_ldi_conformance_matrix(
    value: int, expected_a: int, expected_zero: bool, expected_sign: bool
) -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(FlagValues(False, True, False, True), FlagsDefinedMask.all())
    _write_instruction(state, 0x000, Opcode.LDI, value)

    result = state.step()

    assert result.post_state.a == expected_a
    assert result.post_state.flags.values.zero is expected_zero
    assert result.post_state.flags.values.sign is expected_sign
    assert result.post_state.flags.values.carry is True
    assert result.post_state.flags.values.overflow is True
    assert result.post_state.flags_defined_mask == FlagsDefinedMask.zero_and_sign()


@pytest.mark.parametrize("address", [0x000, 0x001, 0x0FF, 0x100, 0xABC, 0xFFE, 0xFFF])
def test_lda_conformance_uses_current_full_address_memory(address: int) -> None:
    state = ArchitecturalState()
    state._memory.write(address, 0x80 if address & 1 else 0x42)
    _write_instruction(state, 0x000, Opcode.LDA, address)

    result = state.step()

    assert result.instruction == DecodedInstruction(Opcode.LDA, address)
    assert result.post_state.a == state._memory.read(address)
    assert result.post_state.flags_defined_mask == FlagsDefinedMask.zero_and_sign()
    assert result.diagnostic is None


@pytest.mark.parametrize(
    ("opcode", "a", "operand", "expected_a", "expected_flags"),
    [
        (Opcode.ADD, 0x00, 0x00, 0x00, FlagValues(True, False, False, False)),
        (Opcode.ADD, 0x01, 0x01, 0x02, FlagValues(False, False, False, False)),
        (Opcode.ADD, 0x7F, 0x01, 0x80, FlagValues(False, False, True, True)),
        (Opcode.ADD, 0x80, 0x80, 0x00, FlagValues(True, True, False, True)),
        (Opcode.ADD, 0xFF, 0x01, 0x00, FlagValues(True, True, False, False)),
        (Opcode.ADD, 0xFF, 0xFF, 0xFE, FlagValues(False, True, True, False)),
        (Opcode.SUB, 0x00, 0x00, 0x00, FlagValues(True, True, False, False)),
        (Opcode.SUB, 0x01, 0x01, 0x00, FlagValues(True, True, False, False)),
        (Opcode.SUB, 0x00, 0x01, 0xFF, FlagValues(False, False, True, False)),
        (Opcode.SUB, 0x80, 0x01, 0x7F, FlagValues(False, True, False, True)),
        (Opcode.SUB, 0x7F, 0xFF, 0x80, FlagValues(False, False, True, True)),
        (Opcode.SUB, 0xFF, 0x01, 0xFE, FlagValues(False, True, True, False)),
    ],
)
def test_arithmetic_conformance_representative_flags(
    opcode: Opcode,
    a: int,
    operand: int,
    expected_a: int,
    expected_flags: FlagValues,
) -> None:
    state = ArchitecturalState()
    state._a.load(a)
    state._memory.write(0xABC, operand)
    _write_instruction(state, 0x000, opcode, 0xABC)

    result = state.step()

    assert result.post_state.a == expected_a
    assert result.post_state.flags.values == expected_flags
    assert result.post_state.flags_defined_mask == FlagsDefinedMask.all()
    assert result.post_state.memory == result.pre_state.memory


@pytest.mark.parametrize("address", [0x000, 0xFFF])
def test_sta_conformance_changes_exactly_one_addressed_byte(address: int) -> None:
    state = ArchitecturalState()
    state._a.load(0xA5)
    state._memory.write(address, 0x11)
    state._memory.write((address + 1) & 0xFFF, 0x22)
    _write_instruction(state, 0x000, Opcode.STA, address)

    result = state.step(include_memory=True)

    assert result.post_state.memory is not None
    assert result.pre_state.memory is not None
    differences = [
        location
        for location, (before, after) in enumerate(
            zip(result.pre_state.memory, result.post_state.memory, strict=True)
        )
        if before != after
    ]
    assert differences == [address]
    assert result.post_state.flags == result.pre_state.flags
    assert result.post_state.flags_defined_mask == result.pre_state.flags_defined_mask


@pytest.mark.parametrize("target", [0x000, 0x001, 0x123, 0xABC, 0xFFF])
def test_jmp_conformance_accepts_full_and_odd_targets(target: int) -> None:
    state = ArchitecturalState()
    state._a.load(0xA5)
    state._flags = _flags_all_true()
    _write_instruction(state, 0x000, Opcode.JMP, target)

    result = state.step()

    assert result.post_state.pc == target
    assert result.post_state.a == result.pre_state.a
    assert result.post_state.flags == result.pre_state.flags
    assert result.post_state.flags_defined_mask == result.pre_state.flags_defined_mask


@pytest.mark.parametrize(
    ("opcode", "flag_value"),
    [(Opcode.JZ, "zero"), (Opcode.JN, "sign")],
)
@pytest.mark.parametrize("value", [False, True])
def test_defined_conditional_conformance_taken_and_not_taken(
    opcode: Opcode, flag_value: str, value: bool
) -> None:
    state = ArchitecturalState()
    values = FlagValues(
        value if flag_value == "zero" else False,
        False,
        value if flag_value == "sign" else False,
        False,
    )
    state._flags = FlagsSnapshot(values, FlagsDefinedMask.all())
    _write_instruction(state, 0x000, opcode, 0xABC)

    result = state.step()

    assert result.post_state.pc == (0xABC if value else 0x002)
    assert result.diagnostic is None
    assert result.post_state.flags == result.pre_state.flags


@pytest.mark.parametrize("opcode", [Opcode.JC, Opcode.JV])
@pytest.mark.parametrize("value", [False, True])
@pytest.mark.parametrize("policy", list(ExecutionPolicy))
def test_undefined_conditional_conformance_policy_matrix(
    opcode: Opcode, value: bool, policy: ExecutionPolicy
) -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(
        FlagValues(False, value, False, value),
        FlagsDefinedMask.all(),
    )
    _write_instruction(state, 0x000, Opcode.LDI, 0x042)
    _write_instruction(state, 0x002, opcode, 0xABC)

    first = state.step()
    result = state.step(policy=policy)

    assert first.diagnostic is None
    assert result.instruction == DecodedInstruction(opcode, 0xABC)
    assert result.post_state.flags_defined_mask == FlagsDefinedMask.zero_and_sign()
    assert result.post_state.halt_state is False
    assert result.diagnostic is not None
    assert result.diagnostic.identifier is DiagnosticIdentifier.UNDEFINED_CONDITIONAL_FLAG
    assert result.diagnostic.severity is (
        DiagnosticSeverity.ERROR if policy is ExecutionPolicy.STRICT else DiagnosticSeverity.WARNING
    )
    assert result.post_state.pc == (
        0xABC if policy is ExecutionPolicy.HARDWARE_LIKE and value else 0x004
    )


@pytest.mark.parametrize("opcode", RESERVED_OPCODES)
@pytest.mark.parametrize("operand", [0x000, 0xABC, 0xFFF])
def test_reserved_conformance_rows_halt_with_offending_opcode(opcode: Opcode, operand: int) -> None:
    state = ArchitecturalState()
    _write_instruction(state, 0x000, opcode, operand)

    result = state.step()
    halted = state.step()

    assert result.instruction == DecodedInstruction(opcode, operand)
    assert result.post_state.halt_state is True
    assert result.diagnostic is not None
    assert result.diagnostic.identifier is DiagnosticIdentifier.ILLEGAL_OPCODE
    assert result.diagnostic.severity is DiagnosticSeverity.ERROR
    assert result.diagnostic.opcode is opcode
    assert halted.instruction is None
    assert halted.diagnostic is None
    assert halted.pre_state == halted.post_state


def test_hlt_conformance_and_reset_resume_preserve_sram() -> None:
    state = ArchitecturalState()
    _write_instruction(state, 0x000, Opcode.HLT, 0x000)
    state._memory.write(0xABC, 0x5A)

    result = state.step()
    halted = state.step()
    state._memory.write(0x000, 0x10)
    state._memory.write(0x001, 0x42)
    state.reset()
    resumed = state.step()

    assert result.instruction == DecodedInstruction(Opcode.HLT, 0x000)
    assert result.post_state.halt_state is True
    assert result.diagnostic is None
    assert halted.instruction is None
    assert halted.pre_state == halted.post_state
    assert resumed.instruction == DecodedInstruction(Opcode.LDI, 0x042)
    assert resumed.post_state.halt_state is False
    assert resumed.post_state.a == 0x42
    assert state._memory.read(0xABC) == 0x5A


@pytest.mark.parametrize("opcode", ALL_OPCODE_VALUES)
def test_non_memory_instructions_preserve_sram(opcode: Opcode) -> None:
    state = ArchitecturalState()
    state._a.load(0x55)
    state._flags = _flags_all_true()
    state._memory.write(0x123, 0xA6)
    _write_instruction(state, 0x000, opcode, 0x123)

    result = state.step(policy=ExecutionPolicy.HARDWARE_LIKE, include_memory=True)

    assert result.post_state.memory is not None
    if opcode is Opcode.STA:
        assert result.post_state.memory != result.pre_state.memory
        assert result.post_state.memory[0x123] == 0x55
    else:
        assert result.post_state.memory == result.pre_state.memory


def test_strict_diagnostic_does_not_persist_after_reset() -> None:
    state = ArchitecturalState()
    _write_instruction(state, 0x000, Opcode.LDI, 0x042)
    _write_instruction(state, 0x002, Opcode.JC, 0xABC)
    _write_instruction(state, 0x004, Opcode.NOP, 0x000)

    state.step()
    diagnostic = state.step(policy=ExecutionPolicy.STRICT)
    state.reset()
    resumed = state.step()

    assert diagnostic.diagnostic is not None
    assert diagnostic.diagnostic.identifier is DiagnosticIdentifier.UNDEFINED_CONDITIONAL_FLAG
    assert diagnostic.post_state.halt_state is False
    assert resumed.instruction == DecodedInstruction(Opcode.LDI, 0x042)
    assert resumed.diagnostic is None
