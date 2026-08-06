from dataclasses import FrozenInstanceError, fields

import pytest

from cpu import FlagsDefinedMask, FlagsSnapshot, FlagValues
from emulator import (
    ArchitecturalState,
    ArchitecturalStateSnapshot,
    DecodedInstruction,
    DiagnosticIdentifier,
    DiagnosticSeverity,
    ExecutionPolicy,
    Opcode,
    StepResult,
)


def _write_instruction(
    state: ArchitecturalState, address: int, opcode: Opcode, operand: int
) -> None:
    state._memory.write(address, (opcode.value << 4) | ((operand >> 8) & 0x0F))
    state._memory.write((address + 1) & 0xFFF, operand & 0xFF)


def _state_with_instruction(opcode: Opcode, operand: int = 0x123) -> ArchitecturalState:
    state = ArchitecturalState()
    _write_instruction(state, 0x000, opcode, operand)
    return state


def test_step_result_is_immutable_typed_and_value_like() -> None:
    result = _state_with_instruction(Opcode.NOP).step()

    assert isinstance(result, StepResult)
    assert {field.name for field in fields(StepResult)} == {
        "instruction",
        "pre_state",
        "post_state",
        "diagnostic",
    }
    assert result == _state_with_instruction(Opcode.NOP).step()
    with pytest.raises(FrozenInstanceError):
        result.instruction = None  # type: ignore[misc]


def test_nop_result_captures_pre_and_post_architectural_observations() -> None:
    state = _state_with_instruction(Opcode.NOP)
    result = state.step()

    assert result.instruction == DecodedInstruction(Opcode.NOP, 0x123)
    assert result.pre_state.pc == 0x000
    assert result.pre_state.irh == 0x00
    assert result.post_state.pc == 0x002
    assert result.post_state.irh == 0x01
    assert result.post_state.irl == 0x23
    assert result.diagnostic is None


@pytest.mark.parametrize(
    ("opcode", "operand", "initial_a", "memory_value", "expected_a"),
    [
        (Opcode.LDI, 0x0A5, 0x00, 0x00, 0xA5),
        (Opcode.LDA, 0x100, 0x00, 0x5A, 0x5A),
        (Opcode.ADD, 0x100, 0x01, 0x02, 0x03),
        (Opcode.SUB, 0x100, 0x03, 0x01, 0x02),
        (Opcode.STA, 0x100, 0xA5, 0x00, 0xA5),
    ],
)
def test_data_and_arithmetic_results_capture_architectural_changes(
    opcode: Opcode,
    operand: int,
    initial_a: int,
    memory_value: int,
    expected_a: int,
) -> None:
    state = _state_with_instruction(opcode, operand)
    state._a.load(initial_a)
    state._memory.write(operand, memory_value)

    result = state.step(include_memory=True)

    assert result.instruction == DecodedInstruction(opcode, operand)
    assert result.pre_state.a == initial_a
    assert result.post_state.a == expected_a
    assert result.pre_state.pc == 0x000
    assert result.post_state.pc == 0x002
    assert result.diagnostic is None
    if opcode is Opcode.STA:
        assert result.pre_state.memory is not None
        assert result.post_state.memory is not None
        assert result.pre_state.memory[operand] == memory_value
        assert result.post_state.memory[operand] == expected_a


@pytest.mark.parametrize(
    ("opcode", "value", "target"),
    [
        (Opcode.JMP, True, 0xABC),
        (Opcode.JZ, True, 0xABC),
        (Opcode.JZ, False, 0x002),
        (Opcode.JN, True, 0xABC),
        (Opcode.JN, False, 0x002),
        (Opcode.JC, True, 0xABC),
        (Opcode.JC, False, 0x002),
        (Opcode.JV, True, 0xABC),
        (Opcode.JV, False, 0x002),
    ],
)
def test_branch_result_captures_final_pc(opcode: Opcode, value: bool, target: int) -> None:
    state = _state_with_instruction(opcode, 0xABC)
    state._flags = FlagsSnapshot(
        FlagValues(value, value, value, value),
        FlagsDefinedMask.all(),
    )

    result = state.step(policy=ExecutionPolicy.STRICT)

    assert result.instruction is not None
    assert result.instruction.opcode is opcode
    assert result.pre_state.pc == 0x000
    assert result.post_state.pc == target
    assert result.diagnostic is None


