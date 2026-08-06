import pytest

from cpu import FlagsDefinedMask, FlagsSnapshot, FlagValues
from emulator import (
    ArchitecturalState,
    Diagnostic,
    DiagnosticIdentifier,
    DiagnosticSeverity,
    ExecutionPolicy,
    Opcode,
)


def _write_instruction(
    state: ArchitecturalState, address: int, opcode: Opcode, operand: int
) -> None:
    state._memory.write(address, (opcode.value << 4) | ((operand >> 8) & 0x0F))
    state._memory.write((address + 1) & 0xFFF, operand & 0xFF)


def _all_flags_true() -> FlagsSnapshot:
    return FlagsSnapshot(FlagValues(True, True, True, True), FlagsDefinedMask.all())


@pytest.mark.parametrize(
    ("opcode", "expected_diagnostic", "expected_halt", "expected_pc"),
    [
        (Opcode.NOP, None, False, 0x002),
        (Opcode.LDI, None, False, 0x002),
        (Opcode.LDA, None, False, 0x002),
        (Opcode.ADD, None, False, 0x002),
        (Opcode.SUB, None, False, 0x002),
        (Opcode.STA, None, False, 0x002),
        (Opcode.JMP, None, False, 0x123),
        (Opcode.JC, None, False, 0x123),
        (Opcode.JZ, None, False, 0x123),
        (Opcode.JN, None, False, 0x123),
        (Opcode.JV, None, False, 0x123),
        (Opcode.RESERVED_B, DiagnosticIdentifier.ILLEGAL_OPCODE, True, 0x002),
        (Opcode.RESERVED_C, DiagnosticIdentifier.ILLEGAL_OPCODE, True, 0x002),
        (Opcode.RESERVED_D, DiagnosticIdentifier.ILLEGAL_OPCODE, True, 0x002),
        (Opcode.RESERVED_E, DiagnosticIdentifier.ILLEGAL_OPCODE, True, 0x002),
        (Opcode.HLT, None, True, 0x002),
    ],
)
def test_step_dispatches_every_opcode(
    opcode: Opcode,
    expected_diagnostic: DiagnosticIdentifier | None,
    expected_halt: bool,
    expected_pc: int,
) -> None:
    state = ArchitecturalState()
    state._a.load(0x01)
    state._flags = _all_flags_true()
    state._memory.write(0x123, 0x01)
    _write_instruction(state, 0x000, opcode, 0x123)

    diagnostic = state.step(policy=ExecutionPolicy.HARDWARE_LIKE)

    assert state.pc == expected_pc
    assert (state.irh, state.irl) == ((opcode.value << 4) | 0x01, 0x23)
    assert state.halt_state is expected_halt
    if expected_diagnostic is None:
        assert diagnostic is None
    else:
        assert diagnostic == Diagnostic(
            expected_diagnostic,
            DiagnosticSeverity.ERROR,
            opcode,
        )


@pytest.mark.parametrize("opcode", [Opcode.JC, Opcode.JV])
@pytest.mark.parametrize("value", [False, True])
@pytest.mark.parametrize("policy", list(ExecutionPolicy))
def test_step_propagates_undefined_conditional_diagnostics(
    opcode: Opcode, value: bool, policy: ExecutionPolicy
) -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(
        FlagValues(False, value, False, value),
        FlagsDefinedMask.all(),
    )
    _write_instruction(state, 0x000, Opcode.LDI, 0x042)
    _write_instruction(state, 0x002, opcode, 0xABC)

    assert state.step() is None
    diagnostic = state.step(policy=policy)

    assert diagnostic is not None
    assert diagnostic.identifier is DiagnosticIdentifier.UNDEFINED_CONDITIONAL_FLAG
    assert diagnostic.severity is (
        DiagnosticSeverity.ERROR if policy is ExecutionPolicy.STRICT else DiagnosticSeverity.WARNING
    )
    assert state.pc == (0xABC if policy is ExecutionPolicy.HARDWARE_LIKE and value else 0x004)
    assert state.halt_state is False
    assert state.flags_defined_mask == FlagsDefinedMask.zero_and_sign()


