# Отчёты Milestone 1: Component Models

## Назначение

Каталог хранит отчёты о завершённых инженерных задачах Milestone 1. Этот индекс не является ADR и не является architecture specification.

## Правила

Для каждой задачи необходимо:

1. изучить source-of-truth documentation;
2. выполнить только scope одной задачи;
3. реализовать изменения;
4. добавить или обновить tests;
5. обновить документацию только в пределах задачи;
6. выполнить `./scripts/verify`;
7. выполнить `git diff --check`;
8. создать task report;
9. предложить atomic commit;
10. после review перейти к следующей задаче.

Принцип: `one engineering task -> one atomic commit`.

Допустимо несколько commits только если задача объективно требует нескольких независимо проверяемых атомарных изменений. Такое решение и его причина должны быть явно обоснованы в task report. Push и milestone tag не выполняются без отдельного разрешения. Аппаратная проверка Milestone 1 отсутствует, поэтому hardware status остаётся `NOT_TESTED`.

## Статусы

`COMPLETED` означает, что задача выполнена и проверена в пределах своего scope. `PLANNED` означает, что задача запланирована, но ещё не выполнена.

| ID | Phase | Task | Status | Report | Commit | Notes |
|---|---|---|---|---|---|---|
| M1-001 | A | Зафиксировать specification Milestone 1 | COMPLETED | — | `3dd173d` | Documentation-only; отдельный report не создаётся заранее |
| M1-002 | A | Добавить width/value primitives | COMPLETED | `002-width-value-primitives.md` | — | Hash текущего commit будет добавлен следующим documentation update |
| M1-003 | B | Реализовать базовый fixed-width register | COMPLETED | `003-fixed-width-register.md` | — | Hash текущего commit будет добавлен следующим documentation update |
| M1-004 | B | Реализовать A и B register boundaries | COMPLETED | `004-a-b-register-boundaries.md` | — | Решён вариант B: generic `FixedWidthRegister` instances |
| M1-005 | B | Реализовать MAR | COMPLETED | `005-mar.md` | — | Named 12-bit storage boundary |
| M1-006 | B | Реализовать Program Counter | COMPLETED | `006-program-counter.md` | — | Modulo increment only; hold is implicit |
| M1-007 | B | Реализовать Instruction Register | COMPLETED | `007-instruction-register.md` | — | Independent IRH/IRL storage and derived views |
| M1-008 | C | Реализовать ALU ADD | COMPLETED | `008-alu-add.md` | — | Stateless ADD with exhaustive flags coverage |
| M1-009 | C | Реализовать ALU SUB | COMPLETED | `009-alu-sub.md` | — | Stateless SUB with no-borrow carry and exhaustive flags coverage |
| M1-010 | C | Объединить ADD/SUB в публичную ALU model | COMPLETED | `010-unified-alu.md` | — | Stateless unified API with explicit ADD/SUB modes |
| M1-011 | C | Реализовать DATA BUS resolver | COMPLETED | `011-data-bus-resolver.md` | — | Stateless resolver with HIGH_Z and contention detection |
| M1-012 | C | Реализовать address source selector | COMPLETED | `012-address-source-selector.md` | — | Stateless PC/IR operand selector with strict 12-bit validation |
| M1-013 | D | Реализовать Flags value и defined mask | COMPLETED | `013-flags-values-defined-mask.md` | — | Immutable concrete values, mask and reset snapshot |
| M1-014 | D | Реализовать FLAGS latch policy для записи A | COMPLETED | `014-flags-latch-policy.md` | — | Stateless full/partial-defined write policy with preserve/reset |
| M1-015 | D | Добавить exhaustive/parameterized flags tests | COMPLETED | `015-flags-exhaustive-tests.md` | — | 65536 ADD, 65536 SUB and 1024 non-ALU policy cases |
| M1-016 | E | Реализовать SRAM storage model | COMPLETED | `016-sram-storage.md` | — | Fixed 4096-byte zero-filled storage with strict read/write validation |
| M1-017 | E | Реализовать full-image replacement | COMPLETED | `017-full-image-replacement.md` | — | Atomic replacement of exact 4096-byte bytes-like image |
| M1-018 | E | Реализовать MICROSTEP counter | COMPLETED | `018-microstep-counter.md` | — | Fixed 4-bit T0..T15 counter with modulo wrap and explicit return T0 |
| M1-019 | E | Реализовать HALT latch | PLANNED | `019-halt-latch.md` | — | — |
| M1-020 | F | Создать component-state container | PLANNED | `020-component-state-container.md` | — | Условная задача |
| M1-021 | F | Добавить component-level integration tests | PLANNED | `021-component-integration-tests.md` | — | — |
| M1-022 | F | Documentation and milestone regression | PLANNED | `022-milestone-regression.md` | — | — |

Task 1 report не создаётся заранее: текущая работа фиксирует саму specification и этот index; фактические проверки Task 1 указываются в итоговом инженерном отчёте или commit metadata.

## Имена отчётов

Для задач используется numbering `001..022` и связь один-к-одному с ID задачи:

```text
001-specification.md
002-width-value-primitives.md
003-fixed-width-register.md
...
022-milestone-regression.md
```

Пустые report files заранее не создаются. Для Task 1 строка `Report` намеренно содержит `—`, поскольку отдельный пустой report не добавляется.

## Минимальный шаблон отчёта

Каждый будущий report должен содержать:

```markdown
# Task M1-XXX: <title>

## Summary

## Scope

## Changes

## Tests

## Verification

## Architectural compliance

## Result

## Commit

## Follow-up
```

В report нельзя представлять software verification как hardware `PASS`; hardware status для Milestone 1 — `NOT_TESTED`.
