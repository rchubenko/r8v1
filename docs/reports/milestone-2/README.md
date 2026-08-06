# Отчёты Milestone 2: ISA Reference Emulator

## Назначение

Каталог хранит task reports Milestone 2. Этот README определяет структуру отчётов и не является ISA, architecture, microarchitecture или control-word specification.

**Статус Milestone 2:** `PLANNED`

**Аппаратная проверка:** `NOT_TESTED`

## Границы отчётов

Отчёты должны описывать только ISA Reference Emulator и его deterministic software verification. Они не должны смешивать emulator с Microarchitecture Simulator, `control word`, microsteps, DATA BUS execution, clock orchestration или hardware.

Текущая documentation task создаёт только plan и этот index. Пустые task reports заранее не создаются.

## Нумерация и именование

Task reports используют последовательную нумерацию `001..026` и имя:

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
| M2-001 | A | Зафиксировать Milestone 2 plan и report index | COMPLETED | [`001-milestone-2-plan-and-index.md`](001-milestone-2-plan-and-index.md) | 92aa04f | Documentation baseline этой задачи |
| M2-002 | A | Зафиксировать emulator state и atomic transition contract | COMPLETED | [`002-emulator-execution-contract.md`](002-emulator-execution-contract.md) | 4ba49b8 | Atomic architectural contract; implementation не выполнялась |
| M2-003 | B | Добавить opcode и decoded instruction values | COMPLETED | [`003-opcode-and-decoded-instruction-values.md`](003-opcode-and-decoded-instruction-values.md) | f2c2237 | Typed decode foundation; reserved opcode remain representable |
| M2-004 | B | Добавить architectural emulator state | COMPLETED | [`004-architectural-emulator-state.md`](004-architectural-emulator-state.md) | 2edc01e | Architectural state construction and safe observation |
| M2-005 | B | Реализовать architectural reset | COMPLETED | [`005-architectural-reset.md`](005-architectural-reset.md) | d9189b1 | Deterministic reset behavior; SRAM preserved |
| M2-006 | B | Добавить exact executable image loading | COMPLETED | [`006-executable-image-loading.md`](006-executable-image-loading.md) | 0655304 | Validated 4096-byte image input; atomic SRAM replacement |
| M2-007 | B | Реализовать atomic fetch и post-fetch PC behavior | COMPLETED | [`007-atomic-instruction-fetch.md`](007-atomic-instruction-fetch.md) | 8503845 | Atomic ISA layer; PC/IR update only |
| M2-008 | B | Добавить immutable architectural snapshots | COMPLETED | [`008-architectural-state-snapshots.md`](008-architectural-state-snapshots.md) | 11e93bf | Safe architectural observation; optional full memory capture |
| M2-009 | C | Реализовать NOP и LDI | COMPLETED | [`009-nop-and-ldi.md`](009-nop-and-ldi.md) | 9506ae8 | Atomic execution boundary for NOP/LDI |
| M2-010 | C | Реализовать LDA | COMPLETED | [`010-lda.md`](010-lda.md) | d36cb20 | Atomic LDA execution with full 12-bit addressing |
| M2-011 | C | Реализовать ADD | COMPLETED | [`011-add.md`](011-add.md) | fe92ca1 | Atomic ADD execution; exhaustive 256 x 256 coverage |
| M2-012 | C | Реализовать SUB | COMPLETED | [`012-sub.md`](012-sub.md) | 1d8a2d7 | Atomic SUB execution; exhaustive 256 x 256 coverage |
| M2-013 | C | Реализовать STA | COMPLETED | [`013-sta.md`](013-sta.md) | cc9a5b1 | Atomic STA execution; exact-one-byte and self-modifying coverage |
| M2-014 | D | Реализовать JMP | COMPLETED | [`014-jmp.md`](014-jmp.md) | 099c002 | Atomic JMP execution; full 12-bit and odd-target coverage |
| M2-015 | D | Реализовать JZ и JN | COMPLETED | [`015-jz-and-jn.md`](015-jz-and-jn.md) | 4312956 | Atomic JZ/JN; taken/not-taken and mask-preservation coverage |
| M2-016 | D | Реализовать undefined-flag diagnostics | COMPLETED | [`016-undefined-conditional-flag-diagnostics.md`](016-undefined-conditional-flag-diagnostics.md) | a67f870 | Execution policies and immutable diagnostics; JC/JV remain separate |
| M2-017 | D | Реализовать JC и JV | COMPLETED | [`017-jc-and-jv.md`](017-jc-and-jv.md) | c7dbc8e | Policy-aware JC/JV; defined/undefined C/O coverage |
| M2-018 | D | Реализовать HLT | COMPLETED | [`018-hlt.md`](018-hlt.md) | c66e48e | Atomic HLT and halted-guard/no-fetch coverage |
| M2-019 | D | Реализовать reserved-opcode halt | COMPLETED | [`019-reserved-opcode-halt.md`](019-reserved-opcode-halt.md) | 52c322f | Four reserved opcodes halt with IR-derived diagnostics |
| M2-020 | D | Реализовать instruction dispatcher | PLANNED | — | — | Deterministic opcode dispatch |
| M2-021 | D | Добавить structured step result | PLANNED | — | — | Observable step outcome |
| M2-022 | D | Добавить bounded execution helper | PLANNED | — | — | Deterministic bounded execution |
| M2-023 | E | Подготовить conformance matrix | PLANNED | — | — | Instruction and policy coverage |
| M2-024 | E | Добавить integration programs | PLANNED | — | — | End-to-end emulator scenarios |
| M2-025 | E | Проверить boundary and drift cases | PLANNED | — | — | Boundary and source-of-truth verification |
| M2-026 | F | Выполнить final regression and documentation review | PLANNED | — | — | Hardware remains `NOT_TESTED` |

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
