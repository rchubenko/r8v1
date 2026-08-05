from dataclasses import FrozenInstanceError

import pytest

from cpu import InvalidComponentValue, SubtractResult, subtract


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (0x00, 0x00, 0x00),
        (0x01, 0x00, 0x01),
        (0x01, 0x01, 0x00),
        (0x12, 0x02, 0x10),
        (0x7F, 0x00, 0x7F),
        (0x80, 0x00, 0x80),
        (0xFF, 0x00, 0xFF),
        (0x00, 0x01, 0xFF),
        (0x80, 0x01, 0x7F),
        (0x7F, 0xFF, 0x80),
    ],
)
def test_sub_basic_arithmetic_and_underflow(a: int, b: int, expected: int) -> None:
    assert subtract(a, b).result == expected


@pytest.mark.parametrize(
    ("a", "b", "expected_carry"),
    [
        (0x00, 0x00, True),
        (0x00, 0x01, False),
        (0x01, 0x01, True),
        (0x02, 0x01, True),
        (0x7F, 0xFF, False),
        (0xFF, 0x01, True),
    ],
)
def test_sub_carry_means_no_borrow(a: int, b: int, expected_carry: bool) -> None:
    assert subtract(a, b).carry is expected_carry


@pytest.mark.parametrize(
    ("a", "b", "expected_zero"),
    [(0x00, 0x00, True), (0x01, 0x01, True), (0x01, 0x00, False)],
)
def test_sub_zero(a: int, b: int, expected_zero: bool) -> None:
    assert subtract(a, b).zero is expected_zero


@pytest.mark.parametrize(
    ("a", "b", "expected_sign"),
    [(0x7F, 0x00, False), (0x80, 0x00, True), (0x00, 0x01, True), (0x00, 0x00, False)],
)
def test_sub_sign(a: int, b: int, expected_sign: bool) -> None:
    assert subtract(a, b).sign is expected_sign


@pytest.mark.parametrize(
    ("a", "b", "expected_overflow"),
    [
        (0x80, 0x01, True),
        (0x7F, 0xFF, True),
        (0x00, 0x01, False),
        (0x80, 0x80, False),
        (0x7F, 0x01, False),
        (0xFF, 0x01, False),
    ],
)
def test_sub_signed_overflow(a: int, b: int, expected_overflow: bool) -> None:
    assert subtract(a, b).overflow is expected_overflow


@pytest.mark.parametrize("invalid", [-1, 0x100, True, False, "0x12", None])
def test_invalid_first_operand_raises_project_exception(invalid: object) -> None:
    with pytest.raises(InvalidComponentValue):
        subtract(invalid, 0x00)


@pytest.mark.parametrize("invalid", [-1, 0x100, True, False, "0x12", None])
def test_invalid_second_operand_raises_project_exception(invalid: object) -> None:
    with pytest.raises(InvalidComponentValue):
        subtract(0x00, invalid)


def test_invalid_input_error_contains_byte_context() -> None:
    with pytest.raises(InvalidComponentValue, match="byte.*0x0..FF"):
        subtract(0x100, 0x00)


def test_subtract_result_is_immutable() -> None:
    result = subtract(0x80, 0x01)

    with pytest.raises(FrozenInstanceError):
        result.result = 0x00  # type: ignore[misc]

    assert result == SubtractResult(result=0x7F, zero=False, carry=True, sign=False, overflow=True)


def test_subtract_is_stateless_across_calls() -> None:
    first = subtract(0x80, 0x01)
    second = subtract(0x00, 0x01)

    assert first.result == 0x7F
    assert second.result == 0xFF
    assert first.result == 0x7F


def test_sub_exhaustive_8_bit_input_matrix() -> None:
    for a in range(0x100):
        for b in range(0x100):
            wide_difference = a - b
            expected_result = wide_difference & 0xFF
            expected_zero = expected_result == 0
            expected_carry = a >= b
            expected_sign = bool(expected_result & 0x80)
            expected_overflow = bool(((a ^ b) & 0x80) != 0 and ((a ^ expected_result) & 0x80) != 0)

            actual = subtract(a, b)
            assert actual == SubtractResult(
                result=expected_result,
                zero=expected_zero,
                carry=expected_carry,
                sign=expected_sign,
                overflow=expected_overflow,
            )
