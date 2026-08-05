import pytest

from cpu import InvalidComponentValue, MemoryAddressRegister


def test_mar_has_fixed_width_and_reset_value() -> None:
    mar = MemoryAddressRegister()

    assert mar.width == 12
    assert mar.reset_value == 0x000
    assert mar.value == 0x000


def test_mar_constructor_does_not_accept_custom_width_or_reset_value() -> None:
    with pytest.raises(TypeError):
        MemoryAddressRegister(width=8)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        MemoryAddressRegister(reset_value=0x123)  # type: ignore[call-arg]


@pytest.mark.parametrize("value", [0x000, 0x001, 0x7FF, 0x800, 0xFFF])
def test_mar_load_accepts_valid_addresses_without_modification(value: int) -> None:
    mar = MemoryAddressRegister()

    mar.load(value)

    assert mar.value == value


@pytest.mark.parametrize("invalid", [-1, 0x1000, True, False, "0x123", None])
def test_mar_invalid_load_raises_and_preserves_state(invalid: object) -> None:
    mar = MemoryAddressRegister()
    mar.load(0xABC)

    with pytest.raises(InvalidComponentValue):
        mar.load(invalid)

    assert mar.value == 0xABC


def test_mar_invalid_load_error_contains_address_context() -> None:
    mar = MemoryAddressRegister()

    with pytest.raises(InvalidComponentValue, match="address.*0x0..FFF"):
        mar.load(0x1000)


def test_mar_reset_restores_zero_deterministically() -> None:
    mar = MemoryAddressRegister()

    mar.load(0xABC)
    mar.reset()
    assert mar.value == 0x000

    mar.load(0x123)
    mar.reset()
    assert mar.value == 0x000


def test_mar_instances_do_not_share_state() -> None:
    first = MemoryAddressRegister()
    second = MemoryAddressRegister()

    first.load(0xABC)
    assert first.value == 0xABC
    assert second.value == 0x000

    first.reset()
    assert first.value == 0x000
    assert second.value == 0x000
