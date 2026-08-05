import pytest

from cpu import DataBusContention, InvalidComponentValue, resolve_data_bus


def test_zero_producers_are_high_z() -> None:
    assert resolve_data_bus([]) is None
    assert resolve_data_bus(()) is None
    assert resolve_data_bus(iter(())) is None


@pytest.mark.parametrize("value", [0x00, 0x01, 0x7F, 0x80, 0xFF])
def test_single_producer_returns_unchanged_byte(value: int) -> None:
    assert resolve_data_bus([value]) == value


def test_single_generator_producer_is_supported() -> None:
    assert resolve_data_bus(value for value in [0x42]) == 0x42


@pytest.mark.parametrize(
    "producers",
    [
        [0x12, 0x34],
        [0x42, 0x42],
        [0x00, 0x01, 0xFF],
    ],
)
def test_multiple_producers_raise_contention(producers: list[int]) -> None:
    with pytest.raises(DataBusContention, match=f"{len(producers)} producers"):
        resolve_data_bus(producers)


def test_contention_message_contains_values_in_input_order() -> None:
    with pytest.raises(DataBusContention, match=r"0x12, 0x34"):
        resolve_data_bus([0x12, 0x34])


@pytest.mark.parametrize("invalid", [-1, 0x100, True, False, "0x42", None])
def test_invalid_first_producer_raises_project_exception(invalid: object) -> None:
    with pytest.raises(InvalidComponentValue):
        resolve_data_bus([invalid, 0x42])


@pytest.mark.parametrize("invalid", [-1, 0x100, True, False, "0x42", None])
def test_invalid_later_producer_raises_project_exception(invalid: object) -> None:
    with pytest.raises(InvalidComponentValue):
        resolve_data_bus([0x42, invalid])


def test_validation_precedes_contention_detection() -> None:
    with pytest.raises(InvalidComponentValue):
        resolve_data_bus([0x12, 0x100, 0x34])


def test_input_list_is_not_modified() -> None:
    producers = [0x12]

    assert resolve_data_bus(producers) == 0x12
    assert producers == [0x12]


def test_resolver_is_stateless_across_high_z_valid_and_contention_calls() -> None:
    assert resolve_data_bus([]) is None
    assert resolve_data_bus([0x42]) == 0x42

    with pytest.raises(DataBusContention):
        resolve_data_bus([0x12, 0x34])

    assert resolve_data_bus([0xFF]) == 0xFF
    assert resolve_data_bus([0x42]) == resolve_data_bus([0x42])
