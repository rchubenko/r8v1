import pytest

from cpu import FixedWidthRegister, InvalidComponentValue


@pytest.mark.parametrize(("width", "reset_value"), [(4, 0x0), (8, 0x00), (12, 0x000)])
def test_register_constructs_with_minimum_reset_value(width: int, reset_value: int) -> None:
    register = FixedWidthRegister(width=width, reset_value=reset_value)

    assert register.width == width
    assert register.reset_value == reset_value
    assert register.value == reset_value


@pytest.mark.parametrize(("width", "reset_value"), [(4, 0xF), (8, 0xFF), (12, 0xFFF)])
def test_register_constructs_with_maximum_reset_value(width: int, reset_value: int) -> None:
    register = FixedWidthRegister(width=width, reset_value=reset_value)

    assert register.width == width
    assert register.reset_value == reset_value
    assert register.value == reset_value


@pytest.mark.parametrize(
    ("width", "reset_value", "values"),
    [
        (4, 0x0, [0x0, 0x7, 0xF]),
        (8, 0x00, [0x00, 0x7F, 0xFF]),
        (12, 0x000, [0x000, 0x7FF, 0xFFF]),
    ],
)
def test_load_accepts_values_without_modification(
    width: int, reset_value: int, values: list[int]
) -> None:
    register = FixedWidthRegister(width=width, reset_value=reset_value)

    for value in values:
        register.load(value)
        assert register.value == value


@pytest.mark.parametrize(
    ("width", "reset_value", "loaded"),
    [(4, 0x2, 0xD), (8, 0x12, 0xAB), (12, 0x123, 0xFED)],
)
def test_reset_restores_configured_value_deterministically(
    width: int, reset_value: int, loaded: int
) -> None:
    register = FixedWidthRegister(width=width, reset_value=reset_value)

    register.load(loaded)
    register.reset()
    assert register.value == reset_value

    register.load(loaded)
    register.reset()
    assert register.value == reset_value


@pytest.mark.parametrize("width", [4, 8, 12])
@pytest.mark.parametrize("invalid", [-1, 0x1000, True, False, "1", None])
def test_invalid_reset_value_raises_project_exception(width: int, invalid: object) -> None:
    with pytest.raises(InvalidComponentValue):
        FixedWidthRegister(width=width, reset_value=invalid)


@pytest.mark.parametrize("width", [0, -1, 1, 16, True, False, "8", None])
def test_unsupported_width_raises_project_exception(width: object) -> None:
    with pytest.raises(InvalidComponentValue, match="width"):
        FixedWidthRegister(width=width, reset_value=0)


@pytest.mark.parametrize(
    ("width", "reset_value", "invalid"),
    [
        (4, 0x7, -1),
        (4, 0x7, 0x10),
        (8, 0x42, -1),
        (8, 0x42, 0x100),
        (12, 0x420, -1),
        (12, 0x420, 0x1000),
        (8, 0x42, True),
        (8, 0x42, False),
        (8, 0x42, "1"),
        (8, 0x42, None),
    ],
)
def test_invalid_load_raises_and_preserves_current_value(
    width: int, reset_value: int, invalid: object
) -> None:
    register = FixedWidthRegister(width=width, reset_value=reset_value)
    register.load(reset_value)

    with pytest.raises(InvalidComponentValue):
        register.load(invalid)

    assert register.value == reset_value


def test_invalid_load_error_contains_register_context() -> None:
    register = FixedWidthRegister(width=8, reset_value=0x42)

    with pytest.raises(InvalidComponentValue, match="byte.*0x0..FF"):
        register.load(0x100)


def test_register_instances_do_not_share_state() -> None:
    first = FixedWidthRegister(width=8, reset_value=0x00)
    second = FixedWidthRegister(width=8, reset_value=0x00)

    first.load(0x42)
    assert first.value == 0x42
    assert second.value == 0x00

    first.reset()
    assert first.value == 0x00
    assert second.value == 0x00


def test_value_and_reset_value_are_read_only() -> None:
    register = FixedWidthRegister(width=8, reset_value=0x12)

    with pytest.raises(AttributeError):
        register.value = 0x34  # type: ignore[misc]
    with pytest.raises(AttributeError):
        register.reset_value = 0x34  # type: ignore[misc]

    assert register.value == 0x12
    assert register.reset_value == 0x12
