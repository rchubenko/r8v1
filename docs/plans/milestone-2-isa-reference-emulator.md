# Milestone 2: ISA Reference Emulator

## Статус

**Статус:** `PLANNED`

**Аппаратная проверка:** `NOT_TESTED`

## Цель milestone

Создать детерминированную ISA Reference Emulator, которая является атомарной архитектурной моделью R8 v1 и исполняет утверждённую ISA без microsteps, `control word`, DATA BUS execution, clock orchestration или hardware dependencies.

Эта модель предназначена для software reference behavior. Она не является реализацией полного физического CPU и не заменяет будущий Microarchitecture Simulator.

## Source of truth

Приоритет источников определяется `AGENTS.md`. План опирается на:

- `AGENTS.md`;
- `README.md`;
- `docs/architecture.md`;
- `docs/isa.md`;
- `docs/microarchitecture.md`;
- `docs/control-word.md`;
- `docs/memory.md`;
- `docs/repository-structure.md`;
- `docs/testing/software.md`;
- `docs/adr/README.md` и все перечисленные там active ADR;
- отчёты Milestone 0 и итоговый report Milestone 1.

В репозитории отсутствует `docs/software.md`; канонический документ software testing policy имеет путь `docs/testing/software.md` и используется как источник для execution policies.

Этот план не изменяет смысл нормативных документов и не создаёт новый ADR.

## Границы milestone

ISA Reference Emulator:

- исполняет одну инструкцию атомарно;
- использует утверждённые ISA semantics и unified 4 KB SRAM image;
- поддерживает архитектурные registers, FLAGS values и `flags_defined_mask`;
- выполняет fetch и instruction transition как одну software architectural operation;
- предоставляет deterministic diagnostics, не являющиеся architectural CPU state;
- поддерживает `STRICT` и `HARDWARE_LIKE` execution policies для undefined conditional flags.

Emulator не исполняет microsteps и не моделирует физическую последовательность bus, latch и clock transitions.

### Граница с Microarchitecture Simulator

Microarchitecture Simulator является отдельным будущим layer. Он будет использовать реальные `control word`, microsteps, DATA BUS, rising edges и register latching. ISA Reference Emulator не вызывает simulator и simulator не заменяется emulator.

Разделение ответственности:

| Layer | Ответственность | Не входит в layer |
|---|---|---|
| ISA Reference Emulator | Атомарная ISA semantics и architectural state transition | `control word`, microsteps, DATA BUS execution, clock, hardware |
| Microarchitecture Simulator | Исполнение реальных control words через microsteps и rising edges | Вызов atomic ISA implementation как замена microarchitectural behavior |

## Deliverables

Будущие deliverables Milestone 2:

- deterministic ISA Reference Emulator package;
- architectural emulator state, использующий утверждённые register, IR, PC, FLAGS и SRAM boundaries;
- atomic fetch/execute transition для всех утверждённых v1 instructions;
- `STRICT` и `HARDWARE_LIKE` execution policy и non-architectural diagnostics;
- deterministic emulator tests, включая instruction, state, reset, memory и undefined-flag behavior;
- документация public emulator boundary и diagnostics;
- task reports и итоговый Milestone 2 report.

Текущая documentation task создаёт только этот plan, report index и обновление software testing documentation. Production emulator, tests и package files сейчас не создаются.

## Explicit exclusions

### Исключения текущей documentation task

В рамках подготовки этого плана запрещено реализовывать:

- emulator;
- simulator;
- instruction execution;
- opcode decoder;
- CPU;
- `control word` execution;
- microcode;
- EEPROM generation;
- assembler;
- loader;
- parity;
- Raspberry Pi integration;
- hardware;
- GPIO;
- tests, кроме существующих проверок документации.

### Исключения Milestone 2

Даже после начала реализации Milestone 2 в его scope не входят:

- Microarchitecture Simulator;
- `control word` decoding или execution;
- EEPROM и generated microcode;
- microstep sequencing;
- DATA BUS producer/consumer execution;
- rising-edge и clock orchestration;
- hardware adapters, GPIO и physical verification;
- assembler и loader;
- parity с Microarchitecture Simulator;
- изменение ISA, architecture, microarchitecture, control-word specification, memory model или ADR.

