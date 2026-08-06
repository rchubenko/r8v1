import pytest

from cpu import FlagsDefinedMask, FlagsSnapshot, FlagValues
from emulator import ArchitecturalState, DecodedInstruction, Opcode


def _fetch_ldi(state: ArchitecturalState, operand: int) -> DecodedInstruction:
    state._memory.write(0x000, 0x10 | ((operand >> 8) & 0x0F))
    state._memory.write(0x001, operand & 0xFF)
    fetched = state.fetch_instruction()
    assert fetched.opcode is Opcode.LDI
    return fetched


def test_nop_after_fetch_preserves_post_fetch_architectural_state() -> None:
    state = ArchitecturalState()
    state._memory.write(0x000, 0x00)
    state._memory.write(0x001, 0x00)

    fetched = state.fetch_instruction()
    after_fetch = state.snapshot(include_memory=True)
    state.execute_instruction(fetched)

    assert state.snapshot(include_memory=True) == after_fetch


def test_nop_preserves_modified_state_after_fetch() -> None:
    state = ArchitecturalState()
    state._a.load(0xA5)
    state._flags = FlagsSnapshot(
        FlagValues(True, True, True, True),
        FlagsDefinedMask.zero_and_sign(),
    )
    state._memory.write(0x000, 0x00)
    state._memory.write(0x001, 0x00)

    fetched = state.fetch_instruction()
    after_fetch = state.snapshot(include_memory=True)
    state.execute_instruction(fetched)

    assert state.snapshot(include_memory=True) == after_fetch


@pytest.mark.parametrize(
    ("operand", "expected_a"),
    [
        (0x000, 0x00),
        (0x001, 0x01),
        (0x07F, 0x7F),
        (0x080, 0x80),
        (0x0FF, 0xFF),
        (0x100, 0x00),
        (0xABC, 0xBC),
        (0xFFF, 0xFF),
    ],
)
def test_ldi_loads_only_the_low_operand_byte(operand: int, expected_a: int) -> None:
    state = ArchitecturalState()

    fetched = _fetch_ldi(state, operand)
    state.execute_instruction(fetched)

    assert state.a == expected_a
    assert state.pc == 0x002
    assert state.irh == 0x10 | ((operand >> 8) & 0x0F)
    assert state.irl == operand & 0xFF
    assert state.halt_state is False


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
def test_ldi_updates_zero_and_sign_defined_flags(value: int, zero: bool, sign: bool) -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(
        FlagValues(False, True, False, True),
        FlagsDefinedMask.all(),
    )

    state.execute_instruction(DecodedInstruction(Opcode.LDI, value))

    assert state.flags.values.zero is zero
    assert state.flags.values.sign is sign
    assert state.flags_defined_mask == FlagsDefinedMask.zero_and_sign()


@pytest.mark.parametrize("carry", [False, True])
@pytest.mark.parametrize("overflow", [False, True])
def test_ldi_preserves_concrete_carry_and_overflow_but_undefines_them(
    carry: bool, overflow: bool
) -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(
        FlagValues(False, carry, False, overflow),
        FlagsDefinedMask.all(),
    )

    state.execute_instruction(DecodedInstruction(Opcode.LDI, 0x080))

    assert state.flags.values.carry is carry
    assert state.flags.values.overflow is overflow
    assert state.flags_defined_mask == FlagsDefinedMask.zero_and_sign()


def test_repeated_ldi_updates_a_z_and_s_while_preserving_c_and_o() -> None:
    state = ArchitecturalState()
    state._flags = FlagsSnapshot(
        FlagValues(False, True, False, True),
        FlagsDefinedMask.all(),
    )

    for operand, expected_a, expected_zero, expected_sign in (
        (0x000, 0x00, True, False),
        (0x080, 0x80, False, True),
        (0x001, 0x01, False, False),
    ):
        state.execute_instruction(DecodedInstruction(Opcode.LDI, operand))
        assert state.a == expected_a
        assert state.flags.values.zero is expected_zero
        assert state.flags.values.sign is expected_sign
        assert state.flags.values.carry is True
        assert state.flags.values.overflow is True
        assert state.flags_defined_mask == FlagsDefinedMask.zero_and_sign()


def test_ldi_preserves_pc_ir_sram_and_halt_after_fetch() -> None:
    state = ArchitecturalState()
    state._memory.write(0x000, 0x1A)
    state._memory.write(0x001, 0xBC)
    fetched = state.fetch_instruction()
    pc_after_fetch = state.pc
    ir_after_fetch = (state.irh, state.irl)
    memory_after_fetch = state.memory_image
    state._halt.latch()

    state.execute_instruction(fetched)

    assert state.pc == pc_after_fetch
    assert (state.irh, state.irl) == ir_after_fetch
    assert state.memory_image == memory_after_fetch
    assert state.halt_state is True
    assert state.a == 0xBC


def test_ldi_fetched_across_address_boundary_executes_without_pc_change() -> None:
    state = ArchitecturalState()
    state._pc.load(0xFFF)
    state._memory.write(0xFFF, 0x10)
    state._memory.write(0x000, 0x80)

    fetched = state.fetch_instruction()
    state.execute_instruction(fetched)

    assert fetched == DecodedInstruction(Opcode.LDI, 0x080)
    assert state.a == 0x80
    assert state.pc == 0x001


def test_unsupported_opcode_is_rejected_without_mutation() -> None:
    state = ArchitecturalState()
    before = state.snapshot(include_memory=True)

    with pytest.raises(ValueError, match="unsupported opcode"):
        state.execute_instruction(DecodedInstruction(Opcode.SUB, 0x123))

    assert state.snapshot(include_memory=True) == before


def test_invalid_execution_input_is_rejected_without_mutation() -> None:
    state = ArchitecturalState()
    before = state.snapshot(include_memory=True)

    with pytest.raises(TypeError, match="DecodedInstruction"):
        state.execute_instruction(object())  # type: ignore[arg-type]

    assert state.snapshot(include_memory=True) == before
