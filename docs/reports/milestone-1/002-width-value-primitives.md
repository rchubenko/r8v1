# Task M1-002: Width/value primitives

## Summary

Добавлены минимальные primitives для проверки 4-bit, 8-bit и 12-bit значений. Реализация не выполняет masking, wrapping или modulo normalization.

## Scope

В scope входили width constants, masks, validation helpers, единый project-specific exception, unit tests и документация Task 2. Hardware component models, instruction behavior, emulator и simulator не входили.

## Changes

- Добавлен пакет `cpu` в соответствии с repository boundary для component models.
- Добавлены `NIBBLE_BITS`, `BYTE_BITS`, `ADDRESS_BITS`.
- Добавлены `NIBBLE_MASK`, `BYTE_MASK`, `ADDRESS_MASK`.
- Добавлен `InvalidComponentValue`.
- Добавлены `validate_nibble`, `validate_byte`, `validate_address`.
- Значения типа `bool`, отрицательные значения, значения выше максимума и неподходящие типы отклоняются.
- Пакет `cpu` добавлен в wheel package configuration.
- Обновлён milestone report index; для Task 2 commit hash оставлен `—` до следующего documentation update, чтобы не создавать циклическую ссылку на текущий commit.

## Tests

Добавлены unit tests для:

- constants и masks;
- минимальных, внутренних и максимальных valid values;
- отрицательных и превышающих range values;
- неподходящих типов;
- `True` и `False`;
- возврата valid value без изменения;
- project-specific exception и содержательного error message.

## Verification

Выполнены `./scripts/verify` и `git diff --check`. Полный набор tests включает foundation, documentation, layout и width/value primitives.

## Architectural compliance

Architecture semantics не изменены. Widths взяты из утверждённых `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/memory.md` и активных ADR. Validation не добавляет modulo или masking semantics. Component models следующих задач ещё не реализованы. Hardware work отсутствует, hardware status — `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
model: add width/value primitives
```

Hash текущего commit намеренно не записывается в этот report до следующего documentation update.

## Follow-up

Следующая задача — Task 3: базовый fixed-width register. Она не входит в текущий commit.
