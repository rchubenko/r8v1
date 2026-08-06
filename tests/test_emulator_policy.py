from dataclasses import FrozenInstanceError, fields

import pytest

from cpu import Flag, FlagsDefinedMask, FlagsSnapshot, FlagValues
from emulator import (
    ArchitecturalState,
    ArchitecturalStateSnapshot,
    ConditionalFlagResolution,
    DiagnosticIdentifier,
    DiagnosticSeverity,
    ExecutionPolicy,
    resolve_conditional_flag,
)
from emulator.policy import Diagnostic


def _flags(value: bool, defined: FlagsDefinedMask) -> FlagsSnapshot:
    return FlagsSnapshot(FlagValues(value, value, value, value), defined)


def test_execution_policies_are_typed_distinct_immutable_values() -> None:
    assert list(ExecutionPolicy) == [ExecutionPolicy.STRICT, ExecutionPolicy.HARDWARE_LIKE]
    assert len(ExecutionPolicy) == 2
    assert ExecutionPolicy.STRICT.value == "STRICT"
    assert ExecutionPolicy.HARDWARE_LIKE.value == "HARDWARE_LIKE"


@pytest.mark.parametrize("policy", list(ExecutionPolicy))
@pytest.mark.parametrize("value", [False, True])
def test_defined_flag_is_used_without_diagnostic(policy: ExecutionPolicy, value: bool) -> None:
    result = resolve_conditional_flag(Flag.CARRY, _flags(value, FlagsDefinedMask.all()), policy)

    assert result == ConditionalFlagResolution(branch_allowed=True, value=value, diagnostic=None)


@pytest.mark.parametrize("flag", [Flag.CARRY, Flag.OVERFLOW])
@pytest.mark.parametrize("value", [False, True])
def test_undefined_flag_strict_rejects_branch_with_error(flag: Flag, value: bool) -> None:
    flags = FlagsSnapshot(
        FlagValues(
            False,
            value if flag is Flag.CARRY else False,
            False,
            value if flag is Flag.OVERFLOW else False,
        ),
        FlagsDefinedMask.zero_and_sign(),
    )

    result = resolve_conditional_flag(flag, flags, ExecutionPolicy.STRICT)

    assert result.branch_allowed is False
    assert result.value is value
    assert result.diagnostic == Diagnostic(
        DiagnosticIdentifier.UNDEFINED_CONDITIONAL_FLAG,
        DiagnosticSeverity.ERROR,
    )
    assert flags.defined == FlagsDefinedMask.zero_and_sign()
    assert flags.values == FlagValues(
        False,
        value if flag is Flag.CARRY else False,
        False,
        value if flag is Flag.OVERFLOW else False,
    )


@pytest.mark.parametrize("flag", [Flag.CARRY, Flag.OVERFLOW])
@pytest.mark.parametrize("value", [False, True])
def test_undefined_flag_hardware_like_uses_concrete_value_with_warning(
    flag: Flag, value: bool
) -> None:
    flags = FlagsSnapshot(
        FlagValues(value, value, value, value),
        FlagsDefinedMask.zero_and_sign(),
    )

    result = resolve_conditional_flag(flag, flags, ExecutionPolicy.HARDWARE_LIKE)

    assert result.branch_allowed is True
    assert result.value is value
    assert result.diagnostic == Diagnostic(
        DiagnosticIdentifier.UNDEFINED_CONDITIONAL_FLAG,
        DiagnosticSeverity.WARNING,
    )
    assert flags.defined == FlagsDefinedMask.zero_and_sign()


@pytest.mark.parametrize("flag", list(Flag))
def test_defined_flags_are_resolved_identically_by_both_policies(flag: Flag) -> None:
    flags = FlagsSnapshot(FlagValues(True, False, True, False), FlagsDefinedMask.all())

    strict = resolve_conditional_flag(flag, flags, ExecutionPolicy.STRICT)
    hardware_like = resolve_conditional_flag(flag, flags, ExecutionPolicy.HARDWARE_LIKE)

    assert strict == hardware_like
    assert strict.diagnostic is None


def test_diagnostics_are_typed_immutable_and_repeatable() -> None:
    flags = _flags(True, FlagsDefinedMask.zero_and_sign())
    first = resolve_conditional_flag(Flag.CARRY, flags, ExecutionPolicy.STRICT).diagnostic
    second = resolve_conditional_flag(Flag.CARRY, flags, ExecutionPolicy.STRICT).diagnostic

    assert first == second
    assert first is not None
    assert isinstance(first.identifier, DiagnosticIdentifier)
    assert isinstance(first.severity, DiagnosticSeverity)
    with pytest.raises(FrozenInstanceError):
        first.severity = DiagnosticSeverity.WARNING  # type: ignore[misc]


def test_policy_and_diagnostics_are_outside_architectural_state_and_snapshot() -> None:
    state = ArchitecturalState()
    snapshot = state.snapshot()

    assert not hasattr(state, "policy")
    assert not hasattr(state, "diagnostic")
    assert {field.name for field in fields(ArchitecturalStateSnapshot)} == {
        "a",
        "pc",
        "irh",
        "irl",
        "flags",
        "flags_defined_mask",
        "halt_state",
        "memory",
    }
    assert snapshot == state.snapshot()


@pytest.mark.parametrize("policy", list(ExecutionPolicy))
@pytest.mark.parametrize("flag", [Flag.CARRY, Flag.OVERFLOW])
def test_resolution_does_not_change_post_fetch_pc_or_halt(
    policy: ExecutionPolicy, flag: Flag
) -> None:
    state = ArchitecturalState()
    state._pc.load(0x100)
    state._memory.write(0x100, 0x70 if flag is Flag.CARRY else 0xA0)
    state._memory.write(0x101, 0x23)
    fetched = state.fetch_instruction()
    post_fetch_pc = state.pc
    state_snapshot = state.snapshot(include_memory=True)

    resolve_conditional_flag(flag, state.flags, policy)

    assert fetched.operand == 0x023
    assert state.pc == post_fetch_pc
    assert state.halt_state is False
    assert state.snapshot(include_memory=True) == state_snapshot


@pytest.mark.parametrize("policy", list(ExecutionPolicy))
def test_undefined_c_and_o_resolution_is_deterministic(policy: ExecutionPolicy) -> None:
    flags = FlagsSnapshot(
        FlagValues(False, True, False, False),
        FlagsDefinedMask.zero_and_sign(),
    )

    first_c = resolve_conditional_flag(Flag.CARRY, flags, policy)
    second_c = resolve_conditional_flag(Flag.CARRY, flags, policy)
    first_o = resolve_conditional_flag(Flag.OVERFLOW, flags, policy)
    second_o = resolve_conditional_flag(Flag.OVERFLOW, flags, policy)

    assert first_c == second_c
    assert first_o == second_o
