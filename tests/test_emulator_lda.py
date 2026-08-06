import pytest

from cpu import FlagsDefinedMask, FlagsSnapshot, FlagValues
from emulator import ArchitecturalState, DecodedInstruction, Opcode


def _fetch_lda(state: ArchitecturalState, address: int) -> DecodedInstruction:
    high = 0x20 | ((address >> 8) & 0x0F)
    low = address & 0xFF
    state._memory.write(0x000, high)
    state._memory.write(0x001, low)
    fetched = state.fetch_instruction()
    assert fetched.opcode is Opcode.LDA
    assert fetched.operand == address
    return fetched


@pytest.mark.parametrize("address", [0x000, 0x001, 0x07F, 0x080, 0x0FF, 0x100, 0xABC, 0xFFE, 0xFFF])
def test_lda_reads_the_exact_full_12_bit_operand_address(address: int) -> None:
    state = ArchitecturalState()
    if address not in (0x000, 0x001):
        state._memory.write(address, (address * 37 + 11) % 256)

    fetched = _fetch_lda(state, address)
    expected = state._memory.read(address)
    state.execute_instruction(fetched)

    assert state.a == expected


@pytest.mark.parametrize(
    ("value", "zero", "sign"),
    [
        (0x00, True, False),
        (0x01, False, False),
        (0x7F, False, False),
        (0x80, False, True),
        (0xFF, False, True),
    ],
)
def test_lda_updates_zero_and_sign_flags(value: int, zero: bool, sign: bool) -> None:
    state = ArchitecturalState()
    state._memory.write(0xABC, value)

    fetched = _fetch_lda(state, 0xABC)
    state.execute_instruction(fetched)

    assert state.a == value
    assert state.flags.values.zero is zero
    assert state.flags.values.sign is sign
    assert state.flags_defined_mask == FlagsDefinedMask.zero_and_sign()


@pytest.mark.parametrize("carry", [False, True])
@pytest.mark.parametrize("overflow", [False, True])
def test_lda_preserves_concrete_carry_and_overflow_but_undefines_them(
    carry: bool, overflow: bool
) -> None:
    state = ArchitecturalState()
    state._memory.write(0xABC, 0x80)
    state._flags = FlagsSnapshot(
        FlagValues(False, carry, False, overflow),
        FlagsDefinedMask.all(),
    )

    fetched = _fetch_lda(state, 0xABC)
    state.execute_instruction(fetched)

    assert state.flags.values.carry is carry
    assert state.flags.values.overflow is overflow
    assert state.flags_defined_mask == FlagsDefinedMask.zero_and_sign()


def test_lda_reads_current_sram_value_on_repeated_execution() -> None:
    state = ArchitecturalState()
    state._memory.write(0xABC, 0x12)
    first = _fetch_lda(state, 0xABC)
    state.execute_instruction(first)

    state._memory.write(0xABC, 0xE1)
    state._pc.load(0x000)
    second = _fetch_lda(state, 0xABC)
    state.execute_instruction(second)

    assert state.a == 0xE1


def test_lda_preserves_pc_ir_sram_and_halt_after_fetch() -> None:
    state = ArchitecturalState()
    state._memory.write(0xABC, 0x5A)
    fetched = _fetch_lda(state, 0xABC)
    pc_after_fetch = state.pc
    ir_after_fetch = (state.irh, state.irl)
    memory_after_fetch = state.memory_image
    state._halt.latch()

    state.execute_instruction(fetched)

    assert state.a == 0x5A
    assert state.pc == pc_after_fetch
    assert (state.irh, state.irl) == ir_after_fetch
    assert state.memory_image == memory_after_fetch
    assert state.halt_state is True


def test_lda_instruction_fetched_across_boundary_uses_independent_operand() -> None:
    state = ArchitecturalState()
    state._pc.load(0xFFF)
    state._memory.write(0x123, 0xA6)
    state._memory.write(0xFFF, 0x21)
    state._memory.write(0x000, 0x23)

    fetched = state.fetch_instruction()
    state.execute_instruction(fetched)

    assert fetched == DecodedInstruction(Opcode.LDA, 0x123)
    assert state.a == 0xA6
    assert state.pc == 0x001
