from cpu import FlagsDefinedMask, FlagsSnapshot, FlagValues
from emulator import ArchitecturalState, DecodedInstruction, Opcode


def _set_pc(state: ArchitecturalState, value: int) -> None:
    state._pc.load(value)


def test_normal_fetch_updates_ir_pc_and_returns_decoded_instruction() -> None:
    state = ArchitecturalState()
    state._memory.write(0x000, 0x1A)
    state._memory.write(0x001, 0xBC)

    fetched = state.fetch_instruction()

    assert state.irh == 0x1A
    assert state.irl == 0xBC
    assert state.opcode == 0x1
    assert state.operand == 0xABC
    assert state.pc == 0x002
    assert fetched == DecodedInstruction(Opcode.LDI, 0xABC)


def test_fetch_reads_two_bytes_from_non_zero_pc() -> None:
    state = ArchitecturalState()
    _set_pc(state, 0x123)
    state._memory.write(0x123, 0x6A)
    state._memory.write(0x124, 0xBC)

    fetched = state.fetch_instruction()

    assert fetched == DecodedInstruction(Opcode.JMP, 0xABC)
    assert state.irh == 0x6A
    assert state.irl == 0xBC
    assert state.pc == 0x125


def test_fetch_wraps_from_0xFFE_to_zero() -> None:
    state = ArchitecturalState()
    _set_pc(state, 0xFFE)
    state._memory.write(0xFFE, 0x2A)
    state._memory.write(0xFFF, 0xBC)

    fetched = state.fetch_instruction()

    assert fetched == DecodedInstruction(Opcode.LDA, 0xABC)
    assert state.irh == 0x2A
    assert state.irl == 0xBC
    assert state.pc == 0x000


def test_fetch_wraps_from_0xFFF_to_0x001() -> None:
    state = ArchitecturalState()
    _set_pc(state, 0xFFF)
    state._memory.write(0xFFF, 0x3A)
    state._memory.write(0x000, 0xBC)

    fetched = state.fetch_instruction()

    assert fetched == DecodedInstruction(Opcode.ADD, 0xABC)
    assert state.irh == 0x3A
    assert state.irl == 0xBC
    assert state.pc == 0x001


def test_reserved_opcode_fetch_is_representable_without_halting() -> None:
    state = ArchitecturalState()

    for opcode in range(0xB, 0xF):
        state.reset()
        state._memory.write(0x000, opcode << 4)
        state._memory.write(0x001, 0x23)

        fetched = state.fetch_instruction()

        assert fetched.opcode.value == opcode
        assert fetched.operand == 0x023
        assert state.halt_state is False


def test_hlt_fetch_does_not_set_halt_state() -> None:
    state = ArchitecturalState()
    state._memory.write(0x000, 0xF0)
    state._memory.write(0x001, 0x00)

    fetched = state.fetch_instruction()

    assert fetched == DecodedInstruction(Opcode.HLT, 0x000)
    assert state.halt_state is False


def test_fetch_observes_current_sram_bytes_without_caching() -> None:
    state = ArchitecturalState()
    state._memory.write(0x100, 0x10)
    state._memory.write(0x101, 0x01)
    _set_pc(state, 0x100)

    first = state.fetch_instruction()

    state._memory.write(0x100, 0x60)
    state._memory.write(0x101, 0x02)
    _set_pc(state, 0x100)
    second = state.fetch_instruction()

    assert first == DecodedInstruction(Opcode.LDI, 0x001)
    assert second == DecodedInstruction(Opcode.JMP, 0x002)


def test_fetch_changes_only_pc_and_ir() -> None:
    state = ArchitecturalState()
    state._a.load(0xA5)
    state._flags = FlagsSnapshot(
        FlagValues(True, True, True, True),
        FlagsDefinedMask.zero_and_sign(),
    )
    state._halt.latch()
    state._memory.write(0x000, 0x12)
    state._memory.write(0x001, 0x34)
    memory_before = state.memory_image

    state.fetch_instruction()

    assert state.a == 0xA5
    assert state.flags == FlagsSnapshot(
        FlagValues(True, True, True, True),
        FlagsDefinedMask.zero_and_sign(),
    )
    assert state.halt_state is True
    assert state.memory_image == memory_before
    assert state.pc == 0x002
    assert state.irh == 0x12
    assert state.irl == 0x34


def test_fetch_one_state_does_not_affect_another_instance() -> None:
    first = ArchitecturalState()
    second = ArchitecturalState()
    first._memory.write(0x000, 0x10)
    first._memory.write(0x001, 0xFF)

    fetched = first.fetch_instruction()

    assert fetched == DecodedInstruction(Opcode.LDI, 0x0FF)
    assert first.pc == 0x002
    assert second.pc == 0x000
    assert second.irh == 0x00
    assert second.irl == 0x00
