import pytest

from cpu import Flag, FlagsDefinedMask, FlagsSnapshot, FlagValues
from emulator import ArchitecturalState, DecodedInstruction, ExecutionPolicy, Opcode


def _fetch_hlt(state: ArchitecturalState) -> DecodedInstruction:
    state._memory.write(0x000, 0xF0)
    state._memory.write(0x001, 0x00)
    fetched = state.fetch_instruction()
    assert fetched == DecodedInstruction(Opcode.HLT, 0x000)
    return fetched


def test_hlt_sets_halt_state_and_preserves_architectural_state() -> None:
    state = ArchitecturalState()
    state._a.load(0xA5)
    state._flags = FlagsSnapshot(
        FlagValues(True, False, True, False),
        FlagsDefinedMask((Flag.ZERO, Flag.OVERFLOW)),
    )
    state._memory.write(0xABC, 0x5A)
    fetched = _fetch_hlt(state)
    before_a = state.a
    before_pc = state.pc
    before_ir = (state.irh, state.irl)
    before_flags = state.flags
    before_mask = state.flags_defined_mask
    before_memory = state.memory_image

    diagnostic = state.execute_instruction(fetched)

    assert diagnostic is None
    assert state.halt_state is True
    assert state.a == before_a
    assert state.pc == before_pc
    assert (state.irh, state.irl) == before_ir
    assert state.flags == before_flags
    assert state.flags_defined_mask == before_mask
    assert state.memory_image == before_memory


def test_halted_step_does_not_fetch_or_change_architectural_state() -> None:
    state = ArchitecturalState()
    state._memory.write(0x000, 0xF0)
    state._memory.write(0x001, 0x00)
    state._memory.write(0x002, 0x10)
    state._memory.write(0x003, 0x7F)
    state.step()
    assert state.halt_state is True
    before = state.snapshot(include_memory=True)

    for _ in range(3):
        assert state.step().diagnostic is None
        assert state.snapshot(include_memory=True) == before


def test_halted_step_does_not_reload_ir_or_increment_pc() -> None:
    state = ArchitecturalState()
    state._memory.write(0x000, 0xF0)
    state._memory.write(0x001, 0x00)
    state._memory.write(0x002, 0x10)
    state._memory.write(0x003, 0x7F)

    state.step()
    assert state.pc == 0x002
    assert (state.irh, state.irl) == (0xF0, 0x00)

    state.step()

    assert state.pc == 0x002
    assert (state.irh, state.irl) == (0xF0, 0x00)
    assert state.a == 0x00


def test_reset_clears_halt_preserves_sram_and_execution_resumes() -> None:
    state = ArchitecturalState()
    state._memory.write(0x000, 0xF0)
    state._memory.write(0x001, 0x00)
    state._memory.write(0xABC, 0x5A)
    state.step()
    assert state.halt_state is True

    state._memory.write(0x000, 0x10)
    state._memory.write(0x001, 0x42)
    state.reset()

    assert state.halt_state is False
    assert state.a == 0x00
    assert state.pc == 0x000
    assert (state.irh, state.irl) == (0x00, 0x00)
    assert state.flags == FlagsSnapshot.reset()
    assert state.flags_defined_mask == FlagsDefinedMask.all()
    assert state._memory.read(0xABC) == 0x5A

    assert state.step().diagnostic is None
    assert state.a == 0x42
    assert state.pc == 0x002


@pytest.mark.parametrize("policy", list(ExecutionPolicy))
def test_hlt_is_policy_independent(policy: ExecutionPolicy) -> None:
    state = ArchitecturalState()
    fetched = _fetch_hlt(state)

    diagnostic = state.execute_instruction(fetched, policy=policy)

    assert diagnostic is None
    assert state.halt_state is True


def test_hlt_can_be_reached_again_after_reset() -> None:
    state = ArchitecturalState()
    state._memory.write(0x000, 0xF0)
    state._memory.write(0x001, 0x00)

    state.step()
    state.step()
    state.reset()
    state.step()

    assert state.halt_state is True
    assert state.pc == 0x002


def test_hlt_fetched_across_boundary_preserves_post_fetch_pc() -> None:
    state = ArchitecturalState()
    state._pc.load(0xFFF)
    state._memory.write(0xFFF, 0xF0)
    state._memory.write(0x000, 0x00)

    fetched = state.fetch_instruction()
    assert fetched == DecodedInstruction(Opcode.HLT, 0x000)
    assert state.pc == 0x001

    state.execute_instruction(fetched)
    state.step()

    assert state.pc == 0x001
    assert state.halt_state is True