@pytest.mark.parametrize("opcode", [Opcode.JC, Opcode.JV])
@pytest.mark.parametrize("policy", list(ExecutionPolicy))
def test_undefined_conditional_result_contains_policy_diagnostic(
    opcode: Opcode, policy: ExecutionPolicy
) -> None:
    state = _state_with_instruction(opcode, 0xABC)
    state._flags = FlagsSnapshot(
        FlagValues(False, True, False, True),
        FlagsDefinedMask.zero_and_sign(),
    )

    result = state.step(policy=policy)

    assert result.instruction == DecodedInstruction(opcode, 0xABC)
    assert result.pre_state.pc == 0x000
    assert result.post_state.pc == (0xABC if policy is ExecutionPolicy.HARDWARE_LIKE else 0x002)
    assert result.post_state.halt_state is False
    assert result.post_state.flags_defined_mask == FlagsDefinedMask.zero_and_sign()
    assert result.diagnostic is not None
    assert result.diagnostic.identifier is DiagnosticIdentifier.UNDEFINED_CONDITIONAL_FLAG
    assert result.diagnostic.severity is (
        DiagnosticSeverity.ERROR if policy is ExecutionPolicy.STRICT else DiagnosticSeverity.WARNING
    )


@pytest.mark.parametrize("opcode", [Opcode.HLT, Opcode.RESERVED_B])
def test_halt_and_reserved_results_capture_halt_and_diagnostic(opcode: Opcode) -> None:
    result = _state_with_instruction(opcode).step()

    assert result.instruction == DecodedInstruction(opcode, 0x123)
    assert result.pre_state.halt_state is False
    assert result.post_state.halt_state is True
    assert result.post_state.pc == 0x002
    if opcode is Opcode.HLT:
        assert result.diagnostic is None
    else:
        assert result.diagnostic is not None
        assert result.diagnostic.identifier is DiagnosticIdentifier.ILLEGAL_OPCODE
        assert result.diagnostic.severity is DiagnosticSeverity.ERROR
        assert result.diagnostic.opcode is opcode


def test_already_halted_result_has_no_instruction_and_equal_states() -> None:
    state = _state_with_instruction(Opcode.HLT)
    state.step()

    result = state.step(include_memory=True)

    assert result.instruction is None
    assert result.pre_state == result.post_state
    assert result.pre_state.memory == result.post_state.memory
    assert result.diagnostic is None


def test_default_step_result_uses_lightweight_memory_snapshots() -> None:
    result = _state_with_instruction(Opcode.NOP).step()

    assert result.pre_state.memory is None
    assert result.post_state.memory is None


def test_boundary_result_captures_wrapped_fetch() -> None:
    state = ArchitecturalState()
    state._pc.load(0xFFF)
    _write_instruction(state, 0xFFF, Opcode.LDI, 0x042)

    result = state.step()

    assert result.pre_state.pc == 0xFFF
    assert result.instruction == DecodedInstruction(Opcode.LDI, 0x042)
    assert result.post_state.pc == 0x001
    assert result.post_state.a == 0x42


def test_result_tracks_instruction_changed_by_self_modifying_code() -> None:
    state = ArchitecturalState()
    _write_instruction(state, 0x000, Opcode.LDI, 0x060)
    _write_instruction(state, 0x002, Opcode.STA, 0x100)
    state._memory.write(0x100, 0x00)
    state._memory.write(0x101, 0x42)

    state.step()
    state.step()
    state._pc.load(0x100)
    result = state.step()

    assert result.instruction == DecodedInstruction(Opcode.JMP, 0x042)
    assert result.post_state.pc == 0x042


def test_memory_capture_is_detached_from_later_sram_mutations() -> None:
    state = _state_with_instruction(Opcode.STA, 0x100)
    state._a.load(0xA5)
    result = state.step(include_memory=True)
    pre_memory = result.pre_state.memory
    post_memory = result.post_state.memory

    assert pre_memory is not None
    assert post_memory is not None
    assert pre_memory[0x100] == 0x00
    assert post_memory[0x100] == 0xA5

    state._memory.write(0x100, 0xFF)
    state.reset()

    assert result.pre_state.memory == pre_memory
    assert result.post_state.memory == post_memory
    assert result.post_state.memory[0x100] == 0xA5


def test_step_result_is_deterministic_for_equal_independent_states() -> None:
    first = _state_with_instruction(Opcode.LDI, 0x042)
    second = _state_with_instruction(Opcode.LDI, 0x042)

    assert first.step(include_memory=True) == second.step(include_memory=True)


def test_step_result_does_not_contain_policy_or_diagnostic_history() -> None:
    state = _state_with_instruction(Opcode.NOP)
    result = state.step(policy=ExecutionPolicy.HARDWARE_LIKE)

    assert not hasattr(result, "policy")
    assert not hasattr(result.pre_state, "diagnostic")
    assert not hasattr(result.post_state, "diagnostic")
    assert isinstance(result.pre_state, ArchitecturalStateSnapshot)


def test_old_result_remains_stable_after_reset_and_further_execution() -> None:
    state = _state_with_instruction(Opcode.LDI, 0x042)
    result = state.step(include_memory=True)
    before = result

    state.reset()
    _write_instruction(state, 0x000, Opcode.HLT, 0x000)
    state.step()

    assert result == before
    assert result.instruction == DecodedInstruction(Opcode.LDI, 0x042)
    assert result.post_state.a == 0x42
    assert result.post_state.halt_state is False
