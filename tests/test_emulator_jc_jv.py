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


def _fetch_conditional(
    state: ArchitecturalState, opcode: Opcode, target: int
) -> DecodedInstruction:
    state._memory.write(0x000, (opcode.value << 4) | ((target >> 8) & 0x0F))
    state._memory.write(0x001, target & 0xFF)
    fetched = state.fetch_instruction()
    assert fetched == DecodedInstruction(opcode, target)
    return fetched


@pytest.mark.parametrize("opcode,flag", [(Opcode.JC, Flag.CARRY), (Opcode.JV, Flag.OVERFLOW)])
@pytest.mark.parametrize("value", [False, True])
@pytest.mark.parametrize("policy", list(ExecutionPolicy))
def test_defined_jc_and_jv_use_flag_value_without_diagnostic(
    opcode: Opcode, flag: Flag, value: bool, policy: ExecutionPolicy
) -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(
        FlagValues(
            False,
            value if flag is Flag.CARRY else False,
            False,
            value if flag is Flag.OVERFLOW else False,
        ),
        FlagsDefinedMask.all(),
    )
    fetched = _fetch_conditional(state, opcode, 0xABC)
    post_fetch_pc = state.pc

    diagnostic = state.execute_instruction(fetched, policy=policy)

    assert diagnostic is None
    assert state.pc == (0xABC if value else post_fetch_pc)


@pytest.mark.parametrize("opcode,flag", [(Opcode.JC, Flag.CARRY), (Opcode.JV, Flag.OVERFLOW)])
@pytest.mark.parametrize("value", [False, True])
def test_undefined_jc_and_jv_strict_reject_branch_for_both_concrete_values(
    opcode: Opcode, flag: Flag, value: bool
) -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(
        FlagValues(
            False,
            value if flag is Flag.CARRY else False,
            False,
            value if flag is Flag.OVERFLOW else False,
        ),
        FlagsDefinedMask.zero_and_sign(),
    )
    fetched = _fetch_conditional(state, opcode, 0xABC)
    before = state.snapshot(include_memory=True)
    post_fetch_pc = state.pc

    diagnostic = state.execute_instruction(fetched, policy=ExecutionPolicy.STRICT)

    assert diagnostic == Diagnostic(
        DiagnosticIdentifier.UNDEFINED_CONDITIONAL_FLAG,
        DiagnosticSeverity.ERROR,
    )
    assert state.pc == post_fetch_pc
    assert state.snapshot(include_memory=True).a == before.a
    assert state.flags == before.flags
    assert state.flags_defined_mask == before.flags_defined_mask
    assert state.halt_state is False


@pytest.mark.parametrize("opcode,flag", [(Opcode.JC, Flag.CARRY), (Opcode.JV, Flag.OVERFLOW)])
@pytest.mark.parametrize("value", [False, True])
def test_undefined_jc_and_jv_hardware_like_uses_concrete_value(
    opcode: Opcode, flag: Flag, value: bool
) -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(
        FlagValues(
            False,
            value if flag is Flag.CARRY else False,
            False,
            value if flag is Flag.OVERFLOW else False,
        ),
        FlagsDefinedMask.zero_and_sign(),
    )
    fetched = _fetch_conditional(state, opcode, 0xABC)
    post_fetch_pc = state.pc

    diagnostic = state.execute_instruction(fetched, policy=ExecutionPolicy.HARDWARE_LIKE)

    assert diagnostic == Diagnostic(
        DiagnosticIdentifier.UNDEFINED_CONDITIONAL_FLAG,
        DiagnosticSeverity.WARNING,
    )
    assert state.pc == (0xABC if value else post_fetch_pc)
    assert state.flags_defined_mask == FlagsDefinedMask.zero_and_sign()
    assert state.halt_state is False


@pytest.mark.parametrize("opcode", [Opcode.JC, Opcode.JV])
def test_conditional_c_or_o_requires_explicit_execution_policy(opcode: Opcode) -> None:
    state = ArchitecturalState()
    fetched = _fetch_conditional(state, opcode, 0x123)
    before = state.snapshot(include_memory=True)

    with pytest.raises(TypeError, match="policy is required"):
        state.execute_instruction(fetched)

    assert state.snapshot(include_memory=True) == before


