import pytest

from cpu import SRAM_SIZE, FlagsDefinedMask, FlagsSnapshot, FlagValues, InvalidMemoryImage
from emulator import ArchitecturalState


def _image(seed: int = 0) -> bytes:
    return bytes((address * 37 + seed) % 256 for address in range(SRAM_SIZE))


def _prepare_modified_state(state: ArchitecturalState) -> None:
    state._a.load(0xA5)
    state._pc.load(0xABC)
    state._ir.load_high(0xF1)
    state._ir.load_low(0x23)
    state._flags = FlagsSnapshot(
        FlagValues(True, True, True, True),
        FlagsDefinedMask.zero_and_sign(),
    )
    state._memory.write(0x000, 0x11)
    state._memory.write(0xFFF, 0x22)
    state._halt.latch()


def test_valid_image_replaces_the_complete_sram() -> None:
    state = ArchitecturalState()
    image = _image(seed=13)

    state.load_image(image)

    assert state.memory_image == image
    assert state.memory_image[0x000] == image[0x000]
    assert state.memory_image[0x456] == image[0x456]
    assert state.memory_image[0xFFF] == image[0xFFF]


def test_valid_image_replaces_previous_contents_without_residue() -> None:
    state = ArchitecturalState()
    state._memory.write(0x000, 0xFF)
    state._memory.write(0x456, 0xFF)
    state._memory.write(0xFFF, 0xFF)
    image = _image(seed=29)

    state.load_image(image)

    assert state.memory_image == image


@pytest.mark.parametrize("size", [0, 1, 4095, 4097, 8192])
def test_invalid_image_size_is_rejected_without_partial_mutation(size: int) -> None:
    state = ArchitecturalState()
    state.load_image(_image(seed=7))
    before = state.memory_image

    with pytest.raises(InvalidMemoryImage):
        state.load_image(bytes(size))

    assert state.memory_image == before


def test_load_image_preserves_all_other_architectural_fields() -> None:
    state = ArchitecturalState()
    _prepare_modified_state(state)
    before = (
        state.a,
        state.pc,
        state.irh,
        state.irl,
        state.flags,
        state.flags_defined_mask,
        state.halt_state,
    )

    state.load_image(_image(seed=41))

    assert (
        state.a,
        state.pc,
        state.irh,
        state.irl,
        state.flags,
        state.flags_defined_mask,
        state.halt_state,
    ) == before


def test_load_image_accepts_bytearray_and_does_not_retain_mutable_input() -> None:
    state = ArchitecturalState()
    image = bytearray(_image(seed=53))

    state.load_image(image)
    image[0] = (image[0] + 1) % 256

    assert state.memory_image[0] != image[0]


def test_reset_after_image_load_preserves_loaded_sram() -> None:
    state = ArchitecturalState()
    image = _image(seed=67)

    state.load_image(image)
    state.reset()

    assert state.memory_image == image
    assert state.a == 0x00
    assert state.pc == 0x000
    assert state.halt_state is False


def test_image_loading_one_state_does_not_affect_another() -> None:
    first = ArchitecturalState()
    second = ArchitecturalState()
    image = _image(seed=79)

    first.load_image(image)

    assert first.memory_image == image
    assert second.memory_image == bytes(SRAM_SIZE)
