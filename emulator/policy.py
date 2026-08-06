"""Execution-environment policy and diagnostics for the R8 v1 emulator."""

from dataclasses import dataclass
from enum import Enum

from cpu import Flag, FlagsSnapshot


class ExecutionPolicy(Enum):
    """Policy for reading an architecturally undefined conditional flag."""

    STRICT = "STRICT"
    HARDWARE_LIKE = "HARDWARE_LIKE"


class DiagnosticIdentifier(Enum):
    """Typed identifiers for non-architectural execution observations."""

    UNDEFINED_CONDITIONAL_FLAG = "UNDEFINED_CONDITIONAL_FLAG"


class DiagnosticSeverity(Enum):
    """Severity of a non-architectural diagnostic observation."""

    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """Immutable non-architectural execution diagnostic."""

    identifier: DiagnosticIdentifier
    severity: DiagnosticSeverity


@dataclass(frozen=True, slots=True)
class ConditionalFlagResolution:
    """Immutable policy result before a branch mutates architectural state."""

    branch_allowed: bool
    value: bool
    diagnostic: Diagnostic | None


def _flag_value(flags: FlagsSnapshot, flag: Flag) -> bool:
    if flag is Flag.ZERO:
        return flags.values.zero
    if flag is Flag.CARRY:
        return flags.values.carry
    if flag is Flag.SIGN:
        return flags.values.sign
    if flag is Flag.OVERFLOW:
        return flags.values.overflow
    raise AssertionError(f"unhandled flag: {flag!r}")


def resolve_conditional_flag(
    flag: Flag,
    flags: FlagsSnapshot,
    policy: ExecutionPolicy,
) -> ConditionalFlagResolution:
    """Resolve one conditional flag without mutating architectural state."""

    if not isinstance(flag, Flag):
        raise TypeError(f"flag must be a Flag; got {flag!r}")
    if not isinstance(flags, FlagsSnapshot):
        raise TypeError(f"flags must be a FlagsSnapshot; got {flags!r}")
    if not isinstance(policy, ExecutionPolicy):
        raise TypeError(f"policy must be an ExecutionPolicy; got {policy!r}")

    value = _flag_value(flags, flag)
    if flags.defined.is_defined(flag):
        return ConditionalFlagResolution(branch_allowed=True, value=value, diagnostic=None)

    diagnostic = Diagnostic(
        identifier=DiagnosticIdentifier.UNDEFINED_CONDITIONAL_FLAG,
        severity=(
            DiagnosticSeverity.ERROR
            if policy is ExecutionPolicy.STRICT
            else DiagnosticSeverity.WARNING
        ),
    )
    return ConditionalFlagResolution(
        branch_allowed=policy is ExecutionPolicy.HARDWARE_LIKE,
        value=value,
        diagnostic=diagnostic,
    )
