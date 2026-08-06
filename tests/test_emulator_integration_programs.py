import pytest

from cpu import FlagsDefinedMask, FlagsSnapshot, FlagValues
from emulator import (
    ArchitecturalState,
    DecodedInstruction,
    DiagnosticIdentifier,
    DiagnosticSeverity,
    ExecutionPolicy,
    Opcode,
    StepResult,
)

IMAGE_SIZE = 4096


def _build_image(*placements: tuple[int, bytes]) -> bytes:
    image = bytearray(IMAGE_SIZE)
    for address, data in placements:
        image[address : address + len(data)] = data
    result = bytes(image)
    assert len(result) == IMAGE_SIZE
    return result


def _load(image: bytes, *, pc: int = 0x000) -> ArchitecturalState:
    state = ArchitecturalState()
    state.load_image(image)
    state._pc.load(pc)
    assert state.memory_image == image
    return state


def _run_exact(
    state: ArchitecturalState,
    count: int,
    *,
    policy: ExecutionPolicy | None = None,
    include_memory: bool = False,
) -> list[StepResult]:
    return [state.step(policy=policy, include_memory=include_memory) for _ in range(count)]


def _instruction_opcodes(results: list[StepResult]) -> list[Opcode]:
    opcodes: list[Opcode] = []
    for result in results:
        if result.instruction is None:
            raise AssertionError("expected an executed instruction")
        opcodes.append(result.instruction.opcode)
    return opcodes


def _run_until_halt(
    state: ArchitecturalState,
    max_steps: int,
    *,
    policy: ExecutionPolicy | None = None,
) -> list[StepResult]:
    results: list[StepResult] = []
    for _ in range(max_steps):
        result = state.step(policy=policy)
        results.append(result)
        if result.post_state.halt_state:
            break
    assert results[-1].post_state.halt_state is True
    assert len(results) <= max_steps
    return results


def _assert_final(
    result: StepResult,
    *,
    a: int,
    pc: int,
    irh: int,
    irl: int,
    flags: FlagsSnapshot,
    mask: FlagsDefinedMask,
    halt: bool,
    diagnostic: DiagnosticIdentifier | None,
    memory: bytes | None = None,
) -> None:
    snapshot = result.post_state
    assert snapshot.a == a
    assert snapshot.pc == pc
    assert snapshot.irh == irh
    assert snapshot.irl == irl
    assert snapshot.flags == flags
    assert snapshot.flags_defined_mask == mask
    assert snapshot.halt_state is halt
    if memory is not None:
        assert snapshot.memory == memory
    if diagnostic is None:
        assert result.diagnostic is None
    else:
        assert result.diagnostic is not None
        assert result.diagnostic.identifier is diagnostic


ARITHMETIC_IMAGE = _build_image(
    (0x000, bytes([0x10, 0x05, 0x30, 0x10, 0x40, 0x11, 0x50, 0x12, 0xF0, 0x00])),
    (0x010, bytes([0xFB, 0x01, 0x00])),
)


def test_arithmetic_program_has_exact_encoding_and_final_snapshot() -> None:
    state = _load(ARITHMETIC_IMAGE)
    results = _run_exact(state, 5, include_memory=True)

    assert ARITHMETIC_IMAGE[:10] == bytes(
        [0x10, 0x05, 0x30, 0x10, 0x40, 0x11, 0x50, 0x12, 0xF0, 0x00]
    )
    assert [result.instruction for result in results] == [
        DecodedInstruction(Opcode.LDI, 0x005),
        DecodedInstruction(Opcode.ADD, 0x010),
        DecodedInstruction(Opcode.SUB, 0x011),
        DecodedInstruction(Opcode.STA, 0x012),
        DecodedInstruction(Opcode.HLT, 0x000),
    ]
    assert [result.diagnostic for result in results] == [None] * 5
    assert results[1].post_state.a == 0x00
    assert results[1].post_state.flags == FlagsSnapshot(
        FlagValues(True, True, False, False), FlagsDefinedMask.all()
    )
    assert results[2].post_state.a == 0xFF
    assert results[2].post_state.flags == FlagsSnapshot(
        FlagValues(False, False, True, False), FlagsDefinedMask.all()
    )
    final_memory = bytearray(ARITHMETIC_IMAGE)
    final_memory[0x012] = 0xFF
    _assert_final(
        results[-1],
        a=0xFF,
        pc=0x00A,
        irh=0xF0,
        irl=0x00,
        flags=FlagsSnapshot(FlagValues(False, False, True, False), FlagsDefinedMask.all()),
        mask=FlagsDefinedMask.all(),
        halt=True,
        diagnostic=None,
        memory=bytes(final_memory),
    )


DEFINED_BRANCH_IMAGE = _build_image(
    (0x000, bytes([0x10, 0x00, 0x80, 0x09, 0x1E, 0xEE, 0xF0, 0x00])),
    (0x009, bytes([0x10, 0xFF, 0x90, 0x15])),
    (0x015, bytes([0x10, 0xFF, 0x31, 0x00, 0x70, 0x21, 0x10, 0x01, 0xF0, 0x00])),
    (0x100, bytes([0x01])),
    (0x021, bytes([0x10, 0xA0, 0xF0, 0x00])),
)


