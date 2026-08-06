from cpu import FlagsDefinedMask, FlagsSnapshot, FlagValues
from emulator import ArchitecturalState


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
    state._memory.write(0x001, 0x22)
    state._memory.write(0x456, 0x33)
    state._memory.write(0xFFE, 0x44)
    state._memory.write(0xFFF, 0x55)
    state._halt.latch()


def test_reset_on_new_state_keeps_initial_architectural_values() -> None:
    state = ArchitecturalState()

    state.reset()

    assert state.a == 0x00
    assert state.pc == 0x000
    assert state.irh == 0x00
    assert state.irl == 0x00
    assert state.opcode == 0x0
    assert state.operand == 0x000
    assert state.flags == FlagsSnapshot.reset()
    assert state.flags_defined_mask == FlagsDefinedMask.all()
    assert state.halt_state is False


def test_reset_restores_modified_architectural_state() -> None:
    state = ArchitecturalState()
    _prepare_modified_state(state)
    memory_before = state.memory_image

    state.reset()

    assert state.a == 0x00
    assert state.pc == 0x000
    assert state.irh == 0x00
    assert state.irl == 0x00
    assert state.opcode == 0x0
    assert state.operand == 0x000
    assert state.flags.values == FlagValues(False, False, False, False)
    assert state.flags_defined_mask == FlagsDefinedMask.all()
    assert state.halt_state is False
    assert state.memory_image == memory_before


def test_reset_preserves_full_sram_image_at_boundaries() -> None:
    state = ArchitecturalState()
    _prepare_modified_state(state)
    memory_before = state.memory_image

    state.reset()

    assert state.memory_image == memory_before
    assert state.memory_image[0x000] == 0x11
    assert state.memory_image[0x001] == 0x22
    assert state.memory_image[0x456] == 0x33
    assert state.memory_image[0xFFE] == 0x44
    assert state.memory_image[0xFFF] == 0x55


def test_reset_clears_halt_independently_of_architectural_state() -> None:
    state = ArchitecturalState()
    state._halt.latch()
    state._a.load(0x7F)
    memory_before = state.memory_image

    assert state.halt_state is True

    state.reset()

    assert state.halt_state is False
    assert state.a == 0x00
    assert state.pc == 0x000
    assert state.flags == FlagsSnapshot.reset()
    assert state.memory_image == memory_before


def test_reset_is_idempotent() -> None:
    state = ArchitecturalState()
    _prepare_modified_state(state)

    state.reset()
    first_observation = (
        state.a,
        state.pc,
        state.irh,
        state.irl,
        state.flags,
        state.flags_defined_mask,
        state.halt_state,
        state.memory_image,
    )

    state.reset()
    second_observation = (
        state.a,
        state.pc,
        state.irh,
        state.irl,
        state.flags,
        state.flags_defined_mask,
        state.halt_state,
        state.memory_image,
    )

    assert second_observation == first_observation


def test_reset_does_not_affect_another_state_instance() -> None:
    first = ArchitecturalState()
    second = ArchitecturalState()
    _prepare_modified_state(first)
    second._a.load(0x66)
    second._memory.write(0x123, 0x99)
    second_before = (second.a, second.memory_image)

    first.reset()

    assert first.a == 0x00
    assert second.a == second_before[0]
    assert second.memory_image == second_before[1]
