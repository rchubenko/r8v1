# Task M2-005: Architectural reset

## Summary

Реализован архитектурный reset `ArchitecturalState`. Он восстанавливает A, PC, IR, concrete FLAGS, `flags_defined_mask` и HALT state через approved component APIs, не изменяя содержимое SRAM. Electrical reset timing, clock behavior и microarchitecture reset не моделируются.

## Sources

Работа сверена с [`AGENTS.md`](../../../AGENTS.md), [README проекта](../../../README.md), [архитектурой](../../architecture.md), [ISA](../../isa.md), [микроархитектурой](../../microarchitecture.md), [Control Word](../../control-word.md), [memory](../../memory.md), [software testing policy](../../testing/software.md), [планом Milestone 2](../../plans/milestone-2-isa-reference-emulator.md), [execution contract M2-002](002-emulator-execution-contract.md), [report M2-003](003-opcode-and-decoded-instruction-values.md), [report M2-004](004-architectural-emulator-state.md), [ADR-0006](../../adr/0006-reset-architecture.md), [ADR-0010](../../adr/0010-deterministic-software-model-semantics.md), остальными активными ADR и component APIs `cpu/`.

## Scope

В scope входили только architectural reset transition для существующего emulator state, SRAM preservation, HALT independence, FLAGS/defined-mask reset и deterministic/idempotent tests. Image loading, fetch и instruction execution не реализованы.

## Design decision

Canonical API:

```python
ArchitecturalState.reset() -> None
```

Reset вызывает `reset()` у A register, `ProgramCounter`, `InstructionRegister` и `HaltLatch`, а FLAGS заменяет на `FlagsSnapshot.reset()`. SRAM component не затрагивается.

## Reset values

После reset:

- A = `0x00`;
- PC = `0x000`;
- IRH = `0x00`;
- IRL = `0x00`;
- opcode = `0x0`;
- operand = `0x000`;
- concrete FLAGS = `0000`;
- `flags_defined_mask` содержит все flags;
- `HALT_STATE = False`.

## SRAM preservation

Reset не вызывает SRAM reset или image replacement. Тесты сравнивают полный `memory_image` до и после reset, включая адреса `0x000`, `0x001`, representative middle address, `0xFFE` и `0xFFF`.

## Reused components and boundaries

Использованы существующие `FixedWidthRegister`, `ProgramCounter`, `InstructionRegister`, `FlagsSnapshot`, `SRAM` и `HaltLatch`. `cpu/` не изменялся.

Reset работает при установленном HALT и не зависит от execution policy. Electrical asynchronous assertion, synchronized release, clock priority, microstep reset, MAR, DATA BUS и control word остаются вне scope.

## Changes

- `emulator/state.py` — `ArchitecturalState.reset()`.
- `tests/test_emulator_reset.py` — reset, preservation, HALT, idempotence и independence tests.
- `docs/reports/milestone-2/005-architectural-reset.md` — этот report.
- `docs/reports/milestone-2/README.md` — статус и report link для M2-005.

Source-of-truth documents, ISA, active ADR и milestone plan не изменялись.

## Tests

Проверены:

- reset нового state;
- reset modified A, PC, IR, FLAGS, mask и HALT;
- сохранение полного 4096-byte SRAM image и boundary addresses;
- reset при установленном HALT;
- idempotence повторного reset;
- отсутствие влияния reset одного state instance на другой.

Image loading, fetch, snapshots, execution и electrical reset behavior tests не добавлялись.

## Verification

- Targeted reset/state tests: `17 passed`.
- `./scripts/verify` — PASS.
- `git diff --check` — PASS.
- formatting, lint и mypy — PASS.
- documentation checks — PASS.
- Full regression: `659 passed`.
- Generated artifacts отсутствуют.

## Architectural compliance

Reset реализован в `emulator/` как transition существующего emulator-owned state. Он использует component reset semantics, не очищает SRAM, не добавляет loader API и не содержит execution loop, fetch, snapshot или simulator concepts.

Hardware status: `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Expected atomic commit:

```text
emulator: implement architectural reset
```

## Follow-up

Следующая задача — M2-006: добавить exact executable image loading. Push не выполняется в рамках этой задачи.