def test_defined_branch_program_skips_instructions_and_reaches_odd_targets() -> None:
    state = _load(DEFINED_BRANCH_IMAGE)
    results = _run_exact(state, 9, policy=ExecutionPolicy.HARDWARE_LIKE)

    assert [result.instruction for result in results] == [
        DecodedInstruction(Opcode.LDI, 0x000),
        DecodedInstruction(Opcode.JZ, 0x009),
        DecodedInstruction(Opcode.LDI, 0x0FF),
        DecodedInstruction(Opcode.JN, 0x015),
        DecodedInstruction(Opcode.LDI, 0x0FF),
        DecodedInstruction(Opcode.ADD, 0x100),
        DecodedInstruction(Opcode.JC, 0x021),
        DecodedInstruction(Opcode.LDI, 0x0A0),
        DecodedInstruction(Opcode.HLT, 0x000),
    ]
    assert results[1].post_state.pc == 0x009
    assert results[3].post_state.pc == 0x015
    assert results[6].post_state.pc == 0x021
    assert all(result.diagnostic is None for result in results)
    _assert_final(
        results[-1],
        a=0xA0,
        pc=0x025,
        irh=0xF0,
        irl=0x00,
        flags=FlagsSnapshot(FlagValues(False, True, True, False), FlagsDefinedMask.zero_and_sign()),
        mask=FlagsDefinedMask.zero_and_sign(),
        halt=True,
        diagnostic=None,
    )


STRICT_IMAGE = _build_image(
    (0x000, bytes([0x10, 0x42, 0x70, 0x08, 0x10, 0x99, 0xF0, 0x00])),
)


def test_strict_program_stops_at_undefined_conditional_diagnostic() -> None:
    state = _load(STRICT_IMAGE)
    results = _run_exact(state, 2, policy=ExecutionPolicy.STRICT)

    assert [result.instruction for result in results] == [
        DecodedInstruction(Opcode.LDI, 0x042),
        DecodedInstruction(Opcode.JC, 0x008),
    ]
    diagnostic = results[-1].diagnostic
    assert diagnostic is not None
    assert diagnostic.identifier is DiagnosticIdentifier.UNDEFINED_CONDITIONAL_FLAG
    assert diagnostic.severity is DiagnosticSeverity.ERROR
    assert results[-1].post_state.pc == 0x004
    assert results[-1].post_state.halt_state is False
    assert state.a == 0x42
    assert state.pc == 0x004


HARDWARE_LIKE_IMAGE = _build_image(
    (0x000, bytes([0x10, 0x42, 0x70, 0x08, 0x10, 0x99, 0xF0, 0x00])),
    (0x008, bytes([0x10, 0x7A, 0xF0, 0x00])),
)


@pytest.mark.parametrize("carry", [False, True])
def test_hardware_like_program_uses_concrete_undefined_c_and_continues(carry: bool) -> None:
    state = _load(HARDWARE_LIKE_IMAGE)
    state._flags = FlagsSnapshot(FlagValues(False, carry, False, False), FlagsDefinedMask.all())
    expected_path = (
        [Opcode.LDI, Opcode.JC, Opcode.LDI, Opcode.HLT]
        if not carry
        else [Opcode.LDI, Opcode.JC, Opcode.LDI, Opcode.HLT]
    )

    results = _run_exact(state, 4, policy=ExecutionPolicy.HARDWARE_LIKE)

    assert _instruction_opcodes(results) == expected_path
    assert results[1].diagnostic is not None
    assert results[1].diagnostic.identifier is DiagnosticIdentifier.UNDEFINED_CONDITIONAL_FLAG
    assert results[1].diagnostic.severity is DiagnosticSeverity.WARNING
    assert results[1].post_state.pc == (0x008 if carry else 0x004)
    assert results[-1].post_state.a == (0x7A if carry else 0x99)
    assert results[-1].post_state.pc == (0x00C if carry else 0x008)
    assert results[-1].post_state.halt_state is True
    assert results[-1].post_state.flags_defined_mask == FlagsDefinedMask.zero_and_sign()


LOOP_IMAGE = _build_image(
    (
        0x000,
        bytes(
            [
                0x10,
                0x03,
                0x51,
                0x00,
                0x21,
                0x00,
                0x41,
                0x01,
                0x51,
                0x00,
                0x80,
                0x10,
                0x60,
                0x04,
                0x00,
                0x00,
                0xF0,
                0x00,
            ]
        ),
    ),
    (0x100, bytes([0x00, 0x01])),
)


