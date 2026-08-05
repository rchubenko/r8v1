import pytest

from cpu import InvalidComponentValue, MicrostepCounter


def test_microstep_counter_construction() -> None:
    counter = MicrostepCounter()

    assert counter.width == 4
    assert counter.reset_value == 0
    assert counter.value == 0


def test_microstep_counter_constructor_has_no_configurable_arguments() -> None:
    with pytest.raises(TypeError):
        MicrostepCounter(4)  # type: ignore[call-arg]

    with pytest.raises(TypeError):
        MicrostepCounter(reset_value=1)  # type: ignore[call-arg]


def test_increment_traverses_full_t0_to_t15_sequence() -> None:
    counter = MicrostepCounter()

    for expected in range(1, 16):
        counter.increment()
        assert counter.value == expected


def test_increment_wraps_t15_to_t0() -> None:
    counter = MicrostepCounter()
    for _ in range(15):
        counter.increment()

    counter.increment()

    assert counter.value == 0


def test_sixteen_increments_return_to_t0_and_seventeen_reach_t1() -> None:
    counter = MicrostepCounter()

    for _ in range(16):
        counter.increment()
    assert counter.value == 0

    counter.increment()
    assert counter.value == 1


def test_multiple_increment_cycles_are_deterministic() -> None:
    counter = MicrostepCounter()

    for _ in range(16 * 3 + 7):
        counter.increment()

    assert counter.value == 7


@pytest.mark.parametrize("increments", [0, 1, 7, 15])
def test_return_to_t0_is_idempotent_from_representative_states(increments: int) -> None:
    counter = MicrostepCounter()
    for _ in range(increments):
        counter.increment()

    counter.return_to_t0()
    counter.return_to_t0()

    assert counter.value == 0
    counter.increment()
    assert counter.value == 1


def test_hold_is_implicit_when_no_transition_operation_is_called() -> None:
    counter = MicrostepCounter()
    for _ in range(7):
        counter.increment()

    first_read = counter.value
    second_read = counter.value

    assert first_read == second_read == 7


def test_reset_returns_t0_after_increment_and_wraparound() -> None:
    counter = MicrostepCounter()
    for _ in range(16):
        counter.increment()
    counter.increment()

    counter.reset()

    assert counter.value == 0
    counter.reset()
    assert counter.value == 0


def test_reset_after_return_to_t0_is_deterministic() -> None:
    counter = MicrostepCounter()
    for _ in range(11):
        counter.increment()
    counter.return_to_t0()

    counter.reset()

    assert counter.value == 0


def test_instances_are_isolated() -> None:
    first = MicrostepCounter()
    second = MicrostepCounter()

    first.increment()
    first.return_to_t0()

    assert first.value == 0
    assert second.value == 0


def test_inherited_load_keeps_strict_nibble_validation() -> None:
    counter = MicrostepCounter()

    counter.load(0xF)
    assert counter.value == 0xF

    with pytest.raises(InvalidComponentValue):
        counter.load(0x10)
    assert counter.value == 0xF


def test_many_increments_preserve_four_bit_range() -> None:
    counter = MicrostepCounter()

    for _ in range(1000):
        counter.increment()
        assert 0 <= counter.value <= 0xF
