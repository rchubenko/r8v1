import pytest

from cpu import SRAM_SIZE, Flag, FlagsDefinedMask, FlagsSnapshot, FlagValues
from emulator import ArchitecturalState, DecodedInstruction, Opcode


def _fetch_sta(state: ArchitecturalState, address: int) -> DecodedInstruction:
    state._memory.write(0x000, 0x50 | ((address >> 8) & 0x0F))
    state._memory.write(0x001, address & 0xFF)
    fetched = state.fetch_instruction()
    assert fetched == DecodedInstruction(Opcode.STA, address)
    return fetched


@pytest.mark.parametrize("address", [0x000, 0x001, 0x0FF, 0x100, 0xABC, 0xFFE, 0xFFF])
@pytest.mark.parametrize("value", [0x00, 0x01, 0x7F, 0x80, 0xFF])
def test_sta_writes_current_a_to_the_exact_full_12_bit_address(address: int, value: int) -> None:
    state = ArchitecturalState()
    fetched = _fetch_sta(state, address)
    state._a.load(value)

    state.execute_instruction(fetched)

    assert state._memory.read(address) == value


def test_sta_changes_exactly_one_byte_in_a_nontrivial_memory_image() -> None:
    state = ArchitecturalState()
    image = bytes((address * 37 + 11) & 0xFF for address in range(SRAM_SIZE))
    state.load_image(image)
    fetched = _fetch_sta(state, 0xABC)
    before = state.memory_image
    state._a.load(0xE1)

    state.execute_instruction(fetched)

    after = state.memory_image
    assert after[0xABC] == 0xE1
    assert sum(before[address] != after[address] for address in range(SRAM_SIZE)) == 1
    assert all(
        before[address] == after[address] for address in range(SRAM_SIZE) if address != 0xABC
    )


def test_sta_same_value_write_keeps_the_full_memory_image_unchanged() -> None:
    state = ArchitecturalState()
    state._memory.write(0xABC, 0xE1)
    fetched = _fetch_sta(state, 0xABC)
    state._a.load(0xE1)
    before = state.memory_image

    state.execute_instruction(fetched)

    assert state.memory_image == before


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
def test_sta_preserves_concrete_flags_and_defined_mask(
    values: FlagValues, defined: FlagsDefinedMask
) -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(values, defined)
    state._a.load(0xA5)
    fetched = _fetch_sta(state, 0xABC)
    before_flags = state.flags
    before_mask = state.flags_defined_mask

    state.execute_instruction(fetched)

    assert state.flags == before_flags
    assert state.flags_defined_mask == before_mask


def test_sta_uses_current_a_after_fetch() -> None:
    state = ArchitecturalState()
    fetched = _fetch_sta(state, 0xABC)
    state._a.load(0xD7)

    state.execute_instruction(fetched)

    assert state._memory.read(0xABC) == 0xD7


def test_sta_preserves_a_pc_ir_flags_mask_and_halt_after_fetch() -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(
        FlagValues(True, False, True, False),
        FlagsDefinedMask((Flag.ZERO, Flag.OVERFLOW)),
    )
    state._a.load(0xA5)
    fetched = _fetch_sta(state, 0xABC)
    before_a = state.a
    before_pc = state.pc
    before_ir = (state.irh, state.irl)
    before_flags = state.flags
    before_mask = state.flags_defined_mask
    state._halt.latch()

    state.execute_instruction(fetched)

    assert state.a == before_a
    assert state.pc == before_pc
    assert (state.irh, state.irl) == before_ir
    assert state.flags == before_flags
    assert state.flags_defined_mask == before_mask
    assert state.halt_state is True


def test_sta_allows_code_address_write_and_future_fetch_observes_modified_byte() -> None:
    state = ArchitecturalState()
    fetched = _fetch_sta(state, 0x100)
    state._a.load(0xAB)

    state.execute_instruction(fetched)

    assert state._memory.read(0x100) == 0xAB
    state._memory.write(0x101, 0x34)
    state._pc.load(0x100)
    modified = state.fetch_instruction()

    assert modified == DecodedInstruction(Opcode.JV, 0xB34)


def test_sta_instruction_fetched_across_boundary_preserves_post_fetch_pc() -> None:
    state = ArchitecturalState()
    state._pc.load(0xFFF)
    state._memory.write(0xFFF, 0x50)
    state._memory.write(0x000, 0x23)
    state._a.load(0x6C)

    fetched = state.fetch_instruction()
    state.execute_instruction(fetched)

    assert fetched == DecodedInstruction(Opcode.STA, 0x023)
    assert state._memory.read(0x023) == 0x6C
    assert state.pc == 0x001


def test_sta_does_not_create_a_public_b_register_or_hardware_write_boundary() -> None:
    state = ArchitecturalState()

    assert not hasattr(state, "b")
    assert not hasattr(state, "ram_we")
    assert not hasattr(state, "mem_owner")