Фраза «ISA Reference Emulator» в deliverables относится к будущим implementation phases; текущий commit является documentation-only.

## Повторное использование Milestone 1

Milestone 2 переиспользует без изменения:

- width/value validation и `FixedWidthRegister` для approved storage boundaries;
- `ProgramCounter` для 12-bit modulo address behavior;
- `InstructionRegister` для IRH/IRL и derived opcode/operand views;
- `MemoryAddressRegister` только как approved state boundary, без address-path orchestration;
- `SRAM` и full-image replacement для unified 4096-byte image;
- stateless ADD/SUB ALU и unified `evaluate()`;
- immutable `FlagsSnapshot`, `FlagsDefinedMask` и FLAGS latch policy;
- утверждённые `HaltLatch` semantics для HALT state;
- existing validation and diagnostic conventions.

Component-state container из Task 20 не вводится: emulator state boundary должен быть определён отдельной задачей и не должен молча переименовывать или расширять Milestone 1 container decision.

## Undefined FLAGS execution policy

Execution policy является конфигурацией execution environment и не входит в architectural CPU state.

Разрешены ровно две policy:

### `STRICT`

При conditional jump:

1. instruction уже полностью fetched;
2. определяется требуемый flag;
3. проверяется `flags_defined_mask` до branch action;
4. при undefined flag возвращается non-architectural diagnostic `UNDEFINED_CONDITIONAL_FLAG`;
5. branch action не выполняется;
6. PC остаётся в post-fetch состоянии;
7. `HALT_STATE` не устанавливается.

### `HARDWARE_LIKE`

При conditional jump используется concrete physical FLAGS value. `flags_defined_mask` не изменяется. Execution продолжается; реализация может дополнительно записать warning diagnostic.

Эта policy не изменяет ISA encoding, instruction semantics, architectural state layout или reset behavior.

## Фазы реализации

### Phase A — Specification and emulator contract

- Зафиксировать emulator boundary и atomic transition contract.
- Зафиксировать state ownership, input image contract и reset entry conditions.
- Зафиксировать `STRICT`, `HARDWARE_LIKE` и diagnostics contract.
- Подготовить deterministic test matrix для всех ISA instructions.

### Phase B — Architectural state and fetch

- Реализовать minimal emulator state boundary на основе approved Milestone 1 models.
- Реализовать construction/reset и validated full-image input.
- Реализовать atomic instruction fetch и post-fetch PC state.
- Проверить, что fetch не использует microsteps, `control word` или physical bus model.

### Phase C — Atomic ISA execution

- Реализовать non-branch instructions согласно `docs/isa.md`.
- Реализовать arithmetic result и FLAGS updates через approved ALU/FLAGS policy.
- Реализовать memory read/write instructions через unified SRAM contract.
- Реализовать unconditional and conditional branches с двумя approved execution policies.
- Реализовать HLT и reserved-opcode halt согласно ISA semantics.

### Phase D — Emulator regression and documentation

- Выполнить deterministic emulator unit and instruction tests.
- Проверить reset, PC boundary, SRAM persistence и diagnostics.
- Проверить отсутствие simulator/control-word coupling.
- Обновить emulator documentation и подготовить итоговый report.

## Последовательность инженерных задач

| ID | Phase | Task | Result |
|---|---|---|---|
| M2-001 | A | Зафиксировать Milestone 2 plan и report index | Documentation baseline |
| M2-002 | A | Зафиксировать emulator state и atomic transition contract | Approved emulator boundary |
| M2-003 | A | Зафиксировать execution policies и diagnostics | `STRICT`/`HARDWARE_LIKE` contract |
| M2-004 | A | Подготовить emulator instruction test matrix | Deterministic test specification |
| M2-005 | B | Реализовать emulator state и validated image input | Stateful emulator foundation |
| M2-006 | B | Реализовать atomic fetch и post-fetch PC behavior | Fetch boundary |
| M2-007 | C | Реализовать non-branch ISA instructions | Atomic data/memory semantics |
| M2-008 | C | Реализовать branch, HLT и reserved-opcode behavior | Complete control-flow semantics |
| M2-009 | C | Интегрировать FLAGS policies и diagnostics | Undefined-flag behavior |
| M2-010 | D | Добавить emulator instruction and state tests | Emulator regression coverage |
| M2-011 | D | Выполнить full emulator regression and documentation review | Verified milestone scope |
| M2-012 | D | Подготовить final report и release readiness | Milestone 2 completion candidate |

