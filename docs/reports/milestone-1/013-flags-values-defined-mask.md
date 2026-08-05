# Task M1-013: FLAGS values and defined mask

## Summary

Добавлены самостоятельные immutable value models для concrete FLAGS, software-only defined mask и объединённого snapshot состояния.

## Sources

Решение основано на `AGENTS.md`, `README.md`, `docs/plans/milestone-1-component-models.md`, `docs/reports/milestone-1/README.md`, reports Tasks 8–10 и 12, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/adr/README.md` и всеми активными ADR, особенно ADR-0005 и ADR-0010. Реализация сверена с `cpu/alu.py`, `cpu/alu_add.py`, `cpu/alu_sub.py`, `cpu/values.py`, `cpu/__init__.py`, существующими immutable dataclass и enum conventions, tests, `docs/testing/software.md`, `pyproject.toml` и `scripts/verify`.

## Design decision

Добавлен enum `Flag` ровно с четырьмя symbolic members: `ZERO = "z"`, `CARRY = "c"`, `SIGN = "s"`, `OVERFLOW = "o"`. Numeric bit positions, control-word codes и branch mapping отсутствуют.

Concrete values представлены immutable `FlagValues` с четырьмя bool fields: `zero`, `carry`, `sign`, `overflow`. Runtime validation принимает только actual `bool`; integers `0` и `1`, strings и `None` отклоняются через `TypeError`.

Defined mask представлен immutable `FlagsDefinedMask`, являющимся небольшим wrapper над `frozenset[Flag]`. Он предоставляет canonical factories `all()`, `zero_and_sign()`, `none()`, lookup `is_defined()`, immutable `defined_flags` и read-only predicates `all_defined`/`none_defined`. Raw strings и integers в mask не интерпретируются как flags.

Добавлен immutable `FlagsSnapshot`, объединяющий `FlagValues` и `FlagsDefinedMask`. Это соответствует software state из ADR-0010 и позволяет передавать values и defined status вместе без mutable FLAGS register.

## Concrete values

`FlagValues` всегда содержит concrete binary values для Z, C, S и O. Unknown/tri-state значения не вводятся.

Canonical reset values:

```text
Z = 0
C = 0
S = 0
O = 0
```

`FlagValues.reset()` возвращает новый immutable object.

## Defined mask

Canonical states:

```text
FlagsDefinedMask.all()          -> Z/C/S/O defined
FlagsDefinedMask.zero_and_sign() -> Z/S defined, C/O undefined
FlagsDefinedMask.none()         -> no flags defined
```

Контекст применения mask соответствует архитектуре, но переходы не реализуются в Task 13:

```text
RESET   -> Z/C/S/O defined
ADD/SUB -> Z/C/S/O defined
LDI/LDA-like A writes -> only Z/S defined
```

## Reset snapshot

```python
snapshot = FlagsSnapshot.reset()

snapshot.values == FlagValues(False, False, False, False)
snapshot.defined == FlagsDefinedMask.all()
```

## Changes

- Добавлены `Flag`, `FlagValues`, `FlagsDefinedMask` и `FlagsSnapshot` в `cpu/flags.py`.
- Добавлены public exports через `cpu/__init__.py`.
- Добавлены unit tests concrete values, mask states, lookup, validation, immutability и reset snapshot.
- Обновлён milestone index; hash commit оставлен `—`.

## Public API

```python
from cpu import Flag, FlagsDefinedMask, FlagsSnapshot

reset = FlagsSnapshot.reset()
assert reset.values.zero is False
assert reset.defined.is_defined(Flag.ZERO)

zs_only = FlagsDefinedMask.zero_and_sign()
assert zs_only.is_defined(Flag.ZERO)
assert zs_only.is_defined(Flag.SIGN)
assert not zs_only.is_defined(Flag.CARRY)
```

## Tests

Добавлено 49 test cases. Проверены enum, symbolic members, concrete combinations, строгая bool validation, reset values, all-defined/Z-S-only/none-defined masks, invalid flag lookup, invalid mask members, копирование mutable input collection, immutable exposed set, snapshot reset, snapshot equality и snapshot validation.

Transitions from A/ALU, latch policy, preserve behavior и instruction-specific operations не тестируются, поскольку относятся к Tasks 14–15 или simulator layer.

## Verification

Targeted tests, форматирование, lint и mypy проходят. Полная проверка `./scripts/verify` выполняется перед commit и включает предыдущие component tests и новые FLAGS tests.

Hardware verification не выполнялась; hardware status — `NOT_TESTED`.

## Architectural compliance

Architecture, ISA, microarchitecture, control word, memory model и активные ADR не изменены. Mutable FLAGS register, `load()`/`latch()`, calculation from A/ALU, instruction-specific transitions, branch diagnostics, control-word behavior, clock semantics, emulator, simulator и hardware work отсутствуют.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
model: add flags values and defined mask
```

Hash текущего commit будет указан в Git metadata; push и tag не выполняются.

## Follow-up

Следующая задача — Task 14: FLAGS latch policy для записи A. Она определит переходы values и defined mask при событиях записи A.
