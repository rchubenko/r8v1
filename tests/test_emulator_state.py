from dataclasses import FrozenInstanceError

import pytest

from cpu import SRAM_SIZE, Flag, FlagsDefinedMask, FlagsSnapshot
from emulator import ArchitecturalState


def test_architectural_state_has_deterministic_initial_values() -> None:
    state = ArchitecturalState()

    assert state.a == 0x00
    assert state.pc == 0x000
    assert state.irh == 0x00
    assert state.irl == 0x00
    assert state.opcode == 0x0
    assert state.operand == 0x000
    assert state.flags == FlagsSnapshot.reset()
    assert state.flags.values.zero is False
    assert state.flags.values.carry is False
    assert state.flags.values.sign is False
    assert state.flags.values.overflow is False
    assert state.flags_defined_mask == FlagsDefinedMask.all()
    assert state.flags_defined_mask.defined_flags == frozenset(Flag)
    assert state.halt_state is False
    assert len(state.memory_image) == SRAM_SIZE
    assert set(state.memory_image) == {0x00}


def test_independent_state_instances_do_not_share_component_holders() -> None:
    first = ArchitecturalState()
    second = ArchitecturalState()

    assert first._a is not second._a
    assert first._pc is not second._pc
    assert first._ir is not second._ir
    assert first._memory is not second._memory
    assert first._halt is not second._halt

    first._memory.write(0x123, 0xA5)

    assert first.memory_image[0x123] == 0xA5
    assert second.memory_image[0x123] == 0x00


def test_memory_observation_is_detached_bytes() -> None:
    state = ArchitecturalState()
    image = state.memory_image

    assert type(image) is bytes
    with pytest.raises(TypeError):
        image[0] = 0xFF  # type: ignore[index]
    assert state.memory_image[0] == 0x00


def test_observation_reads_do_not_change_state() -> None:
    state = ArchitecturalState()

    before = (
        state.a,
        state.pc,
        state.irh,
        state.irl,
        state.opcode,
        state.operand,
        state.flags,
        state.flags_defined_mask,
        state.halt_state,
        state.memory_image,
    )
    observations = (
        state.a,
        state.pc,
        state.irh,
        state.irl,
        state.opcode,
        state.operand,
        state.flags,
        state.flags_defined_mask,
        state.halt_state,
        state.memory_image,
    )

    assert observations == before


def test_flags_observation_is_immutable_and_mask_cannot_be_mutated() -> None:
    state = ArchitecturalState()

    with pytest.raises(FrozenInstanceError):
        state.flags.values = state.flags.values  # type: ignore[misc]
    with pytest.raises(AttributeError):
        state.flags_defined_mask.defined_flags.add(Flag.ZERO)  # type: ignore[attr-defined]


@pytest.mark.parametrize("excluded", ["b", "mar", "microstep", "data_bus", "control_word"])
def test_microarchitectural_values_are_not_public_state(excluded: str) -> None:
    state = ArchitecturalState()

    assert not hasattr(state, excluded)


def test_state_does_not_expose_execution_policy_or_diagnostics() -> None:
    state = ArchitecturalState()

    assert not hasattr(state, "execution_policy")
    assert not hasattr(state, "diagnostics")
