from dataclasses import FrozenInstanceError

import pytest

from cpu import SRAM_SIZE, FlagsDefinedMask, FlagsSnapshot, FlagValues
from emulator import ArchitecturalState, ArchitecturalStateSnapshot, Opcode


def _image(seed: int = 0) -> bytes:
    return bytes((address * 37 + seed) % 256 for address in range(SRAM_SIZE))


def _prepare_modified_state(state: ArchitecturalState) -> None:
    state._a.load(0xA5)
    state._pc.load(0xABC)
    state._ir.load_high(0xF1)
    state._ir.load_low(0x23)
    state._flags = FlagsSnapshot(
        FlagValues(True, True, True, True),
        FlagsDefinedMask.zero_and_sign(),
    )
    state._memory.write(0x000, 0x11)
    state._memory.write(0xFFF, 0x22)
    state._halt.latch()


def test_initial_lightweight_and_full_snapshots_are_architectural_values() -> None:
    state = ArchitecturalState()

    lightweight = state.snapshot()
    full = state.snapshot(include_memory=True)

    assert type(lightweight) is ArchitecturalStateSnapshot
    assert lightweight.a == 0x00
    assert lightweight.pc == 0x000
    assert lightweight.irh == 0x00
    assert lightweight.irl == 0x00
    assert lightweight.flags == FlagsSnapshot.reset()
    assert lightweight.flags_defined_mask == FlagsDefinedMask.all()
    assert lightweight.halt_state is False
    assert lightweight.memory is None
    assert full.memory == bytes(SRAM_SIZE)


def test_repeated_snapshots_are_equal_and_memory_capture_is_explicit() -> None:
    state = ArchitecturalState()

    assert state.snapshot() == state.snapshot()
    assert state.snapshot(include_memory=True) == state.snapshot(include_memory=True)
    assert state.snapshot() != state.snapshot(include_memory=True)


def test_snapshot_is_immutable() -> None:
    snapshot = ArchitecturalState().snapshot(include_memory=True)

    with pytest.raises(FrozenInstanceError):
        snapshot.a = 0x01  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        snapshot.flags = FlagsSnapshot.reset()  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        snapshot.memory = bytes(SRAM_SIZE)  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        snapshot.flags.values = snapshot.flags.values  # type: ignore[misc]
    with pytest.raises(AttributeError):
        snapshot.flags_defined_mask.defined_flags.add(  # type: ignore[attr-defined]
            next(iter(snapshot.flags_defined_mask.defined_flags))
        )
    with pytest.raises(TypeError):
        snapshot.memory[0] = 0xFF  # type: ignore[index]


def test_snapshot_captures_modified_state_exactly() -> None:
    state = ArchitecturalState()
    _prepare_modified_state(state)

    snapshot = state.snapshot(include_memory=True)

    assert snapshot.a == 0xA5
    assert snapshot.pc == 0xABC
    assert snapshot.irh == 0xF1
    assert snapshot.irl == 0x23
    assert snapshot.flags == FlagsSnapshot(
        FlagValues(True, True, True, True),
        FlagsDefinedMask.zero_and_sign(),
    )
    assert snapshot.halt_state is True
    assert snapshot.memory is not None
    assert snapshot.memory[0x000] == 0x11
    assert snapshot.memory[0xFFF] == 0x22


def test_snapshot_is_independent_from_later_state_mutations() -> None:
    state = ArchitecturalState()
    _prepare_modified_state(state)
    before = state.snapshot(include_memory=True)

    state._a.load(0x66)
    state._pc.load(0x123)
    state._memory.write(0x000, 0x99)
    state._halt.reset()
    after = state.snapshot(include_memory=True)

    assert before.a == 0xA5
    assert before.pc == 0xABC
    assert before.halt_state is True
    assert before.memory is not None
    assert before.memory[0x000] == 0x11
    assert after.a == 0x66
    assert after.pc == 0x123
    assert after.halt_state is False
    assert after.memory is not None
    assert after.memory[0x000] == 0x99
    assert before != after


def test_snapshot_equality_distinguishes_memory_capture_and_content() -> None:
    first = ArchitecturalState()
    second = ArchitecturalState()
    first.load_image(_image(seed=1))
    second.load_image(_image(seed=2))

    assert first.snapshot() == second.snapshot()
    assert first.snapshot(include_memory=True) != second.snapshot(include_memory=True)

    second.load_image(_image(seed=1))
    assert first.snapshot(include_memory=True) == second.snapshot(include_memory=True)
    assert first.snapshot() != first.snapshot(include_memory=True)


def test_snapshot_has_only_architectural_public_fields() -> None:
    snapshot = ArchitecturalState().snapshot()

    for excluded in (
        "b",
        "mar",
        "microstep",
        "data_bus",
        "control_word",
        "execution_policy",
        "diagnostics",
        "bus_trace",
        "microstep_trace",
        "simulator_state",
    ):
        assert not hasattr(snapshot, excluded)


def test_image_loading_is_visible_in_full_snapshot() -> None:
    state = ArchitecturalState()
    image = _image(seed=11)

    state.load_image(image)

    snapshot = state.snapshot(include_memory=True)

    assert snapshot.memory == image


def test_fetch_changes_only_pc_and_ir_in_snapshots() -> None:
    state = ArchitecturalState()
    state._memory.write(0x000, 0x1A)
    state._memory.write(0x001, 0xBC)
    before = state.snapshot(include_memory=True)

    fetched = state.fetch_instruction()
    after = state.snapshot(include_memory=True)

    assert fetched.opcode is Opcode.LDI
    assert before.a == after.a
    assert before.flags == after.flags
    assert before.flags_defined_mask == after.flags_defined_mask
    assert before.halt_state == after.halt_state
    assert before.memory == after.memory
    assert before.pc == 0x000
    assert after.pc == 0x002
    assert before.irh == 0x00
    assert before.irl == 0x00
    assert after.irh == 0x1A
    assert after.irl == 0xBC


def test_reset_resets_architecture_and_preserves_snapshot_memory() -> None:
    state = ArchitecturalState()
    image = _image(seed=19)
    state.load_image(image)
    state._a.load(0xA5)
    before = state.snapshot(include_memory=True)

    state.reset()
    after = state.snapshot(include_memory=True)

    assert before.memory == after.memory == image
    assert after.a == 0x00
    assert after.pc == 0x000
    assert after.flags == FlagsSnapshot.reset()
    assert after.halt_state is False
