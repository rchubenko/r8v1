# Task M2-004: Architectural emulator state

## Summary

Создан emulator-owned `ArchitecturalState` для persistent architectural data ISA Reference Emulator. State детерминированно создаёт A, PC, IR, FLAGS, `flags_defined_mask`, SRAM и HALT state. Execution, fetch, reset transition и policy runtime не реализованы.

## Sources

Работа сверена с [`AGENTS.md`](../../../AGENTS.md), [README проекта](../../../README.md), [архитектурой](../../architecture.md), [ISA](../../isa.md), [микроархитектурой](../../microarchitecture.md), [Control Word](../../control-word.md), [memory](../../memory.md), [software testing policy](../../testing/software.md), [планом Milestone 2](../../plans/milestone-2-isa-reference-emulator.md), [execution contract M2-002](002-emulator-execution-contract.md), [report M2-003](003-opcode-and-decoded-instruction-values.md), [индексом ADR](../../adr/README.md), активными ADR и существующими component/package/test conventions.

## Scope

В scope входили только emulator-owned state construction, read-only observation и ownership checks. State содержит A, PC, IR, concrete FLAGS snapshot, defined mask, unified SRAM и HALT latch. Execution policy и diagnostics в state не включаются.

## Design decision

Canonical construction API:

```python
ArchitecturalState() -> ArchitecturalState
```

State предоставляет read-only properties `a`, `pc`, `irh`, `irl`, `opcode`, `operand`, `flags`, `flags_defined_mask`, `halt_state` и `memory_image`. `memory_image` возвращает detached `bytes` image размера 4096, а не mutable SRAM storage.

Reset method, mutation methods, fetch orchestration и final architectural snapshot не добавлялись.

## Reused Milestone 1 components

- `FixedWidthRegister(width=8, reset_value=0x00)` для A;
- `ProgramCounter` для 12-bit PC с reset `0x000`;
- `InstructionRegister` для IRH/IRL и derived opcode/operand views;
- `FlagsSnapshot.reset()` для concrete FLAGS `0000` и fully defined mask;
- `SRAM` для zero-filled 4096-byte storage;
- `HaltLatch` для initial cleared HALT state.

Component APIs достаточны. `cpu/` не расширялся.

## Ownership and exclusions

State владеет отдельными component instances. Внешнему коду не выдаются mutable component holders или SRAM storage. A, PC, IR, FLAGS, mask, SRAM и HALT являются частью state boundary.

Публичные поля B, MAR, MICROSTEP, DATA BUS, control word, execution policy и diagnostics отсутствуют. B не создаётся, поскольку instruction execution и ALU integration не входят в текущую задачу.

## Changes

- `emulator/state.py` — `ArchitecturalState` и safe observations.
- `emulator/__init__.py` — public export `ArchitecturalState`.
- `tests/test_emulator_state.py` — construction, ownership и observation tests.
- `docs/reports/milestone-2/004-architectural-emulator-state.md` — этот report.
- `docs/reports/milestone-2/README.md` — статус и report link для M2-004.

Source-of-truth documents, ISA, active ADR и milestone plan не изменялись.

## Tests

Проверены:

- initial A, PC, IRH, IRL, opcode, operand, FLAGS, mask, HALT и SRAM;
- два независимых state instances и отсутствие shared component holders;
- независимость SRAM contents между instances;
- detached immutable `bytes` observation SRAM;
- отсутствие side effects от observations;
- immutability FLAGS и defined mask;
- отсутствие public B, MAR, MICROSTEP, DATA BUS, control word, execution policy и diagnostics.

Fetch, reset, image loading, instruction execution и execution-policy tests не добавлялись.

## Verification

- Targeted state tests: `11 passed`; combined emulator decode/state tests: `64 passed`.
- `./scripts/verify` — PASS.
- `git diff --check` — PASS.
- formatting, lint и mypy — PASS.
- documentation checks — PASS.
- Full regression: `653 passed`.
- Generated artifacts отсутствуют.

## Architectural compliance

Implementation находится в `emulator/`, переиспользует approved `cpu/` components и не добавляет emulator coordinator в `cpu/`. Нет зависимостей от simulator, microcode, assembler, loader или hardware. State не содержит execution policy, diagnostics или simulator concepts.

Hardware status: `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
2edc01e emulator: add architectural machine state
```

## Follow-up

Следующая задача — M2-005: реализовать architectural reset. Push не выполняется в рамках этой задачи.
