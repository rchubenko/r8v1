from dataclasses import FrozenInstanceError

import pytest

from cpu import Flag, FlagsDefinedMask, FlagsSnapshot, FlagValues
from emulator import (
    ArchitecturalState,
    DecodedInstruction,
    Diagnostic,
    DiagnosticIdentifier,
    DiagnosticSeverity,
    ExecutionPolicy,
    Opcode,
)

RESERVED_OPCODES = [
    Opcode.RESERVED_B,
    Opcode.RESERVED_C,
    Opcode.RESERVED_D,
    Opcode.RESERVED_E,
]


def _fetch_reserved(state: ArchitecturalState, opcode: Opcode, operand: int) -> DecodedInstruction:
    state._memory.write(0x000, (opcode.value << 4) | ((operand >> 8) & 0x0F))
    state._memory.write(0x001, operand & 0xFF)
    fetched = state.fetch_instruction()
    assert fetched == DecodedInstruction(opcode, operand)
    return fetched


@pytest.mark.parametrize("opcode", RESERVED_OPCODES)
@pytest.mark.parametrize("operand", [0x000, 0x001, 0xABC, 0xFFF])
def test_each_reserved_opcode_halts_and_reports_the_fetched_opcode(
    opcode: Opcode, operand: int
) -> None:
    state = ArchitecturalState()
    fetched = _fetch_reserved(state, opcode, operand)

    diagnostic = state.execute_instruction(fetched)

    assert diagnostic == Diagnostic(
        identifier=DiagnosticIdentifier.ILLEGAL_OPCODE,
        severity=DiagnosticSeverity.ERROR,
        opcode=opcode,
    )
    assert state.halt_state is True
    assert state.pc == 0x002
    assert state.opcode == opcode.value
    assert state.operand == operand


@pytest.mark.parametrize("opcode", RESERVED_OPCODES)
def test_reserved_opcode_preserves_architectural_state_like_hlt(opcode: Opcode) -> None:
    state = ArchitecturalState()
    state._a.load(0xA5)
    state._flags = FlagsSnapshot(
        FlagValues(True, False, True, False),
        FlagsDefinedMask((Flag.ZERO, Flag.OVERFLOW)),
    )
    state._memory.write(0xABC, 0x5A)
    fetched = _fetch_reserved(state, opcode, 0xABC)
    before = state.snapshot(include_memory=True)

    diagnostic = state.execute_instruction(fetched)

    assert diagnostic is not None
    assert state.halt_state is True
    assert state.a == before.a
    assert state.pc == before.pc
    assert (state.irh, state.irl) == (before.irh, before.irl)
    assert state.flags == before.flags
    assert state.flags_defined_mask == before.flags_defined_mask
    assert state.memory_image == before.memory


def test_reserved_opcode_differs_from_hlt_only_by_ir_and_diagnostic() -> None:
    hlt_state = ArchitecturalState()
    reserved_state = ArchitecturalState()
    hlt = _fetch_reserved(hlt_state, Opcode.HLT, 0xABC)
    reserved = _fetch_reserved(reserved_state, Opcode.RESERVED_B, 0xABC)

    hlt_diagnostic = hlt_state.execute_instruction(hlt)
    reserved_diagnostic = reserved_state.execute_instruction(reserved)

    assert hlt_diagnostic is None
    assert reserved_diagnostic == Diagnostic(
        DiagnosticIdentifier.ILLEGAL_OPCODE,
        DiagnosticSeverity.ERROR,
        Opcode.RESERVED_B,
    )
    assert hlt_state.a == reserved_state.a
    assert hlt_state.pc == reserved_state.pc
    assert hlt_state.flags == reserved_state.flags
    assert hlt_state.flags_defined_mask == reserved_state.flags_defined_mask
    assert hlt_state.memory_image[2:] == reserved_state.memory_image[2:]
    assert hlt_state.halt_state is reserved_state.halt_state is True


@pytest.mark.parametrize("policy", [None, ExecutionPolicy.STRICT, ExecutionPolicy.HARDWARE_LIKE])
def test_reserved_opcode_is_policy_independent(policy: ExecutionPolicy | None) -> None:
    state = ArchitecturalState()
    fetched = _fetch_reserved(state, Opcode.RESERVED_C, 0x123)

    diagnostic = state.execute_instruction(fetched, policy=policy)

    assert diagnostic is not None
    assert diagnostic.identifier is DiagnosticIdentifier.ILLEGAL_OPCODE
    assert diagnostic.severity is DiagnosticSeverity.ERROR
    assert diagnostic.opcode is Opcode.RESERVED_C
    assert state.halt_state is True


@pytest.mark.parametrize("opcode", RESERVED_OPCODES)
def test_reserved_opcode_halted_steps_do_not_repeat_diagnostic_or_fetch(opcode: Opcode) -> None:
    state = ArchitecturalState()
    fetched = _fetch_reserved(state, opcode, 0x123)
    first = state.execute_instruction(fetched)
    before = state.snapshot(include_memory=True)

    assert first is not None
    assert state.step().diagnostic is None
    assert state.step().diagnostic is None
    assert state.snapshot(include_memory=True) == before


def test_reserved_opcode_reset_clears_halt_and_execution_resumes() -> None:
    state = ArchitecturalState()
    state._memory.write(0x000, 0xB0)
    state._memory.write(0x001, 0x00)
    state._memory.write(0xABC, 0x5A)

    first = state.step()
    assert first.diagnostic is not None
    assert first.diagnostic.identifier is DiagnosticIdentifier.ILLEGAL_OPCODE

    state._memory.write(0x000, 0x10)
    state._memory.write(0x001, 0x42)
    state.reset()

    assert state.halt_state is False
    assert state._memory.read(0xABC) == 0x5A
    assert state.step().diagnostic is None
    assert state.a == 0x42


@pytest.mark.parametrize("opcode", RESERVED_OPCODES)
def test_reserved_opcode_fetched_across_boundary_halts_after_post_fetch_pc(opcode: Opcode) -> None:
    state = ArchitecturalState()
    state._pc.load(0xFFF)
    state._memory.write(0xFFF, opcode.value << 4)
    state._memory.write(0x000, 0x23)

    fetched = state.fetch_instruction()
    assert fetched == DecodedInstruction(opcode, 0x023)
    assert state.pc == 0x001

    diagnostic = state.execute_instruction(fetched)

    assert diagnostic is not None
    assert diagnostic.identifier is DiagnosticIdentifier.ILLEGAL_OPCODE
    assert state.pc == 0x001
    assert state.halt_state is True


def test_illegal_opcode_diagnostic_is_immutable_and_typed() -> None:
    state = ArchitecturalState()
    diagnostic = state.execute_instruction(_fetch_reserved(state, Opcode.RESERVED_D, 0xFFF))

    assert diagnostic is not None
    assert diagnostic.opcode is Opcode.RESERVED_D
    assert isinstance(diagnostic.identifier, DiagnosticIdentifier)
    assert isinstance(diagnostic.severity, DiagnosticSeverity)
    with pytest.raises(FrozenInstanceError):
        diagnostic.opcode = Opcode.RESERVED_E  # type: ignore[misc]