@pytest.mark.parametrize("opcode", [Opcode.JC, Opcode.JV])
def test_step_requires_policy_before_conditional_branch_mutation(opcode: Opcode) -> None:
    state = ArchitecturalState()
    _write_instruction(state, 0x000, opcode, 0xABC)

    with pytest.raises(TypeError, match="policy is required"):
        state.step()

    assert state.pc == 0x002
    assert state.halt_state is False


@pytest.mark.parametrize("opcode", [Opcode.JC, Opcode.JV])
def test_step_uses_defined_conditional_flags_without_diagnostic(opcode: Opcode) -> None:
    state = ArchitecturalState()
    state._flags = _all_flags_true()
    _write_instruction(state, 0x000, opcode, 0xABC)

    diagnostic = state.step(policy=ExecutionPolicy.STRICT)

    assert diagnostic is None
    assert state.pc == 0xABC
    assert state.flags_defined_mask == FlagsDefinedMask.all()


def test_step_fetches_current_sram_after_self_modifying_sta() -> None:
    state = ArchitecturalState()
    _write_instruction(state, 0x000, Opcode.LDI, 0x060)
    _write_instruction(state, 0x002, Opcode.STA, 0x100)
    state._memory.write(0x100, 0x00)
    state._memory.write(0x101, 0x42)

    assert state.step() is None
    assert state.step() is None
    state._pc.load(0x100)

    assert state.step() is None
    assert state.opcode == Opcode.JMP.value
    assert state.operand == 0x042
    assert state.pc == 0x042


@pytest.mark.parametrize("start", [0xFFE, 0xFFF])
def test_step_fetches_across_sram_address_boundary(start: int) -> None:
    state = ArchitecturalState()
    state._pc.load(start)
    _write_instruction(state, start, Opcode.LDI, 0x042)

    assert state.step() is None
    assert state.a == 0x42
    assert state.pc == (0x000 if start == 0xFFE else 0x001)


@pytest.mark.parametrize("opcode", [Opcode.HLT, Opcode.RESERVED_B])
def test_halted_step_is_stable_and_does_not_repeat_diagnostic(opcode: Opcode) -> None:
    state = ArchitecturalState()
    _write_instruction(state, 0x000, opcode, 0x123)
    first = state.step()
    before = state.snapshot(include_memory=True)

    assert state.halt_state is True
    if opcode is Opcode.HLT:
        assert first is None
    else:
        assert first is not None
        assert first.identifier is DiagnosticIdentifier.ILLEGAL_OPCODE

    for _ in range(3):
        assert state.step() is None
        assert state.snapshot(include_memory=True) == before


def test_step_reset_resumes_from_zero_without_clearing_sram() -> None:
    state = ArchitecturalState()
    _write_instruction(state, 0x000, Opcode.HLT, 0x000)
    state._memory.write(0xABC, 0x5A)

    assert state.step() is None
    state._memory.write(0x000, 0x10)
    state._memory.write(0x001, 0x42)
    state.reset()

    assert state.step() is None
    assert state.a == 0x42
    assert state.pc == 0x002
    assert state._memory.read(0xABC) == 0x5A


@pytest.mark.parametrize(
    "opcode",
    [Opcode.NOP, Opcode.LDI, Opcode.ADD, Opcode.JMP, Opcode.JC, Opcode.HLT, Opcode.RESERVED_B],
)
def test_step_matches_direct_fetch_execute_composition(opcode: Opcode) -> None:
    stepped = ArchitecturalState()
    composed = ArchitecturalState()
    for state in (stepped, composed):
        state._a.load(0x01)
        state._flags = _all_flags_true()
        state._memory.write(0x123, 0x01)
        _write_instruction(state, 0x000, opcode, 0x123)

    policy = ExecutionPolicy.HARDWARE_LIKE
    stepped_diagnostic = stepped.step(policy=policy)
    fetched = composed.fetch_instruction()
    composed_diagnostic = composed.execute_instruction(fetched, policy=policy)

    assert stepped_diagnostic == composed_diagnostic
    assert stepped.snapshot(include_memory=True) == composed.snapshot(include_memory=True)
