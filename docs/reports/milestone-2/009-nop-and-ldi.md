# Task M2-009: Implement NOP and LDI

## Summary

Добавлена минимальная atomic execution boundary для NOP и LDI после уже выполненного fetch. NOP сохраняет post-fetch architectural state, а LDI загружает low byte operand в A и обновляет FLAGS по approved non-ALU write policy.

## Sources

Работа сверена с [`AGENTS.md`](../../../AGENTS.md), [README проекта](../../../README.md), [архитектурой](../../architecture.md), [ISA](../../isa.md), [микроархитектурой](../../microarchitecture.md), [Control Word](../../control-word.md), [memory](../../memory.md), [software testing policy](../../testing/software.md), [планом Milestone 2](../../plans/milestone-2-isa-reference-emulator.md), [execution contract M2-002](002-emulator-execution-contract.md), reports M2-003 through M2-008, [ADR-0005](../../adr/0005-flags-update-on-a-write.md), [ADR-0010](../../adr/0010-deterministic-software-model-semantics.md), `ArchitecturalState`, fetch/snapshot APIs, FLAGS и register APIs, а также test conventions.

## Scope

В scope входят только NOP и LDI execution после supplied `DecodedInstruction`. Полный dispatcher, остальные instructions, instruction execution loop, branches, HALT execution и conditional diagnostics не реализованы.

## Design decision

Canonical API:

```python
ArchitecturalState.execute_instruction(instruction: DecodedInstruction) -> None
```

Поддерживаются только `Opcode.NOP` и `Opcode.LDI`. Unsupported opcode отклоняется `ValueError` до mutation. Неправильный input отклоняется `TypeError`.

NOP не изменяет state после fetch. LDI использует `operand & 0xFF`, поэтому operands выше `0x0FF` не отвергаются execution layer.

## FLAGS behavior

LDI переиспользует `latch_flags_for_non_alu_write()`:

- Z вычисляется из нового A;
- S берётся из bit 7 нового A;
- concrete C/O сохраняются;
- `flags_defined_mask` становится `Z | S`.

Execution policy `STRICT`/`HARDWARE_LIKE` не используется.

## State preservation

После fetch NOP сохраняет A, FLAGS/mask, SRAM и HALT. LDI дополнительно изменяет только A и FLAGS/mask; PC остаётся post-fetch, IR сохраняется, SRAM и HALT не изменяются.

## Changes

- `emulator/state.py` — minimal NOP/LDI execution API.
- `tests/test_emulator_execution.py` — ISA execution and FLAGS tests.
- `docs/reports/milestone-2/009-nop-and-ldi.md` — этот report.
- `docs/reports/milestone-2/README.md` — статус и report link для M2-009.

Source-of-truth documents, ISA, active ADR и milestone plan не изменялись.

## Tests

Проверены:

- NOP initial и modified state;
- LDI operands `0x000`, `0x001`, `0x07F`, `0x080`, `0x0FF`, `0x100`, `0xABC`, `0xFFF`;
- Z/S cases `0x00`, `0x01`, `0x7F`, `0x80`, `0xFF`;
- все combinations concrete C/O;
- repeated LDI;
- сохранение PC, IR, SRAM и HALT;
- LDI через boundary `0xFFF -> 0x000`;
- unsupported opcode и invalid input без mutation.

## Verification

- Targeted execution tests: `24 passed`; combined emulator tests: `71 passed`.
- `./scripts/verify` — PASS.
- `git diff --check` — PASS.
- formatting, lint и mypy — PASS.
- documentation checks — PASS.
- Full regression: `713 passed`.
- Generated artifacts отсутствуют.

## Architectural compliance

Implementation находится в `emulator/`, `cpu/` не изменялся. Full dispatcher, execution loop, assembler validation, simulator, microcode, control-word decode, hardware и future instruction semantics отсутствуют.

Hardware status: `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
9506ae8 emulator: implement NOP and LDI
```

## Follow-up

Следующая задача — M2-010: продолжить atomic ISA execution согласно canonical milestone sequence. Push не выполняется в рамках этой задачи.
