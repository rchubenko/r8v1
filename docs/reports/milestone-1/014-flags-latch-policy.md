# Task M1-014: FLAGS latch policy

## Summary

Добавлена stateless policy перехода immutable FLAGS snapshot при записи значения в A. Policy поддерживает полностью определённую ALU-derived запись, частично определённую non-ALU запись, preserve и canonical reset.

## Sources

Решение основано на `AGENTS.md`, `README.md`, `docs/plans/milestone-1-component-models.md`, `docs/reports/milestone-1/README.md`, reports Tasks 8–10 и 13, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/adr/README.md` и всеми активными ADR, особенно ADR-0005 и ADR-0010. Реализация сверена с `cpu/flags.py`, `cpu/alu.py`, `cpu/alu_add.py`, `cpu/alu_sub.py`, `cpu/values.py`, `cpu/__init__.py`, существующими immutable value и stateless function conventions, tests, `docs/testing/software.md`, `pyproject.toml` и `scripts/verify`.

## Design decision

Выбраны две отдельные stateless functions вместо mode enum и набора optional arguments:

```python
latch_flags_for_alu_write(alu_result) -> FlagsSnapshot
latch_flags_for_non_alu_write(
    a_value, *, alu_carry, alu_overflow
) -> FlagsSnapshot
```

Такой API не содержит instruction mnemonics и делает invalid combinations труднее выразимыми: ALU-derived path принимает только unified `ALUResult`, а non-ALU path явно требует incoming byte и concrete C/O outputs.

`latch_flags_for_alu_write()` принимает только actual `ALUResult`, использует его `result` как incoming A byte, берёт C/O из ALU result и создаёт all-defined mask. Z/S вычисляются из result byte, поэтому они не зависят от потенциально противоречащих derived fields объекта.

`latch_flags_for_non_alu_write()` валидирует incoming A byte, принимает concrete C/O и создаёт Z/S-only mask. C/O остаются concrete values, но помечаются undefined metadata.

`preserve_flags(snapshot)` — явная identity policy: для immutable snapshot возвращается тот же object. Reset не дублирует construction logic и использует существующий `FlagsSnapshot.reset()`.

## Full-defined A write

```text
Z/S from ALU result byte
C/O from ALU outputs
defined = Z/C/S/O
```

`latch_flags_for_alu_write()` не выполняет арифметику и не изменяет входной `ALUResult`.

## Partial-defined A write

```text
Z/S from incoming A byte
C/O from concrete ALU outputs
defined = Z/S
```

Undefined C/O не означают отсутствие concrete values: они сохраняются в `FlagValues` как actual bool и различаются через `FlagsDefinedMask`.

## Preserve and reset

Preserve сохраняет values и mask без пересчёта и возвращает исходный immutable snapshot.

Reset использует canonical Task 13 snapshot:

```text
values = 0000
defined = Z/C/S/O
```

## Changes

- Добавлены `latch_flags_for_alu_write`, `latch_flags_for_non_alu_write` и `preserve_flags` в `cpu/flags_policy.py`.
- Добавлены public exports через `cpu/__init__.py`.
- Добавлены focused unit tests full-defined/partial-defined paths, validation, preserve, reset и statelessness.
- Обновлён milestone index; hash commit оставлен `—`.

## Public API

```python
from cpu import (
    ALUResult,
    latch_flags_for_alu_write,
    latch_flags_for_non_alu_write,
)

full = latch_flags_for_alu_write(
    ALUResult(result=0x80, zero=False, carry=False, sign=True, overflow=True)
)

partial = latch_flags_for_non_alu_write(
    0x80,
    alu_carry=True,
    alu_overflow=False,
)
```

## Tests

Добавлено 55 test cases. Проверены full-defined ALU matrix, deriving Z/S from result byte, concrete C/O, partial-defined byte boundaries, все четыре C/O combinations, preserve identity, reset, invalid A values, invalid C/O types, invalid ALU result types, validation order и stateless behavior.

Instruction-specific transitions, mutable FLAGS register, A mutation и branch diagnostics не тестируются, поскольку находятся вне Task 14.

## Verification

Targeted tests, форматирование, lint и mypy проходят. Полная проверка `./scripts/verify` выполняется перед commit и включает предыдущие component/ALU/FLAGS tests и новые policy tests.

Hardware verification не выполнялась; hardware status — `NOT_TESTED`.

## Architectural compliance

Architecture, ISA, microarchitecture, control word, memory model и активные ADR не изменены. Public API не содержит instruction mnemonics. Mutable FLAGS register, A mutation, `E_A`/`FLAGS_LOAD_INTERNAL` decoding, control-word parsing, clock/rising edge, branch diagnostics, emulator, simulator и hardware work отсутствуют.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
model: add flags latch policy
```

Hash текущего commit будет указан в Git metadata; push и tag не выполняются.

## Follow-up

Следующая задача — Task 15: exhaustive/parameterized FLAGS tests. Она расширит coverage transitions и parity без изменения policy boundary.
