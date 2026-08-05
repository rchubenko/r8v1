import pytest

from cpu import (
    SRAM,
    AddressSource,
    ALUMode,
    FixedWidthRegister,
    FlagsDefinedMask,
    FlagsSnapshot,
    HaltLatch,
    InstructionRegister,
    MemoryAddressRegister,
    MicrostepCounter,
    ProgramCounter,
    evaluate,
    latch_flags_for_alu_write,
    resolve_data_bus,
    select_address,
)


@pytest.mark.parametrize(
    ("high", "low", "expected_operand"),
    [
        (0x00, 0x00, 0x000),
        (0x0F, 0xFF, 0xFFF),
        (0xAF, 0xFF, 0xFFF),
        (0xF1, 0x23, 0x123),
    ],
)
def test_instruction_operand_flows_to_address_selector(
    high: int, low: int, expected_operand: int
) -> None:
    ir = InstructionRegister()
    ir.load_high(high)
    ir.load_low(low)
    original_high = ir.high
    original_low = ir.low

    address = select_address(
        AddressSource.IR_OPERAND,
        pc=0xABC,
        ir_operand=ir.operand,
    )

    assert address == expected_operand
    assert ir.high == original_high
    assert ir.low == original_low
    assert ir.operand == expected_operand


def test_instruction_opcode_bits_do_not_enter_selected_operand() -> None:
    ir = InstructionRegister()
    ir.load_high(0xF1)
    ir.load_low(0x23)

    assert ir.opcode == 0xF
    assert ir.operand == 0x123
    assert select_address(AddressSource.IR_OPERAND, pc=0x000, ir_operand=ir.operand) == 0x123


@pytest.mark.parametrize("loaded", [0x000, 0x001, 0x7FF, 0x800, 0xFFF])
def test_program_counter_value_flows_to_address_selector(loaded: int) -> None:
    pc = ProgramCounter()
    pc.load(loaded)

    address = select_address(
        AddressSource.PC,
        pc=pc.value,
        ir_operand=0x123,
    )

    assert address == loaded
    assert pc.value == loaded


def test_program_counter_wrap_value_flows_to_address_selector() -> None:
    pc = ProgramCounter()
    pc.load(0xFFF)
    pc.increment()

    assert pc.value == 0x000
    assert select_address(AddressSource.PC, pc=pc.value, ir_operand=0x123) == 0x000


@pytest.mark.parametrize(
    ("mode", "a", "b", "expected"),
    [
        (ALUMode.ADD, 0x00, 0x00, (0x00, True, False, False, False)),
        (ALUMode.ADD, 0x7F, 0x01, (0x80, False, False, True, True)),
        (ALUMode.ADD, 0xFF, 0x01, (0x00, True, True, False, False)),
        (ALUMode.ADD, 0x80, 0x80, (0x00, True, True, False, True)),
        (ALUMode.SUB, 0x00, 0x01, (0xFF, False, False, True, False)),
        (ALUMode.SUB, 0x80, 0x01, (0x7F, False, True, False, True)),
        (ALUMode.SUB, 0x7F, 0xFF, (0x80, False, False, True, True)),
        (ALUMode.SUB, 0x01, 0x01, (0x00, True, True, False, False)),
    ],
)
def test_alu_result_flows_to_flags_policy(
    mode: ALUMode,
    a: int,
    b: int,
    expected: tuple[int, bool, bool, bool, bool],
) -> None:
    alu_result = evaluate(mode, a, b)
    snapshot = latch_flags_for_alu_write(alu_result)
    result, zero, carry, sign, overflow = expected

    assert alu_result.result == result
    assert (alu_result.zero, alu_result.carry, alu_result.sign, alu_result.overflow) == (
        zero,
        carry,
        sign,
        overflow,
    )
    assert snapshot.values.zero is zero
    assert snapshot.values.carry is carry
    assert snapshot.values.sign is sign
    assert snapshot.values.overflow is overflow
    assert snapshot.defined == FlagsDefinedMask.all()
    assert alu_result.result == result


@pytest.mark.parametrize(
    ("address", "value"),
    [(0x000, 0x00), (0x001, 0x01), (0x7FF, 0x7F), (0x800, 0x80), (0xFFF, 0xFF)],
)
def test_sram_read_flows_to_single_data_bus_producer(address: int, value: int) -> None:
    memory = SRAM()
    memory.write(address, value)

    memory_value = memory.read(address)
    bus_value = resolve_data_bus([memory_value])

    assert bus_value == value
    assert memory.read(address) == value


def test_zero_byte_is_driven_and_no_producer_is_high_z() -> None:
    memory = SRAM()
    memory.write(0x000, 0x00)

    assert resolve_data_bus([memory.read(0x000)]) == 0x00
    assert resolve_data_bus([]) is None


def test_a_and_b_reset_independently_to_zero() -> None:
    a = FixedWidthRegister(width=8, reset_value=0x00)
    b = FixedWidthRegister(width=8, reset_value=0x00)
    a.load(0x12)
    b.load(0x34)

    a.reset()
    assert a.value == 0x00
    assert b.value == 0x34

    b.reset()
    assert b.value == 0x00


def test_address_components_reset_locally() -> None:
    pc = ProgramCounter()
    mar = MemoryAddressRegister()
    pc.load(0xABC)
    mar.load(0x123)

    pc.reset()
    assert pc.value == 0x000
    assert mar.value == 0x123

    mar.reset()
    assert mar.value == 0x000


def test_instruction_register_resets_both_views_locally() -> None:
    ir = InstructionRegister()
    ir.load_high(0xAF)
    ir.load_low(0xFF)

    ir.reset()

    assert ir.high == 0x00
    assert ir.low == 0x00
    assert ir.opcode == 0x0
    assert ir.operand == 0x000


def test_microstep_and_halt_reset_locally() -> None:
    microstep = MicrostepCounter()
    halt = HaltLatch()
    microstep.increment()
    halt.latch()

    halt.reset()
    assert halt.is_halted is False
    assert microstep.value == 0x1

    microstep.reset()
    assert microstep.value == 0x0


def test_flags_reset_is_canonical_immutable_snapshot() -> None:
    reset_flags = FlagsSnapshot.reset()

    assert reset_flags.values.zero is False
    assert reset_flags.values.carry is False
    assert reset_flags.values.sign is False
    assert reset_flags.values.overflow is False
    assert reset_flags.defined == FlagsDefinedMask.all()


def test_sram_persists_across_independent_component_resets() -> None:
    memory = SRAM()
    memory.write(0x123, 0xAB)
    a = FixedWidthRegister(width=8, reset_value=0x00)
    pc = ProgramCounter()
    ir = InstructionRegister()
    mar = MemoryAddressRegister()
    microstep = MicrostepCounter()
    halt = HaltLatch()

    a.load(0x42)
    pc.load(0xABC)
    ir.load_high(0x15)
    ir.load_low(0xAA)
    mar.load(0x123)
    microstep.increment()
    halt.latch()

    a.reset()
    pc.reset()
    ir.reset()
    mar.reset()
    microstep.reset()
    halt.reset()

    assert memory.read(0x123) == 0xAB
