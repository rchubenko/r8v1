import pytest

from cpu import InstructionRegister, InvalidComponentValue


def test_instruction_register_starts_zeroed() -> None:
    ir = InstructionRegister()

    assert ir.high == 0x00
    assert ir.low == 0x00
    assert ir.opcode == 0x0
    assert ir.operand == 0x000


def test_instruction_register_constructor_does_not_accept_custom_parameters() -> None:
    with pytest.raises(TypeError):
        InstructionRegister(width=8)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        InstructionRegister(reset_value=0x0000)  # type: ignore[call-arg]


@pytest.mark.parametrize("value", [0x00, 0x01, 0x7F, 0x80, 0xFF])
def test_load_high_accepts_valid_bytes(value: int) -> None:
    ir = InstructionRegister()

    ir.load_high(value)

    assert ir.high == value


@pytest.mark.parametrize("value", [0x00, 0x01, 0x7F, 0x80, 0xFF])
def test_load_low_accepts_valid_bytes(value: int) -> None:
    ir = InstructionRegister()

    ir.load_low(value)

    assert ir.low == value


@pytest.mark.parametrize("invalid", [-1, 0x100, True, False, "0x12", None])
def test_invalid_load_high_raises_and_preserves_both_bytes(invalid: object) -> None:
    ir = InstructionRegister()
    ir.load_high(0xAB)
    ir.load_low(0xCD)

    with pytest.raises(InvalidComponentValue):
        ir.load_high(invalid)

    assert ir.high == 0xAB
    assert ir.low == 0xCD


@pytest.mark.parametrize("invalid", [-1, 0x100, True, False, "0x12", None])
def test_invalid_load_low_raises_and_preserves_both_bytes(invalid: object) -> None:
    ir = InstructionRegister()
    ir.load_high(0xAB)
    ir.load_low(0xCD)

    with pytest.raises(InvalidComponentValue):
        ir.load_low(invalid)

    assert ir.high == 0xAB
    assert ir.low == 0xCD


def test_invalid_load_error_contains_byte_context() -> None:
    ir = InstructionRegister()

    with pytest.raises(InvalidComponentValue, match="byte.*0x0..FF"):
        ir.load_high(0x100)


def test_high_and_low_loads_are_independent() -> None:
    ir = InstructionRegister()
    ir.load_low(0xCD)
    ir.load_high(0xAB)

    assert ir.high == 0xAB
    assert ir.low == 0xCD

    ir.load_high(0x12)
    assert ir.high == 0x12
    assert ir.low == 0xCD

    ir.load_low(0x34)
    assert ir.high == 0x12
    assert ir.low == 0x34


@pytest.mark.parametrize(
    ("high", "expected_opcode"),
    [(0x00, 0x0), (0x1F, 0x1), (0xA5, 0xA), (0xB0, 0xB), (0xE0, 0xE), (0xF0, 0xF), (0xFF, 0xF)],
)
def test_opcode_is_extracted_from_high_nibble(high: int, expected_opcode: int) -> None:
    ir = InstructionRegister()
    ir.load_high(high)

    assert ir.opcode == expected_opcode


@pytest.mark.parametrize(
    ("high", "low", "expected_operand"),
    [
        (0x00, 0x00, 0x000),
        (0x0F, 0xFF, 0xFFF),
        (0xA0, 0x00, 0x000),
        (0xAF, 0xFF, 0xFFF),
        (0x15, 0xAA, 0x5AA),
        (0xF1, 0x23, 0x123),
    ],
)
def test_operand_is_assembled_from_low_high_nibble_and_low_byte(
    high: int, low: int, expected_operand: int
) -> None:
    ir = InstructionRegister()
    ir.load_high(high)
    ir.load_low(low)

    assert ir.operand == expected_operand


def test_views_update_dynamically() -> None:
    ir = InstructionRegister()
    ir.load_high(0x15)
    ir.load_low(0xAA)

    assert ir.opcode == 0x1
    assert ir.operand == 0x5AA

    ir.load_high(0xF1)
    assert ir.opcode == 0xF
    assert ir.operand == 0x1AA

    ir.load_low(0x45)
    assert ir.opcode == 0xF
    assert ir.operand == 0x145


def test_reserved_opcodes_are_returned_without_interpretation() -> None:
    ir = InstructionRegister()

    for opcode in [0xB, 0xC, 0xD, 0xE]:
        ir.load_high(opcode << 4)
        assert ir.opcode == opcode


def test_reset_clears_both_bytes_and_views_deterministically() -> None:
    ir = InstructionRegister()
    ir.load_high(0xAF)
    ir.load_low(0xFF)

    ir.reset()
    assert ir.high == 0x00
    assert ir.low == 0x00
    assert ir.opcode == 0x0
    assert ir.operand == 0x000

    ir.load_high(0xF1)
    ir.load_low(0x23)
    ir.reset()
    ir.reset()
    assert ir.high == 0x00
    assert ir.low == 0x00
    assert ir.opcode == 0x0
    assert ir.operand == 0x000


def test_instruction_register_instances_do_not_share_state() -> None:
    first = InstructionRegister()
    second = InstructionRegister()

    first.load_high(0xAB)
    first.load_low(0xCD)
    assert first.high == 0xAB
    assert first.low == 0xCD
    assert second.high == 0x00
    assert second.low == 0x00

    first.reset()
    assert first.high == 0x00
    assert first.low == 0x00
    assert second.high == 0x00
    assert second.low == 0x00
