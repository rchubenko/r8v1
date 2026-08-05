from dataclasses import FrozenInstanceError

import pytest

from cpu import AddResult, InvalidComponentValue, add


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (0x00, 0x00, 0x00),
        (0x00, 0x01, 0x01),
        (0x01, 0x01, 0x02),
        (0x12, 0x34, 0x46),
        (0x7F, 0x00, 0x7F),
        (0x80, 0x00, 0x80),
        (0xFF, 0x00, 0xFF),
        (0xFF, 0x01, 0x00),
        (0x80, 0x80, 0x00),
        (0xFF, 0xFF, 0xFE),
        (0x7F, 0x01, 0x80),
    ],
)
def test_add_basic_arithmetic_and_wrap(a: int, b: int, expected: int) -> None:
    assert add(a, b).result == expected


@pytest.mark.parametrize(
    ("a", "b", "expected_carry"),
    [
        (0x00, 0x00, False),
        (0xFF, 0x01, True),
        (0x80, 0x80, True),
        (0xFF, 0xFF, True),
        (0x7F, 0x01, False),
    ],
)
def test_add_carry(a: int, b: int, expected_carry: bool) -> None:
    assert add(a, b).carry is expected_carry


@pytest.mark.parametrize(
    ("a", "b", "expected_zero"),
    [(0x00, 0x00, True), (0xFF, 0x01, True), (0x01, 0x01, False)],
)
def test_add_zero(a: int, b: int, expected_zero: bool) -> None:
    assert add(a, b).zero is expected_zero


@pytest.mark.parametrize(
    ("a", "b", "expected_sign"),
    [(0x7F, 0x00, False), (0x80, 0x00, True), (0xFF, 0x00, True), (0x00, 0x00, False)],
)
def test_add_sign(a: int, b: int, expected_sign: bool) -> None:
    assert add(a, b).sign is expected_sign


@pytest.mark.parametrize(
    ("a", "b", "expected_overflow"),
    [
        (0x7F, 0x01, True),
        (0x40, 0x40, True),
        (0x80, 0x80, True),
        (0x80, 0xFF, True),
        (0xFF, 0x01, False),
        (0x7F, 0xFF, False),
        (0x01, 0x01, False),
    ],
)
def test_add_signed_overflow(a: int, b: int, expected_overflow: bool) -> None:
    assert add(a, b).overflow is expected_overflow


@pytest.mark.parametrize("invalid", [-1, 0x100, True, False, "0x12", None])
def test_invalid_first_operand_raises_project_exception(invalid: object) -> None:
    with pytest.raises(InvalidComponentValue):
        add(invalid, 0x00)


@pytest.mark.parametrize("invalid", [-1, 0x100, True, False, "0x12", None])
def test_invalid_second_operand_raises_project_exception(invalid: object) -> None:
    with pytest.raises(InvalidComponentValue):
        add(0x00, invalid)


def test_invalid_input_error_contains_byte_context() -> None:
    with pytest.raises(InvalidComponentValue, match="byte.*0x0..FF"):
        add(0x100, 0x00)


def test_add_result_is_immutable() -> None:
    result = add(0x12, 0x34)

    with pytest.raises(FrozenInstanceError):
        result.result = 0x00  # type: ignore[misc]

    assert result == AddResult(result=0x46, zero=False, carry=False, sign=False, overflow=False)


def test_add_is_stateless_across_calls() -> None:
    first = add(0x12, 0x34)
    second = add(0xFF, 0x01)

    assert first.result == 0x46
    assert second.result == 0x00
    assert first.result == 0x46


def test_add_exhaustive_8_bit_input_matrix() -> None:
    for a in range(0x100):
        for b in range(0x100):
            wide_sum = a + b
            expected_result = wide_sum & 0xFF
            expected_zero = expected_result == 0
            expected_carry = wide_sum > 0xFF
            expected_sign = bool(expected_result & 0x80)
            expected_overflow = bool(((a ^ b) & 0x80) == 0 and ((a ^ expected_result) & 0x80) != 0)

            actual = add(a, b)
            assert actual == AddResult(
                result=expected_result,
                zero=expected_zero,
                carry=expected_carry,
                sign=expected_sign,
                overflow=expected_overflow,
            )