def test_finite_loop_program_reaches_zero_with_hard_bound() -> None:
    state = _load(LOOP_IMAGE)
    results = _run_until_halt(state, max_steps=20)

    assert len(results) == 17
    assert _instruction_opcodes(results) == [
        Opcode.LDI,
        Opcode.STA,
        Opcode.LDA,
        Opcode.SUB,
        Opcode.STA,
        Opcode.JZ,
        Opcode.JMP,
        Opcode.LDA,
        Opcode.SUB,
        Opcode.STA,
        Opcode.JZ,
        Opcode.JMP,
        Opcode.LDA,
        Opcode.SUB,
        Opcode.STA,
        Opcode.JZ,
        Opcode.HLT,
    ]
    assert results[5].post_state.pc == 0x00C
    assert results[10].post_state.pc == 0x00C
    assert results[15].post_state.pc == 0x010
    assert results[-1].post_state.a == 0x00
    assert results[-1].post_state.flags == FlagsSnapshot(
        FlagValues(True, True, False, False), FlagsDefinedMask.all()
    )
    _assert_final(
        results[-1],
        a=0x00,
        pc=0x012,
        irh=0xF0,
        irl=0x00,
        flags=FlagsSnapshot(FlagValues(True, True, False, False), FlagsDefinedMask.all()),
        mask=FlagsDefinedMask.all(),
        halt=True,
        diagnostic=None,
    )
    assert state._memory.read(0x100) == 0x00


SELF_MODIFYING_IMAGE = _build_image(
    (0x000, bytes([0x10, 0xF0, 0x50, 0x10, 0x60, 0x10])),
    (0x010, bytes([0x00, 0x00])),
)


def test_self_modifying_program_fetches_modified_future_instruction() -> None:
    state = _load(SELF_MODIFYING_IMAGE)
    results = _run_exact(state, 4, include_memory=True)

    assert [result.instruction for result in results] == [
        DecodedInstruction(Opcode.LDI, 0x0F0),
        DecodedInstruction(Opcode.STA, 0x010),
        DecodedInstruction(Opcode.JMP, 0x010),
        DecodedInstruction(Opcode.HLT, 0x000),
    ]
    assert results[1].post_state.memory is not None
    assert results[1].post_state.memory[0x010] == 0xF0
    assert results[3].post_state.pc == 0x012
    assert results[3].post_state.halt_state is True
    assert results[3].post_state.memory is not None
    assert results[3].post_state.memory[0x011] == 0x00


BOUNDARY_IMAGE = _build_image(
    (0xFFF, bytes([0x10])),
    (0x000, bytes([0x42, 0xF0, 0x00])),
)


def test_boundary_program_fetches_instruction_across_0xfff_to_zero() -> None:
    state = _load(BOUNDARY_IMAGE, pc=0xFFF)
    results = _run_exact(state, 2)

    assert results[0].instruction == DecodedInstruction(Opcode.LDI, 0x042)
    assert results[0].pre_state.pc == 0xFFF
    assert results[0].post_state.pc == 0x001
    assert results[0].post_state.irh == 0x10
    assert results[0].post_state.irl == 0x42
    assert results[1].instruction == DecodedInstruction(Opcode.HLT, 0x000)
    assert results[1].post_state.pc == 0x003
    assert results[1].post_state.halt_state is True


RESERVED_IMAGE = _build_image(
    (0x000, bytes([0x10, 0x42, 0xB1, 0x23, 0x10, 0x99])),
)


def test_reserved_program_halts_and_reset_resumes_from_image_start() -> None:
    state = _load(RESERVED_IMAGE)
    results = _run_exact(state, 2)
    halted = state.step()
    old_reserved_result = results[-1]
    state.reset()
    resumed = state.step()

    assert results[0].instruction == DecodedInstruction(Opcode.LDI, 0x042)
    assert results[1].instruction == DecodedInstruction(Opcode.RESERVED_B, 0x123)
    assert results[1].diagnostic is not None
    assert results[1].diagnostic.identifier is DiagnosticIdentifier.ILLEGAL_OPCODE
    assert results[1].diagnostic.opcode is Opcode.RESERVED_B
    assert results[1].post_state.halt_state is True
    assert halted.instruction is None
    assert halted.diagnostic is None
    assert halted.pre_state == halted.post_state
    assert resumed.instruction == DecodedInstruction(Opcode.LDI, 0x042)
    assert resumed.post_state.a == 0x42
    assert resumed.post_state.halt_state is False
    assert old_reserved_result.post_state.halt_state is True
    assert state.memory_image == RESERVED_IMAGE


def test_representative_programs_are_deterministic_on_independent_states() -> None:
    first = _load(ARITHMETIC_IMAGE)
    second = _load(ARITHMETIC_IMAGE)

    first_results = _run_exact(first, 5, include_memory=True)
    second_results = _run_exact(second, 5, include_memory=True)

    assert first_results == second_results
    assert first.snapshot(include_memory=True) == second.snapshot(include_memory=True)


def test_program_images_are_exact_4096_byte_images() -> None:
    for image in (
        ARITHMETIC_IMAGE,
        DEFINED_BRANCH_IMAGE,
        STRICT_IMAGE,
        HARDWARE_LIKE_IMAGE,
        LOOP_IMAGE,
        SELF_MODIFYING_IMAGE,
        BOUNDARY_IMAGE,
        RESERVED_IMAGE,
    ):
        assert type(image) is bytes
        assert len(image) == IMAGE_SIZE
