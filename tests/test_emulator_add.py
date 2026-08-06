import pytest

from cpu import ALUMode, Flag, FlagsDefinedMask, FlagsSnapshot, FlagValues, evaluate
from emulator import ArchitecturalState, DecodedInstruction, Opcode


def _fetch_add(state: ArchitecturalState, address: int) -> DecodedInstruction:
    state._memory.write(0x000, 0x30 | ((address >> 8) & 0x0F))
    state._memory.write(0x001, address & 0xFF)
    fetched = state.fetch_instruction()
    assert fetched == DecodedInstruction(Opcode.ADD, address)
    return fetched


@pytest.mark.parametrize(
    ("a", "operand", "expected"),
    [
        (0x00, 0x00, 0x00),
        (0x00, 0x01, 0x01),
        (0x01, 0x01, 0x02),
        (0x7E, 0x01, 0x7F),
        (0x7F, 0x01, 0x80),
        (0x80, 0x7F, 0xFF),
        (0x80, 0x80, 0x00),
        (0xFE, 0x01, 0xFF),
        (0xFF, 0x01, 0x00),
        (0xFF, 0xFF, 0xFE),
    ],
)
def test_add_result_boundary_cases(a: int, operand: int, expected: int) -> None:
    state = ArchitecturalState()
    state._a.load(a)
    state._memory.write(0xABC, operand)

    state.execute_instruction(DecodedInstruction(Opcode.ADD, 0xABC))

    assert state.a == expected


@pytest.mark.parametrize("address", [0x000, 0x001, 0x0FF, 0x100, 0xABC, 0xFFE, 0xFFF])
def test_add_reads_the_exact_full_12_bit_operand_address(address: int) -> None:
    state = ArchitecturalState()
    fetched = _fetch_add(state, address)
    state._memory.write(address, 0x37)
    state._a.load(0x28)

    state.execute_instruction(fetched)

    assert state.a == 0x5F


def test_add_reads_current_sram_value_on_repeated_execution() -> None:
    state = ArchitecturalState()
    instruction = DecodedInstruction(Opcode.ADD, 0xABC)
    state._memory.write(0xABC, 0x12)
    state._a.load(0x10)
    state.execute_instruction(instruction)

    state._memory.write(0xABC, 0xE1)
    state._a.load(0x10)
    state.execute_instruction(instruction)

    assert state.a == 0xF1


@pytest.mark.parametrize(
    "defined",
    [
        FlagsDefinedMask.none(),
        FlagsDefinedMask.zero_and_sign(),
        FlagsDefinedMask((Flag.CARRY, Flag.OVERFLOW)),
        FlagsDefinedMask.all(),
    ],
)
def test_add_defines_all_flags_regardless_of_previous_mask(defined: FlagsDefinedMask) -> None:
    state = ArchitecturalState()
    state._a.load(0x7F)
    state._memory.write(0xABC, 0x01)
    state._flags = FlagsSnapshot(FlagValues(True, True, False, False), defined)

    state.execute_instruction(DecodedInstruction(Opcode.ADD, 0xABC))

    assert state.flags.values == FlagValues(False, False, True, True)
    assert state.flags_defined_mask == FlagsDefinedMask.all()


def test_add_preserves_pc_ir_sram_and_halt_after_fetch() -> None:
    state = ArchitecturalState()
    fetched = _fetch_add(state, 0xABC)
    state._memory.write(0xABC, 0x37)
    state._a.load(0x28)
    pc_after_fetch = state.pc
    ir_after_fetch = (state.irh, state.irl)
    memory_after_fetch = state.memory_image
    state._halt.latch()

    state.execute_instruction(fetched)

    assert state.a == 0x5F
    assert state.pc == pc_after_fetch
    assert (state.irh, state.irl) == ir_after_fetch
    assert state.memory_image == memory_after_fetch
    assert state.halt_state is True


def test_add_instruction_fetched_across_boundary_preserves_post_fetch_pc() -> None:
    state = ArchitecturalState()
    state._pc.load(0xFFF)
    state._memory.write(0x123, 0xA6)
    state._memory.write(0xFFF, 0x31)
    state._memory.write(0x000, 0x23)

    fetched = state.fetch_instruction()
    state.execute_instruction(fetched)

    assert fetched == DecodedInstruction(Opcode.ADD, 0x123)
    assert state.a == 0xA6
    assert state.pc == 0x001


def test_add_exhaustively_matches_approved_alu_and_flags_policy() -> None:
    state = ArchitecturalState()
    instruction = DecodedInstruction(Opcode.ADD, 0xABC)

    for a in range(0x100):
        for operand in range(0x100):
            state._a.load(a)
            state._memory.write(0xABC, operand)
            state.execute_instruction(instruction)
            expected = evaluate(ALUMode.ADD, a, operand)

            assert state.a == expected.result
            assert state.flags.values == FlagValues(
                zero=expected.zero,
                carry=expected.carry,
                sign=expected.sign,
                overflow=expected.overflow,
            )
            assert state.flags_defined_mask == FlagsDefinedMask.all()


def test_add_does_not_create_a_public_b_register_or_alu_mode_boundary() -> None:
    state = ArchitecturalState()

    assert not hasattr(state, "b")
    assert not hasattr(state, "alu_mode")
