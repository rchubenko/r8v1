import pytest

from cpu import Flag, FlagsDefinedMask, FlagsSnapshot, FlagValues
from emulator import ArchitecturalState, DecodedInstruction, Opcode


def _fetch_jmp(state: ArchitecturalState, target: int) -> DecodedInstruction:
    state._memory.write(0x000, 0x60 | ((target >> 8) & 0x0F))
    state._memory.write(0x001, target & 0xFF)
    fetched = state.fetch_instruction()
    assert fetched == DecodedInstruction(Opcode.JMP, target)
    return fetched


@pytest.mark.parametrize("target", [0x000, 0x001, 0x002, 0x0FF, 0x100, 0xABC, 0xFFE, 0xFFF])
def test_jmp_loads_the_exact_full_12_bit_target(target: int) -> None:
    state = ArchitecturalState()
    fetched = _fetch_jmp(state, target)

    state.execute_instruction(fetched)

    assert state.pc == target


@pytest.mark.parametrize("target", [0x001, 0x123, 0xFFF])
def test_jmp_accepts_odd_targets_without_alignment(target: int) -> None:
    state = ArchitecturalState()
    fetched = _fetch_jmp(state, target)

    state.execute_instruction(fetched)

    assert state.pc == target


@pytest.mark.parametrize(
    "values",
    [
        FlagValues(False, False, False, False),
        FlagValues(False, False, False, True),
        FlagValues(False, False, True, False),
        FlagValues(False, True, False, False),
        FlagValues(True, False, False, False),
        FlagValues(True, True, True, True),
    ],
)
@pytest.mark.parametrize(
    "defined",
    [
        FlagsDefinedMask.none(),
        FlagsDefinedMask.zero_and_sign(),
        FlagsDefinedMask((Flag.CARRY, Flag.OVERFLOW)),
        FlagsDefinedMask.all(),
    ],
)
def test_jmp_preserves_concrete_flags_and_defined_mask(
    values: FlagValues, defined: FlagsDefinedMask
) -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(values, defined)
    fetched = _fetch_jmp(state, 0xABC)
    before_flags = state.flags
    before_mask = state.flags_defined_mask

    state.execute_instruction(fetched)

    assert state.flags == before_flags
    assert state.flags_defined_mask == before_mask


def test_jmp_preserves_a_ir_sram_and_halt_after_fetch() -> None:
    state = ArchitecturalState()
    state._a.load(0xA5)
    fetched = _fetch_jmp(state, 0xABC)
    before_a = state.a
    before_ir = (state.irh, state.irl)
    before_memory = state.memory_image
    state._halt.latch()

    state.execute_instruction(fetched)

    assert state.a == before_a
    assert (state.irh, state.irl) == before_ir
    assert state.memory_image == before_memory
    assert state.halt_state is True
    assert state.pc == 0xABC


def test_jmp_uses_post_fetch_pc_before_loading_target() -> None:
    state = ArchitecturalState()
    state._pc.load(0x100)
    state._memory.write(0x100, 0x60)
    state._memory.write(0x101, 0x01)

    fetched = state.fetch_instruction()

    assert fetched == DecodedInstruction(Opcode.JMP, 0x001)
    assert state.pc == 0x102

    state.execute_instruction(fetched)

    assert state.pc == 0x001


def test_jmp_instruction_fetched_across_boundary_loads_target_after_fetch() -> None:
    state = ArchitecturalState()
    state._pc.load(0xFFF)
    state._memory.write(0xFFF, 0x60)
    state._memory.write(0x000, 0x23)

    fetched = state.fetch_instruction()
    assert state.pc == 0x001

    state.execute_instruction(fetched)

    assert fetched == DecodedInstruction(Opcode.JMP, 0x023)
    assert state.pc == 0x023
