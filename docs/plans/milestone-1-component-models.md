# Milestone 1: Component Models

## Статус

**Статус:** Активен
**Аппаратная проверка:** `NOT_TESTED`

## Цель

Создать детерминированные программные модели отдельных компонентов CPU. Milestone не является реализацией процессора, ISA emulator или microarchitecture simulator.

## Источники истины

План опирается на `AGENTS.md`, `README.md`, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/memory.md`, `docs/repository-structure.md`, `docs/testing/software.md` и активные ADR из `docs/adr/README.md`. Этот план не изменяет смысл нормативных документов и не заменяет их.

## Область и границы

Repository boundary Milestone 1 — `cpu/`. В нём могут находиться reusable component models и необходимые state containers, но не instruction decoder и не complete CPU loop.

Планируемые component models и границы:

- width/value primitives для 4-bit, 8-bit и 12-bit значений;
- fixed-width register abstraction;
- A register boundary и B register boundary;
- MAR;
- Program Counter;
- Instruction Register;
- ALU ADD и ALU SUB;
- unified public ALU model;
- DATA BUS resolver;
- address source selector;
- FLAGS values и `flags_defined_mask`;
- FLAGS latch policy при записи A;
- SRAM storage;
- full-image replacement;
- MICROSTEP counter;
- HALT latch;
- при необходимости component-state container;
- component-level integration tests.

Models обязаны сохранять утверждённые ширины и диапазоны: данные 8 bit, адреса 12 bit, instruction views из IR — opcode 4 bit и operand 12 bit, SRAM — `0x000..0xFFF`. Компоненты имеют самостоятельную ответственность и состояние. Их реализация не должна добавлять скрытые instruction semantics.

## Исключения из области

Milestone 1 не включает:

- opcode decoder;
- instruction execution;
- ISA reference emulator;
- microarchitecture simulator;
- fetch T0–T3 orchestration;
- control-word decode;
- control-word execution;
- microcode definitions;
- microcode generator;
- EEPROM artifacts;
- complete CPU clock-edge transition;
- assembler;
- loader protocol;
- memory ownership implementation;
- hardware adapters;
- hardware assembly;
- hardware verification;
- hardware `PASS`;
- autonomous clock;
- Raspberry Pi GPIO integration.

В частности, IR не вызывает HALT для reserved opcode, ALU не декодирует numeric control word, DATA BUS не реализует consumer semantics или `OE_SEL` decoding, а компоненты не выполняют инструкции и не координируют fetch.

## Допустимый test layer

Допускаются:

- unit tests отдельных компонентов;
- property, parametrized или exhaustive tests, если это оправдано;
- component-level integration tests только между независимыми component boundaries;
- детерминированные и воспроизводимые tests;
- проверки reset, width, boundary и invalid-input behavior.

Запрещены tests, которые исполняют инструкции, моделируют полный CPU cycle, организуют fetch T0–T3, выполняют control word или заменяют component boundary готовой атомарной реализацией CPU. Tests не вводят новую архитектурную semantics и не являются hardware verification.

## Критерии приёмки

Milestone считается завершённым, когда:

- все утверждённые component models реализованы;
- компоненты имеют изолированные responsibilities;
- width/range invariants проверяются;
- reset behavior соответствует architecture;
- PC работает modulo `0x1000`;
- IR корректно предоставляет opcode и 12-bit operand views;
- ALU ADD/SUB соответствует ISA formulas;
- FLAGS содержит concrete values и `flags_defined_mask`;
- DATA BUS представляет отсутствие producer как `HIGH_Z`/`None` и обнаруживает contention;
- address path остаётся отдельным от DATA BUS;
- SRAM содержит ровно 4096 bytes, новая software memory заполнена `0x00`, а full-image replacement принимает только image ровно 4096 bytes;
- CPU reset не очищает SRAM;
- MICROSTEP и HALT представлены как самостоятельные state elements;
- отсутствуют instruction decoder и execution loop;
- отсутствуют emulator и simulator;
- hardware work отсутствует, hardware status остаётся `NOT_TESTED`;
- `./scripts/verify` проходит;
- документация не расходится с architecture и ADR.

## Порядок реализации

### Фаза A — Общие примитивы

#### Task 1. Зафиксировать specification Milestone 1

Documentation-only task: создать этот план и индекс отчётов, описать workflow, задачи и acceptance criteria, выполнить verification и подготовить атомарный commit. Component models, tests поведения, emulator, simulator, microcode, assembler, loader и hardware integration не реализуются.

#### Task 2. Добавить width/value primitives

Добавить masks/ranges для 4-bit, 8-bit и 12-bit values, validation byte/address/nibble и project-specific invalid component input error. Универсальный bit-vector framework не создавать.

### Фаза B — Простые stateful components

#### Task 3. Реализовать базовый fixed-width register

Задать initial/reset value, read, explicit load и range validation с boundary tests. Не добавлять PC increment и IR decoding.

#### Task 4. Реализовать A и B register boundaries

Определить подходящие boundaries в соответствии со стилем repository. Не создавать бессодержательные classes только ради имён.

#### Task 5. Реализовать MAR

Добавить 12-bit storage, reset `0x000`, load/read и boundary tests. MAR не выбирает PC или IR operand самостоятельно.

#### Task 6. Реализовать Program Counter

Добавить reset, hold, modulo increment, parallel load и переход `0xFFF -> 0x000`. Fetch orchestration не входит.

#### Task 7. Реализовать Instruction Register

Добавить independent load IRH/IRL, reset, opcode view, operand view и extraction tests. Reserved opcode не вызывает HALT внутри IR.

### Фаза C — Combinational components

#### Task 8. Реализовать ALU ADD

Реализовать result modulo 256, Z/C/S/O, immutable result и parametrized или exhaustive tests.

#### Task 9. Реализовать ALU SUB

Реализовать result modulo 256, no-borrow C, signed overflow и boundary tests. Обязательно проверить `0x00 - 0x01`, `0x80 - 0x01`, `0x7F - 0xFF`, equal operands и underflow.

#### Task 10. Объединить ADD/SUB в публичную ALU model

Предоставить explicit mode только ADD/SUB и stateless evaluation API. Numeric control-word decoding не добавлять.

#### Task 11. Реализовать DATA BUS resolver

Поддержать `HIGH_Z`/`None`, single producer и contention. Consumer semantics и `OE_SEL` decoding не входят.

#### Task 12. Реализовать address source selector

Поддержать PC source, IR operand source, 12-bit output и invalid source rejection. `ADDR_SEL` bit decoding и MAR latching не входят.

### Фаза D — FLAGS

#### Task 13. Реализовать Flags value и defined mask

Предоставить concrete Z/C/S/O, mask каждого flag, reset values `0000`, reset mask со всеми defined flags и immutable snapshots.

#### Task 14. Реализовать FLAGS latch policy для записи A

Использовать Z/S из byte, записываемого в A, C/O из concrete ALU outputs, full-defined и partial-defined policy, preserve и reset. API не содержит instruction mnemonics.

#### Task 15. Добавить exhaustive/parameterized flags tests

Проверить ADD, SUB, Z/S при non-ALU A write, concrete C/O, defined mask transitions, preserve и reset. Проверить приемлемое время полного `./scripts/verify`.

### Фаза E — Память и управляющие state elements

#### Task 16. Реализовать SRAM storage model

Создать ровно 4096 zero-filled bytes, read/write, strict address/value validation и сохранение содержимого при CPU reset. Snapshot/export добавлять только при необходимости тестов.

#### Task 17. Реализовать full-image replacement

Поддержать image ровно 4096 bytes и atomic replacement; invalid length rejected. Assembler layout не входит.

#### Task 18. Реализовать MICROSTEP counter

Поддержать T0–T15, modulo increment, explicit return T0, hold и reset. Validation microcode sequence beyond T15 остаётся вне component model.

#### Task 19. Реализовать HALT latch

Задать initial/reset false, latch true и hold true до reset. Автоматическая блокировка других components не входит.

### Фаза F — Состояние и интеграционные границы

#### Task 20. Создать component-state container

Условная задача: container создаётся только если действительно нужен component boundaries или tests. Возможное содержание: A, B, PC, IR, MAR, FLAGS, MICROSTEP, HALT и SRAM только при соответствии утверждённым repository boundaries. Запрещены `step()`, `execute()`, `decode()`, `fetch()`, control word и clock-edge orchestration.

#### Task 21. Добавить component-level integration tests

Допустимы IR operand -> address selector, PC value -> address selector, ALU result -> FLAGS latch, SRAM byte -> single DATA BUS producer и reset отдельных stateful components. Fetch T0–T3, instruction execution, control-word execution, complete rising edge и full CPU state transition запрещены.

#### Task 22. Documentation and milestone regression

Обновить component documentation, перечислить реализованные boundaries, явно отметить отсутствие emulator/simulator, выполнить `./scripts/verify` и `git diff --check`, проверить отсутствие architectural drift и подготовить final milestone report. Milestone release готовить только после отдельного разрешения.

## Зависимости

| Задача | Зависит от |
|---|---|
| Task 1 | — |
| Task 2 | Task 1 |
| Tasks 3, 8, 11, 13, 16, 18 | Task 2 |
| Tasks 4, 5, 6, 7, 19 | Task 3 |
| Task 9 | Task 8 |
| Task 10 | Tasks 8, 9 |
| Task 12 | Tasks 6, 7 |
| Task 14 | Tasks 10, 13 |
| Task 15 | Task 14 |
| Task 17 | Task 16 |
| Task 20 | Tasks 3–19, optional |
| Task 21 | Required completed components |
| Task 22 | All previous tasks |

Зависимости ограничены фактическими границами компонентов. Независимые задачи после Task 2 могут выполняться параллельно, если это не нарушает порядок фаз и atomic commit workflow.

## Workflow и атомарные commits

Для каждой задачи:

1. изучить source-of-truth documentation;
2. выполнить только scope одной задачи;
3. реализовать изменения;
4. добавить или обновить tests;
5. обновить документацию только в пределах задачи;
6. выполнить `./scripts/verify`;
7. выполнить `git diff --check`;
8. создать task report в `docs/reports/milestone-1/`;
9. предложить atomic commit;
10. после review перейти к следующей задаче.

Принцип: `one engineering task -> one atomic commit`. Несколько commits допустимы только если задача объективно требует нескольких независимо проверяемых атомарных изменений; причина должна быть указана в task report. Push и milestone tag не выполняются без отдельного разрешения. Hardware tests не выполняются, hardware status остаётся `NOT_TESTED`.

Рекомендуемый commit для Task 1:

```text
docs: define milestone 1 component models plan
```

## Документация и exit gate

Отчёты задач хранятся в `docs/reports/milestone-1/README.md`. Итоговый report должен отделять утверждённую архитектуру, программную проверку, отсутствие hardware verification и отложенные возможности. Milestone exit gate — все критерии приёмки выше, успешный `./scripts/verify`, чистая проверка diff и отсутствие реализации за пределами scope.

На текущей задаче создаются только specification и report index. Python-код компонентов, component behavior tests, emulator, simulator, microcode, assembler, loader и hardware integration не создаются.
