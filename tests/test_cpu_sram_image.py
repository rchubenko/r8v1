import pytest

from cpu import SRAM, SRAM_SIZE, InvalidMemoryImage


def test_replace_zero_image_clears_previous_non_zero_contents() -> None:
    memory = SRAM()
    for address in (0x000, 0x123, 0x800, 0xFFF):
        memory.write(address, 0xA5)

    memory.replace_image(bytes(SRAM_SIZE))

    assert all(memory.read(address) == 0x00 for address in range(SRAM_SIZE))


def test_replace_patterned_image_maps_every_offset_to_same_address() -> None:
    image = bytes(address & 0xFF for address in range(SRAM_SIZE))
    memory = SRAM()

    memory.replace_image(image)

    assert all(memory.read(address) == image[address] for address in range(SRAM_SIZE))
    for address in (0x000, 0x001, 0x7FF, 0x800, 0xFFE, 0xFFF):
        assert memory.read(address) == image[address]


def test_second_replacement_completely_overwrites_first_image() -> None:
    first = bytes((address * 3) & 0xFF for address in range(SRAM_SIZE))
    second = bytes((0xFF - address) & 0xFF for address in range(SRAM_SIZE))
    memory = SRAM()

    memory.replace_image(first)
    memory.replace_image(second)

    assert all(memory.read(address) == second[address] for address in range(SRAM_SIZE))


@pytest.mark.parametrize(
    "image",
    [b"", bytes(1), bytes(SRAM_SIZE - 1), bytes(SRAM_SIZE + 1), bytes(SRAM_SIZE * 2)],
)
def test_invalid_image_length_is_rejected_atomically(image: bytes) -> None:
    existing = bytes((address * 7) & 0xFF for address in range(SRAM_SIZE))
    memory = SRAM()
    memory.replace_image(existing)

    with pytest.raises(
        InvalidMemoryImage,
        match=f"exactly {SRAM_SIZE} bytes; got {len(image)}",
    ):
        memory.replace_image(image)

    assert all(memory.read(address) == existing[address] for address in range(SRAM_SIZE))


@pytest.mark.parametrize("invalid", ["0x00", [0] * SRAM_SIZE, None, 0, object()])
def test_invalid_image_type_is_rejected_atomically(invalid: object) -> None:
    existing = bytes((address * 11) & 0xFF for address in range(SRAM_SIZE))
    memory = SRAM()
    memory.replace_image(existing)

    with pytest.raises(TypeError, match="image must be bytes or bytearray"):
        memory.replace_image(invalid)

    assert all(memory.read(address) == existing[address] for address in range(SRAM_SIZE))


def test_bytearray_input_is_defensively_copied() -> None:
    image = bytearray((address * 5) & 0xFF for address in range(SRAM_SIZE))
    memory = SRAM()

    memory.replace_image(image)
    expected_first = image[0]
    image[0] = (expected_first + 1) & 0xFF

    assert memory.read(0x000) == expected_first
    assert memory.read(0xFFF) == image[0xFFF]


def test_replacement_preserves_full_image_until_explicit_write() -> None:
    image = bytes((address * 13) & 0xFF for address in range(SRAM_SIZE))
    memory = SRAM()
    memory.replace_image(image)

    assert memory.read(0x123) == image[0x123]
    memory.write(0x123, 0x00)
    assert memory.read(0x123) == 0x00
    assert memory.read(0x124) == image[0x124]


def test_repeated_replacement_and_instance_isolation() -> None:
    image = bytes((address ^ 0xAA) & 0xFF for address in range(SRAM_SIZE))
    first = SRAM()
    second = SRAM()

    first.replace_image(image)
    first.replace_image(image)

    assert first.read(0x123) == image[0x123]
    assert second.read(0x123) == 0x00
