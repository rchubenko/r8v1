# Task M2-007: Atomic instruction fetch

## Summary

Реализован atomic fetch одной 16-bit instruction из state-owned SRAM. Fetch читает два bytes по текущему PC и следующему modulo-4096 адресу, дважды increments PC, обновляет IR и возвращает `DecodedInstruction` через существующий decode API.

## Sources

Работа сверена с [`AGENTS.md`](../../../AGENTS.md), [README проекта](../../../README.md), [архитектурой](../../architecture.md), [ISA](../../isa.md), [микроархитектурой](../../microarchitecture.md), [memory contract](../../memory.md), [software testing policy](../../testing/software.md), [планом Milestone 2](../../plans/milestone-2-isa-reference-emulator.md), [execution contract M2-002](002-emulator-execution-contract.md), reports M2-003 through M2-006, [ADR-0001](../../adr/0001-unified-memory.md), [ADR-0010](../../adr/0010-deterministic-software-model-semantics.md), APIs `ProgramCounter`, `InstructionRegister`, `SRAM`, `decode_instruction()` и test conventions.

## Scope

В scope входили только atomic instruction fetch, PC modulo increments, IR update, decoded return value, boundary fetch и observation актуальных SRAM bytes. Instruction execution и microarchitecture sequencing не реализованы.

## Design decision

Canonical API:

```python
ArchitecturalState.fetch_instruction() -> DecodedInstruction
```

Логическая последовательность:

```text
read SRAM[PC]
-> PC.increment()
-> read SRAM[PC]
-> PC.increment()
-> IRH/IRL load
-> decode current IR
-> return DecodedInstruction
```

PC increments выполняются существующим `ProgramCounter.increment()`. IR fields извлекаются существующим `InstructionRegister`, а decode выполняется через существующий `decode_instruction()`.

## State preservation and boundaries

Fetch изменяет только PC и IR. A, FLAGS, `flags_defined_mask`, HALT и SRAM сохраняются. Reserved opcode успешно декодируются без illegal-opcode halt, HLT только возвращается как value и не устанавливает HALT.

Fetch не содержит T0–T3, MAR, DATA BUS, clock, control word, microsteps, execution policy, diagnostics или instruction execution.

## Changes

- `emulator/state.py` — `ArchitecturalState.fetch_instruction()`.
- `tests/test_emulator_fetch.py` — normal, boundary, current SRAM и preservation tests.
- `docs/reports/milestone-2/007-atomic-instruction-fetch.md` — этот report.
- `docs/reports/milestone-2/README.md` — статус и report link для M2-007.

Source-of-truth documents, ISA, active ADR и milestone plan не изменялись.

## Tests

Проверены:

- normal fetch с PC `0x000`;
- fetch с non-zero PC `0x123`;
- boundaries `0xFFE -> 0x000` и `0xFFF -> 0x001`;
- reserved opcode `0xB..0xE`;
- HLT fetch без HALT effect;
- актуальные SRAM bytes без cached decoded result;
- preservation A, FLAGS/mask, HALT и SRAM;
- независимость state instances.

## Verification

- Targeted fetch tests: `9 passed`; combined fetch/image/reset/state tests: `37 passed`.
- `./scripts/verify` — PASS.
- `git diff --check` — PASS.
- formatting, lint и mypy — PASS.
- documentation checks — PASS.
- Full regression: `679 passed`.
- Generated artifacts отсутствуют.

## Architectural compliance

Implementation находится в `emulator/`, переиспользует `ProgramCounter`, `InstructionRegister`, `SRAM` и `decode_instruction()`. `cpu/` не изменялся. Нет зависимостей от simulator, microcode, assembler, loader или hardware.

Hardware status: `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
8503845 emulator: implement atomic instruction fetch
```

## Follow-up

Следующая задача — M2-008: добавить immutable architectural snapshots. Push не выполняется в рамках этой задачи.
