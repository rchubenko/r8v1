# Отчёты Milestone 2: ISA Reference Emulator

## Назначение

Каталог хранит task reports Milestone 2. Этот README определяет структуру отчётов и не является ISA, architecture, microarchitecture или control-word specification.

**Статус Milestone 2:** `PLANNED`

**Аппаратная проверка:** `NOT_TESTED`

## Границы отчётов

Отчёты должны описывать только ISA Reference Emulator и его deterministic software verification. Они не должны смешивать emulator с Microarchitecture Simulator, `control word`, microsteps, DATA BUS execution, clock orchestration или hardware.

Текущая documentation task создаёт только plan и этот index. Пустые task reports заранее не создаются.

## Нумерация и именование

Task reports используют последовательную нумерацию `001..014` и имя:

```text
NNN-short-kebab-case-name.md
```

Связь report с task определяется ID `M2-NNN`. Пример:

```text
M2-004 -> 004-emulator-state.md
```

Итоговый report milestone будет иметь отдельное имя:

```text
000-final-report.md
```

## Поля index

Index содержит таблицу с обязательными полями:

| Поле | Назначение |
|---|---|
| `Phase` | Фаза Milestone 2: A, B, C или D |
| `Task` | Краткое название инженерной задачи |
| `Status` | `PLANNED` или `COMPLETED` |
| `Report` | Ссылка на task report либо `—`, если report ещё не создан |
| `Commit` | Atomic commit hash либо `—` до commit |
| `Notes` | Краткие scope notes, diagnostics или blockers |

`BLOCKED` не используется для незавершённой плановой задачи: архитектурный blocker описывается в `Notes` и task report после фактического обнаружения.

## Task index

| ID | Phase | Task | Status | Report | Commit | Notes |
|---|---|---|---|---|---|---|
| M2-001 | A | Зафиксировать Milestone 2 plan и report index | COMPLETED | — | — | Documentation baseline этой задачи |
| M2-002 | A | Зафиксировать emulator state и atomic transition contract | COMPLETED | [`002-emulator-execution-contract.md`](002-emulator-execution-contract.md) | — | Atomic architectural contract; implementation не выполнялась |
| M2-003 | B | Добавить opcode и decoded instruction values | COMPLETED | [`003-opcode-and-decoded-instruction-values.md`](003-opcode-and-decoded-instruction-values.md) | — | Typed decode foundation; reserved opcode remain representable |
| M2-004 | B | Добавить architectural emulator state | COMPLETED | [`004-architectural-emulator-state.md`](004-architectural-emulator-state.md) | — | Architectural state construction and safe observation |
| M2-005 | B | Реализовать architectural reset | COMPLETED | [`005-architectural-reset.md`](005-architectural-reset.md) | — | Deterministic reset behavior; SRAM preserved |
| M2-006 | B | Добавить exact executable image loading | PLANNED | — | — | Validated 4096-byte image input |
| M2-007 | B | Реализовать atomic fetch и post-fetch PC behavior | PLANNED | — | — | Atomic ISA layer |
| M2-008 | B | Добавить immutable architectural snapshots | PLANNED | — | — | Safe architectural observation |
| M2-009 | C | Реализовать non-branch ISA instructions | PLANNED | — | — | ISA semantics only |
| M2-010 | C | Реализовать branch, HLT и reserved-opcode behavior | PLANNED | — | — | Approved ISA behavior |
| M2-011 | C | Интегрировать FLAGS policies и diagnostics | PLANNED | — | — | Undefined conditional flag policy |
| M2-012 | D | Добавить emulator instruction and state tests | PLANNED | — | — | Emulator test layer |
| M2-013 | D | Выполнить full emulator regression and documentation review | PLANNED | — | — | No microarchitecture parity |
| M2-014 | D | Подготовить final report и release readiness | PLANNED | — | — | Hardware remains `NOT_TESTED` |

## Обязательные поля task report

Каждый task report должен содержать:

```markdown
# Task M2-XXX: <title>

## Summary
## Sources
## Scope
## Design decision
## Changes
## Tests
## Verification
## Architectural compliance
## Result
## Commit
## Follow-up
```

Report обязан явно указывать:

- phase и task ID;
- изменённые files;
- production code status;
- execution policy, если задача затрагивает undefined FLAGS;
- отсутствие simulator/control-word/hardware coupling;
- hardware status `NOT_TESTED` до отдельной physical verification.

## Status rules

`PLANNED` означает, что задача описана, но её implementation не завершена. `COMPLETED` означает, что task scope реализован, проверен, documented и committed. Report не должен представлять software test как hardware `PASS`.

## Workflow and commits

Одна инженерная задача оформляется одним atomic commit с approved prefix. После завершения каждой фазы обязательны regression, clean-tree check, push checkpoint и проверка remote tracking. Push checkpoint не заменяет финальный milestone review и tag procedure.

## Hardware status

```text
NOT_TESTED
```

## Связанные решения и документы

- [План Milestone 2](../../plans/milestone-2-isa-reference-emulator.md) определяет roadmap, scope и acceptance criteria.
- [Архитектура R8 v1](../../architecture.md), [ISA](../../isa.md), [микроархитектура](../../microarchitecture.md), [Control Word](../../control-word.md) и [memory](../../memory.md) являются источниками task reports.
- [Индекс ADR](../../adr/README.md) содержит активные решения, обязательные для emulator boundary.
- [Локальная проверка software](../../testing/software.md) определяет verification workflow.
