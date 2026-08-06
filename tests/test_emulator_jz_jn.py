import pytest

from cpu import Flag, FlagsDefinedMask, FlagsSnapshot, FlagValues
from emulator import ArchitecturalState, DecodedInstruction, Opcode


def _fetch_branch(state: ArchitecturalState, opcode: Opcode, target: int) -> DecodedInstruction:
    state._memory.write(0x000, (opcode.value << 4) | ((target >> 8) & 0x0F))
    state._memory.write(0x001, target & 0xFF)
    fetched = state.fetch_instruction()
    assert fetched == DecodedInstruction(opcode, target)
    return fetched


@pytest.mark.parametrize("target", [0x000, 0x001, 0x123, 0xABC, 0xFFF])
def test_jz_taken_loads_target_when_zero_is_set(target: int) -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(
        FlagValues(True, False, False, False),
        FlagsDefinedMask((Flag.ZERO,)),
    )
    fetched = _fetch_branch(state, Opcode.JZ, target)

    state.execute_instruction(fetched)

    assert state.pc == target


def test_jz_not_taken_preserves_post_fetch_pc_when_zero_is_clear() -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(
        FlagValues(False, True, False, True),
        FlagsDefinedMask((Flag.ZERO,)),
    )
    fetched = _fetch_branch(state, Opcode.JZ, 0xABC)
    post_fetch_pc = state.pc

    state.execute_instruction(fetched)

    assert state.pc == post_fetch_pc


@pytest.mark.parametrize("target", [0x000, 0x001, 0x123, 0xABC, 0xFFF])
def test_jn_taken_loads_target_when_sign_is_set(target: int) -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(
        FlagValues(False, False, True, False),
        FlagsDefinedMask((Flag.SIGN,)),
    )
    fetched = _fetch_branch(state, Opcode.JN, target)

    state.execute_instruction(fetched)

    assert state.pc == target


def test_jn_not_taken_preserves_post_fetch_pc_when_sign_is_clear() -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(
        FlagValues(True, True, False, True),
        FlagsDefinedMask((Flag.SIGN,)),
    )
    fetched = _fetch_branch(state, Opcode.JN, 0xABC)
    post_fetch_pc = state.pc

    state.execute_instruction(fetched)

    assert state.pc == post_fetch_pc


@pytest.mark.parametrize("opcode", [Opcode.JZ, Opcode.JN])
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
        FlagsDefinedMask((Flag.ZERO, Flag.SIGN)),
        FlagsDefinedMask.all(),
        FlagsDefinedMask((Flag.ZERO,)),
        FlagsDefinedMask((Flag.SIGN,)),
    ],
)
def test_jz_and_jn_preserve_flags_and_defined_mask(
    opcode: Opcode, values: FlagValues, defined: FlagsDefinedMask
) -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(values, defined)
    fetched = _fetch_branch(state, opcode, 0xABC)
    before_flags = state.flags
    before_mask = state.flags_defined_mask

    state.execute_instruction(fetched)

    assert state.flags == before_flags
    assert state.flags_defined_mask == before_mask


@pytest.mark.parametrize("opcode", [Opcode.JZ, Opcode.JN])
def test_conditional_jump_preserves_a_ir_sram_and_halt(
    opcode: Opcode,
) -> None:
    state = ArchitecturalState()
    state._a.load(0xA5)
    state._flags = FlagsSnapshot(
        FlagValues(True, False, True, False),
        FlagsDefinedMask((Flag.ZERO, Flag.SIGN)),
    )
    fetched = _fetch_branch(state, opcode, 0xABC)
    before_a = state.a
    before_ir = (state.irh, state.irl)
    before_memory = state.memory_image
    state._halt.latch()

    state.execute_instruction(fetched)

    assert state.a == before_a
    assert (state.irh, state.irl) == before_ir
    assert state.memory_image == before_memory
    assert state.halt_state is True


@pytest.mark.parametrize("opcode", [Opcode.JZ, Opcode.JN])
@pytest.mark.parametrize("target", [0x001, 0x123, 0xFFF])
def test_conditional_jump_accepts_odd_targets(opcode: Opcode, target: int) -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(
        FlagValues(opcode is Opcode.JZ, False, opcode is Opcode.JN, False),
        FlagsDefinedMask.all(),
    )
    fetched = _fetch_branch(state, opcode, target)

    state.execute_instruction(fetched)

    assert state.pc == target


@pytest.mark.parametrize("opcode", [Opcode.JZ, Opcode.JN])
def test_conditional_jump_fetched_across_boundary_preserves_false_post_fetch_pc(
    opcode: Opcode,
) -> None:
    state = ArchitecturalState()
    state._pc.load(0xFFF)
    state._memory.write(0xFFF, (opcode.value << 4) | 0x01)
    state._memory.write(0x000, 0x23)
    state._flags = FlagsSnapshot(
        FlagValues(False, False, False, False),
        FlagsDefinedMask.all(),
    )

    fetched = state.fetch_instruction()
    assert fetched == DecodedInstruction(opcode, 0x123)
    assert state.pc == 0x001

    state.execute_instruction(fetched)

    assert state.pc == 0x001


@pytest.mark.parametrize("opcode", [Opcode.JZ, Opcode.JN])
def test_conditional_jump_fetched_across_boundary_takes_target(
    opcode: Opcode,
) -> None:
    state = ArchitecturalState()
    state._pc.load(0xFFF)
    state._memory.write(0xFFF, (opcode.value << 4) | 0x01)
    state._memory.write(0x000, 0x23)
    state._flags = FlagsSnapshot(
        FlagValues(opcode is Opcode.JZ, False, opcode is Opcode.JN, False),
        FlagsDefinedMask.all(),
    )

    fetched = state.fetch_instruction()
    state.execute_instruction(fetched)

    assert state.pc == 0x123
