# Task M1-003: Fixed-width register

## Summary

Добавлена минимальная переиспользуемая модель регистра фиксированной ширины с initial/reset value, чтением, явной загрузкой и строгой проверкой диапазона.

## Scope

Реализован только базовый `FixedWidthRegister`. Поддерживаются утверждённые widths 4, 8 и 12 bit. Семантика A, B, MAR, PC, IR, clock, increment и instruction execution не входит в scope.

## Changes

- Добавлен `cpu.register.FixedWidthRegister`.
- Register повторно использует `validate_nibble`, `validate_byte` и `validate_address`.
- Добавлены read-only properties `width`, `reset_value` и `value`.
- Добавлены `load(value)` и `reset()`.
- В `cpu/__init__.py` добавлен минимальный public export `FixedWidthRegister`.
- Обновлён milestone index; hash текущего commit оставлен `—` до следующего documentation update.

## Tests

Добавлены unit tests для:

- минимальных и максимальных reset values для всех widths;
- valid load values и сохранения значения без изменения;
- reset после load, non-zero reset value и повторного reset;
- invalid reset values и unsupported widths;
- invalid load с сохранением предыдущего state;
- project-specific exception и error context;
- изоляции двух register instances;
- read-only current и reset values.

## Verification

Выполнены `./scripts/verify` и `git diff --check`. Полный набор tests включает предыдущие tests Task 2 и новые tests fixed-width register.

## Architectural compliance

Architecture semantics не изменены. Выбран подход A: register принимает только widths 4, 8 и 12, поскольку именно эти widths утверждены для текущих primitives. Это не universal bit-vector framework: отсутствуют arithmetic, slicing, concatenation, signed interpretation и bit operations. Validation использует существующие Task 2 helpers, не добавляет masking или modulo. Concrete register semantics, clock behavior, instruction execution, emulator, simulator и hardware work отсутствуют. Hardware status — `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
model: add fixed-width register
```

Hash текущего commit намеренно не записывается до следующего documentation update.

## Follow-up

Следующая задача — Task 4: A и B register boundaries. Она не входит в текущий commit.
