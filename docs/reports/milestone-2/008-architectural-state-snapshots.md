# Task M2-008: Architectural state snapshots

## Summary

Добавлен immutable `ArchitecturalStateSnapshot` для conformance observations и будущей parity preparation. Snapshot содержит только architectural state и поддерживает lightweight режим без SRAM copy и explicit full-memory capture.

## Sources

Работа сверена с [`AGENTS.md`](../../../AGENTS.md), [README проекта](../../../README.md), [архитектурой](../../architecture.md), [ISA](../../isa.md), [memory](../../memory.md), [software testing policy](../../testing/software.md), [планом Milestone 2](../../plans/milestone-2-isa-reference-emulator.md), [execution contract M2-002](002-emulator-execution-contract.md), reports M2-004 through M2-007, [ADR-0010](../../adr/0010-deterministic-software-model-semantics.md), `ArchitecturalState`, `FlagsSnapshot`, SRAM и immutable value/test conventions.

## Scope

В scope входили immutable architectural snapshot value, snapshot creation API, explicit memory observation strategy, equality semantics и integrations с image loading, fetch и reset. Simulator state, traces, execution result и diagnostics не добавлялись.

## Design decision

Canonical API:

```python
ArchitecturalState.snapshot(include_memory: bool = False) -> ArchitecturalStateSnapshot
```

`ArchitecturalStateSnapshot` является `@dataclass(frozen=True, slots=True)` с полями A, PC, IRH, IRL, `FlagsSnapshot`, `FlagsDefinedMask`, HALT и optional `memory`.

По умолчанию `memory is None`, поэтому lightweight conformance observations не копируют 4096 bytes. При `include_memory=True` state передаёт detached immutable `bytes` image размера 4096. Полное memory equality выполняется только между snapshots с captured memory; register-only snapshot и full-memory snapshot не считаются equal.

## Architectural boundary

Snapshot не содержит B, MAR, MICROSTEP, DATA BUS, control word, execution policy, diagnostics, clock, memory owner, EEPROM, simulator state или traces. Snapshot creation не изменяет state, не выполняет reset, fetch или instruction.

## Changes

- `emulator/snapshot.py` — `ArchitecturalStateSnapshot` и field validation.
- `emulator/state.py` — `snapshot(include_memory=False)`.
- `emulator/__init__.py` — public export snapshot type.
- `tests/test_emulator_snapshot.py` — immutability, equality, memory и integration tests.
- `docs/reports/milestone-2/008-architectural-state-snapshots.md` — этот report.
- `docs/reports/milestone-2/README.md` — статус и report link для M2-008.

Source-of-truth documents, ISA, active ADR и milestone plan не изменялись.

## Tests

Проверены:

- initial lightweight и full snapshot;
- deterministic repeated snapshots;
- top-level, FLAGS, mask и memory immutability;
- modified architectural state;
- independence после state mutations;
- equality register-only/full-memory snapshots и различающиеся memory images;
- отсутствие microarchitectural/public execution fields;
- image loading, fetch и reset integrations;
- detached full memory capture с boundary values.

## Memory observation strategy

Выбран explicit optional full capture. Lightweight snapshot не копирует SRAM и имеет `memory=None`; full snapshot содержит независимые `bytes`. Это минимальная стратегия без caching/versioning abstraction, сохраняющая deterministic full comparison там, где он нужен.

## Verification

- Targeted snapshot tests: `10 passed`; combined emulator tests: `47 passed`.
- `./scripts/verify` — PASS.
- `git diff --check` — PASS.
- formatting, lint и mypy — PASS.
- documentation checks — PASS.
- Full regression: `689 passed`.
- Generated artifacts отсутствуют.

## Architectural compliance

Implementation находится в `emulator/`, использует existing immutable component values и не добавляет snapshot coordinator в `cpu/`. Snapshot пригоден для conformance observations и future parity preparation без simulator coupling.

Hardware status: `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Expected atomic commit:

```text
emulator: add architectural state snapshots
```

## Follow-up

Следующая задача — M2-009: реализовать non-branch ISA instructions. Push не выполняется в рамках этой задачи.
