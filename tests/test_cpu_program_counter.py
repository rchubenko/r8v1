import pytest

from cpu import InvalidComponentValue, ProgramCounter


def test_program_counter_has_fixed_width_and_reset_value() -> None:
    pc = ProgramCounter()

    assert pc.width == 12
    assert pc.reset_value == 0x000
    assert pc.value == 0x000


def test_program_counter_constructor_does_not_accept_custom_width_or_reset_value() -> None:
    with pytest.raises(TypeError):
        ProgramCounter(width=8)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        ProgramCounter(reset_value=0x123)  # type: ignore[call-arg]


@pytest.mark.parametrize("value", [0x000, 0x001, 0x7FF, 0x800, 0xFFF])
def test_parallel_load_accepts_valid_addresses_without_modification(value: int) -> None:
    pc = ProgramCounter()

    pc.load(value)

    assert pc.value == value


@pytest.mark.parametrize("invalid", [-1, 0x1000, True, False, "0x123", None])
def test_invalid_parallel_load_raises_and_preserves_state(invalid: object) -> None:
    pc = ProgramCounter()
    pc.load(0xABC)

    with pytest.raises(InvalidComponentValue):
        pc.load(invalid)

    assert pc.value == 0xABC


def test_invalid_parallel_load_error_contains_address_context() -> None:
    pc = ProgramCounter()

    with pytest.raises(InvalidComponentValue, match="address.*0x0..FFF"):
        pc.load(0x1000)


@pytest.mark.parametrize(
    ("loaded", "expected"),
    [(0x000, 0x001), (0x001, 0x002), (0x7FF, 0x800), (0xFFE, 0xFFF), (0xFFF, 0x000)],
)
def test_increment_advances_by_one_byte_modulo_4096(loaded: int, expected: int) -> None:
    pc = ProgramCounter()
    pc.load(loaded)

    pc.increment()

    assert pc.value == expected


def test_increment_remains_deterministic_after_wrap() -> None:
    pc = ProgramCounter()
    pc.load(0xFFF)

    pc.increment()
    pc.increment()

    assert pc.value == 0x001


def test_repeated_increment_advances_deterministically() -> None:
    pc = ProgramCounter()

    for _ in range(5):
        pc.increment()

    assert pc.value == 0x005


def test_reset_restores_zero_after_load_increment_and_wrap() -> None:
    pc = ProgramCounter()

    pc.load(0x123)
    pc.increment()
    pc.reset()
    assert pc.value == 0x000

    pc.load(0xFFF)
    pc.increment()
    pc.reset()
    assert pc.value == 0x000

    pc.reset()
    assert pc.value == 0x000


def test_program_counter_instances_do_not_share_state() -> None:
    first = ProgramCounter()
    second = ProgramCounter()

    first.load(0xABC)
    first.increment()
    assert first.value == 0xABD
    assert second.value == 0x000

    first.reset()
    assert first.value == 0x000
    assert second.value == 0x000
