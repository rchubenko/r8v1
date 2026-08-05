import pytest

from cpu import HaltLatch


def test_halt_latch_constructs_clear_with_boolean_state() -> None:
    halt = HaltLatch()

    assert halt.is_halted is False
    assert type(halt.is_halted) is bool


def test_halt_latch_constructor_has_no_configurable_arguments() -> None:
    with pytest.raises(TypeError):
        HaltLatch(True)  # type: ignore[call-arg]

    with pytest.raises(TypeError):
        HaltLatch(initial_state=True)  # type: ignore[call-arg]


def test_latch_sets_true_without_arguments() -> None:
    halt = HaltLatch()

    halt.latch()

    assert halt.is_halted is True
    assert type(halt.is_halted) is bool


def test_repeated_latch_is_idempotent() -> None:
    halt = HaltLatch()

    halt.latch()
    halt.latch()

    assert halt.is_halted is True


def test_halt_state_holds_until_reset() -> None:
    halt = HaltLatch()
    halt.latch()

    assert halt.is_halted is True
    assert halt.is_halted is True
    halt.latch()
    assert halt.is_halted is True


def test_reset_is_idempotent_from_clear_state() -> None:
    halt = HaltLatch()

    halt.reset()
    halt.reset()

    assert halt.is_halted is False


def test_reset_clears_latched_state() -> None:
    halt = HaltLatch()
    halt.latch()

    halt.reset()

    assert halt.is_halted is False


def test_latch_after_reset_sets_state_again() -> None:
    halt = HaltLatch()
    halt.latch()
    halt.reset()

    halt.latch()

    assert halt.is_halted is True


def test_halt_latch_state_is_read_only() -> None:
    halt = HaltLatch()

    with pytest.raises(AttributeError):
        halt.is_halted = True  # type: ignore[misc]

    assert halt.is_halted is False


def test_halt_latch_instances_are_isolated() -> None:
    first = HaltLatch()
    second = HaltLatch()

    first.latch()

    assert first.is_halted is True
    assert second.is_halted is False

    second.latch()
    first.reset()

    assert first.is_halted is False
    assert second.is_halted is True