Каждая implementation task выполняется в порядке specification -> production code -> tests -> regression -> documentation. Архитектурные вопросы, обнаруженные в ходе задач, блокируют только затронутую часть до принятия решения.

## Dependency graph

```text
M2-001
  -> M2-002 -> M2-003 -> M2-004
  -> M2-005 -> M2-006
  -> M2-007 -> M2-008 -> M2-009
  -> M2-010 -> M2-011 -> M2-012
```

Точнее:

```text
M2-001 -> M2-002
M2-002 -> M2-003
M2-003 -> M2-004
M2-002 -> M2-005
M2-005 -> M2-006
M2-006 -> M2-007
M2-007 -> M2-008
M2-003 -> M2-009
M2-008 -> M2-009
M2-009 -> M2-010
M2-010 -> M2-011
M2-011 -> M2-012
```

Milestone 1 components являются prerequisite для M2-005, а не частью dependency graph повторно реализуемых production features.

## Acceptance criteria

Milestone 2 может быть завершён только если:

- ISA Reference Emulator существует как отдельный atomic architectural layer;
- все утверждённые v1 ISA instructions исполняются согласно `docs/isa.md`;
- instruction fetch и post-fetch PC behavior детерминированы;
- FLAGS values и `flags_defined_mask` соответствуют approved policy;
- `STRICT` возвращает `UNDEFINED_CONDITIONAL_FLAG`, не выполняет branch, сохраняет post-fetch PC и не устанавливает HALT;
- `HARDWARE_LIKE` использует concrete flag value, сохраняет `flags_defined_mask` и продолжает execution;
- execution policy не является architectural CPU state;
- HLT и reserved-opcode halt соответствуют утверждённой ISA semantics;
- SRAM image contract и CPU reset persistence не нарушены;
- emulator не использует microsteps, `control word`, EEPROM, DATA BUS execution, clock или hardware APIs;
- Microarchitecture Simulator не вызывается и не реализуется внутри emulator;
- deterministic emulator tests проходят;
- documentation и reports синхронизированы с источниками истины;
- `./scripts/verify` и `git diff --check` проходят;
- hardware status остаётся `NOT_TESTED`.

## Workflow проекта

Для каждой задачи:

1. изучить source-of-truth documents;
2. зафиксировать design decision без изменения architecture;
3. реализовать только scope задачи;
4. добавить соответствующие deterministic tests;
5. выполнить regression;
6. обновить documentation и task report;
7. проверить generated artifacts и `git diff --check`;
8. создать atomic commit с approved prefix;
9. выполнить обязательный push checkpoint фазы;
10. перейти к следующей задаче только после проверки remote state.

### Обязательные push checkpoints

После завершения каждой фазы:

- выполнить соответствующую regression;
- проверить clean working tree;
- создать atomic commits фазы;
- отправить commits в configured remote;
- проверить branch tracking и remote HEAD;
- не создавать milestone tag до завершения всех фаз и финального review.

Для текущей documentation task workflow ограничен изучением документации, подготовкой документов, documentation checks, `./scripts/verify`, `git diff --check` и одним atomic commit. Push этой задачи не выполняется автоматически без отдельного Git/release запроса.

## Regression

Обязательная software regression для каждой implementation phase:

```bash
time ./scripts/verify
```

Targeted emulator tests выполняются дополнительно, когда production emulator появится. Ни одна software regression не является hardware verification.

## Hardware status

```text
NOT_TESTED
```

Milestone 2 не включает physical CPU, hardware adapters, GPIO или hardware `PASS`.
