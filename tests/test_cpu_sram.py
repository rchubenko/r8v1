import pytest

from cpu import SRAM, SRAM_SIZE, InvalidComponentValue


def test_sram_has_fixed_capacity_and_zero_filled_construction() -> None:
    memory = SRAM()

    assert SRAM_SIZE == 4096
    assert sum(memory.read(address) for address in range(SRAM_SIZE)) == 0
    assert not hasattr(memory, "reset")
    assert not hasattr(memory, "clear")


def test_sram_constructor_does_not_accept_configurable_size_or_contents() -> None:
    with pytest.raises(TypeError):
        SRAM(4096)  # type: ignore[call-arg]

    with pytest.raises(TypeError):
        SRAM(initial=b"\x00" * SRAM_SIZE)  # type: ignore[call-arg]


@pytest.mark.parametrize("address", [0x000, 0x001, 0x7FF, 0x800, 0xFFE, 0xFFF])
def test_new_sram_reads_zero_at_representative_addresses(address: int) -> None:
    assert SRAM().read(address) == 0x00


@pytest.mark.parametrize(
    ("address", "value"),
    [
        (0x000, 0x00),
        (0x001, 0x01),
        (0x123, 0x7F),
        (0x7FF, 0x80),
        (0x800, 0xAA),
        (0xFFF, 0xFF),
    ],
)
def test_valid_write_read_round_trip(address: int, value: int) -> None:
    memory = SRAM()

    memory.write(address, value)

    assert memory.read(address) == value


def test_write_changes_only_one_byte() -> None:
    memory = SRAM()
    memory.write(0x000, 0x11)
    memory.write(0x001, 0x22)
    memory.write(0xFFF, 0x33)

    memory.write(0x001, 0xAA)

    assert memory.read(0x000) == 0x11
    assert memory.read(0x001) == 0xAA
    assert memory.read(0x002) == 0x00
    assert memory.read(0xFFE) == 0x00
    assert memory.read(0xFFF) == 0x33


@pytest.mark.parametrize("address", [-1, 0x1000, True, False, "0x123", None])
def test_read_rejects_invalid_address(address: object) -> None:
    with pytest.raises(InvalidComponentValue):
        SRAM().read(address)


@pytest.mark.parametrize("address", [-1, 0x1000, True, False, "0x123", None])
def test_write_rejects_invalid_address(address: object) -> None:
    with pytest.raises(InvalidComponentValue):
        SRAM().write(address, 0x00)


@pytest.mark.parametrize("value", [-1, 0x100, True, False, "0x42", None])
def test_write_rejects_invalid_byte(value: object) -> None:
    with pytest.raises(InvalidComponentValue):
        SRAM().write(0x123, value)


def test_write_validates_address_before_value() -> None:
    with pytest.raises(InvalidComponentValue, match="address"):
        SRAM().write(-1, 0x100)


def test_failed_write_preserves_previous_value() -> None:
    memory = SRAM()
    memory.write(0x123, 0xAB)

    with pytest.raises(InvalidComponentValue):
        memory.write(0x1000, 0xCD)
    with pytest.raises(InvalidComponentValue):
        memory.write(0x123, 0x100)
    with pytest.raises(InvalidComponentValue):
        memory.write(-1, 0x100)

    assert memory.read(0x123) == 0xAB


def test_failed_write_does_not_change_neighbors() -> None:
    memory = SRAM()
    memory.write(0x122, 0x12)
    memory.write(0x123, 0x23)
    memory.write(0x124, 0x34)

    with pytest.raises(InvalidComponentValue):
        memory.write(0x123, -1)

    assert memory.read(0x122) == 0x12
    assert memory.read(0x123) == 0x23
    assert memory.read(0x124) == 0x34


def test_repeated_reads_and_writes_are_deterministic() -> None:
    memory = SRAM()

    assert memory.read(0x321) == memory.read(0x321) == 0x00
    memory.write(0x321, 0x5A)
    memory.write(0x321, 0x5A)
    assert memory.read(0x321) == memory.read(0x321) == 0x5A
    memory.write(0x321, 0x00)
    assert memory.read(0x321) == 0x00


def test_sram_instances_have_independent_storage() -> None:
    first = SRAM()
    second = SRAM()

    first.write(0x123, 0xAB)

    assert first.read(0x123) == 0xAB
    assert second.read(0x123) == 0x00
