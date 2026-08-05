"""Immutable FLAGS values and defined-mask models for R8 v1."""

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum


class Flag(Enum):
    """The four concrete architectural flags."""

    ZERO = "z"
    CARRY = "c"
    SIGN = "s"
    OVERFLOW = "o"


def _validate_flag(flag: object) -> Flag:
    if not isinstance(flag, Flag):
        raise TypeError(f"flag must be a Flag; got {flag!r}")
    return flag


@dataclass(frozen=True, slots=True)
class FlagValues:
    """Immutable concrete boolean values for Z, C, S, and O."""

    zero: bool
    carry: bool
    sign: bool
    overflow: bool

    def __post_init__(self) -> None:
        for name, value in (
            ("zero", self.zero),
            ("carry", self.carry),
            ("sign", self.sign),
            ("overflow", self.overflow),
        ):
            if type(value) is not bool:
                raise TypeError(f"{name} must be a bool; got {value!r}")

    @classmethod
    def reset(cls) -> "FlagValues":
        """Return the canonical concrete reset values: Z=C=S=O=0."""

        return cls(False, False, False, False)


@dataclass(frozen=True, slots=True, init=False)
class FlagsDefinedMask:
    """Immutable set of flags whose concrete values are architecturally defined."""

    _defined: frozenset[Flag]

    def __init__(self, flags: Iterable[Flag] = ()) -> None:
        normalized = frozenset(flags)
        for flag in normalized:
            _validate_flag(flag)
        object.__setattr__(self, "_defined", normalized)

    @classmethod
    def all(cls) -> "FlagsDefinedMask":
        """Return a mask with all four flags defined."""

        return cls(Flag)

    @classmethod
    def zero_and_sign(cls) -> "FlagsDefinedMask":
        """Return a mask with only Z and S defined."""

        return cls((Flag.ZERO, Flag.SIGN))

    @classmethod
    def none(cls) -> "FlagsDefinedMask":
        """Return a mask with no defined flags."""

        return cls()

    @property
    def defined_flags(self) -> frozenset[Flag]:
        """Return the immutable set of defined flags."""

        return self._defined

    @property
    def all_defined(self) -> bool:
        """Whether every architectural flag is defined."""

        return self._defined == frozenset(Flag)

    @property
    def none_defined(self) -> bool:
        """Whether no architectural flag is defined."""

        return not self._defined

    def is_defined(self, flag: Flag) -> bool:
        """Return whether one validated flag is defined by this mask."""

        return _validate_flag(flag) in self._defined


@dataclass(frozen=True, slots=True)
class FlagsSnapshot:
    """Immutable concrete FLAGS values paired with their defined mask."""

    values: FlagValues
    defined: FlagsDefinedMask

    def __post_init__(self) -> None:
        if not isinstance(self.values, FlagValues):
            raise TypeError(f"values must be a FlagValues; got {self.values!r}")
        if not isinstance(self.defined, FlagsDefinedMask):
            raise TypeError(f"defined must be a FlagsDefinedMask; got {self.defined!r}")

    @classmethod
    def reset(cls) -> "FlagsSnapshot":
        """Return concrete zero values with every flag defined."""

        return cls(FlagValues.reset(), FlagsDefinedMask.all())