@pytest.mark.parametrize("opcode,flag", [(Opcode.JC, Flag.CARRY), (Opcode.JV, Flag.OVERFLOW)])
@pytest.mark.parametrize("target", [0x000, 0x001, 0x123, 0xABC, 0xFFF])
def test_undefined_hardware_like_taken_paths_support_full_targets(
    opcode: Opcode, flag: Flag, target: int
) -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(
        FlagValues(False, flag is Flag.CARRY, False, flag is Flag.OVERFLOW),
        FlagsDefinedMask.zero_and_sign(),
    )
    fetched = _fetch_conditional(state, opcode, target)

    diagnostic = state.execute_instruction(fetched, policy=ExecutionPolicy.HARDWARE_LIKE)

    assert diagnostic is not None
    assert state.pc == target


@pytest.mark.parametrize("opcode,flag", [(Opcode.JC, Flag.CARRY), (Opcode.JV, Flag.OVERFLOW)])
def test_conditional_jump_boundary_fetch_preserves_post_fetch_pc_on_strict_error(
    opcode: Opcode, flag: Flag
) -> None:
    state = ArchitecturalState()
    state._pc.load(0xFFF)
    state._memory.write(0xFFF, (opcode.value << 4) | 0x01)
    state._memory.write(0x000, 0x23)
    state._flags = FlagsSnapshot(
        FlagValues(False, False, False, False),
        FlagsDefinedMask.zero_and_sign(),
    )

    fetched = state.fetch_instruction()
    assert fetched == DecodedInstruction(opcode, 0x123)
    assert state.pc == 0x001

    diagnostic = state.execute_instruction(fetched, policy=ExecutionPolicy.STRICT)

    assert diagnostic is not None
    assert diagnostic.identifier is DiagnosticIdentifier.UNDEFINED_CONDITIONAL_FLAG
    assert state.pc == 0x001


@pytest.mark.parametrize("opcode,flag", [(Opcode.JC, Flag.CARRY), (Opcode.JV, Flag.OVERFLOW)])
def test_conditional_jump_boundary_fetch_hardware_like_takes_concrete_target(
    opcode: Opcode, flag: Flag
) -> None:
    state = ArchitecturalState()
    state._pc.load(0xFFF)
    state._memory.write(0xFFF, (opcode.value << 4) | 0x01)
    state._memory.write(0x000, 0x23)
    state._flags = FlagsSnapshot(
        FlagValues(False, flag is Flag.CARRY, False, flag is Flag.OVERFLOW),
        FlagsDefinedMask.zero_and_sign(),
    )

    fetched = state.fetch_instruction()
    diagnostic = state.execute_instruction(fetched, policy=ExecutionPolicy.HARDWARE_LIKE)

    assert diagnostic is not None
    assert state.pc == 0x123


@pytest.mark.parametrize(
    "instruction",
    [
        DecodedInstruction(Opcode.LDI, 0x080),
        DecodedInstruction(Opcode.LDA, 0xABC),
    ],
)
@pytest.mark.parametrize("opcode,flag", [(Opcode.JC, Flag.CARRY), (Opcode.JV, Flag.OVERFLOW)])
def test_ldi_and_lda_leave_c_and_o_undefined_for_policy_resolution(
    instruction: DecodedInstruction, opcode: Opcode, flag: Flag
) -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(
        FlagValues(False, True, False, True),
        FlagsDefinedMask.all(),
    )
    if instruction.opcode is Opcode.LDA:
        state._memory.write(instruction.operand, 0x12)
    state.execute_instruction(instruction)
    fetched = _fetch_conditional(state, opcode, 0xABC)

    diagnostic = state.execute_instruction(fetched, policy=ExecutionPolicy.STRICT)

    assert diagnostic is not None
    assert diagnostic.severity is DiagnosticSeverity.ERROR
    assert state.flags_defined_mask == FlagsDefinedMask.zero_and_sign()


@pytest.mark.parametrize(
    "instruction",
    [
        DecodedInstruction(Opcode.ADD, 0xABC),
        DecodedInstruction(Opcode.SUB, 0xABC),
    ],
)
@pytest.mark.parametrize("opcode", [Opcode.JC, Opcode.JV])
def test_add_and_sub_make_c_and_o_defined_for_both_policies(
    instruction: DecodedInstruction, opcode: Opcode
) -> None:
    state = ArchitecturalState()
    state._a.load(0x80)
    state._memory.write(0xABC, 0x01)
    state.execute_instruction(instruction)
    fetched = _fetch_conditional(state, opcode, 0xABC)

    strict_diagnostic = state.execute_instruction(fetched, policy=ExecutionPolicy.STRICT)
    state._pc.load(0x002)
    hardware_like_diagnostic = state.execute_instruction(
        fetched, policy=ExecutionPolicy.HARDWARE_LIKE
    )

    assert strict_diagnostic is None
    assert hardware_like_diagnostic is None
    assert state.flags_defined_mask == FlagsDefinedMask.all()
