# Task M2-002: ISA Emulator Execution Contract

## Summary

Формально определён execution contract ISA Reference Emulator как документационный atomic architectural contract. Реализация emulator, execution code и tests этой задачи не выполнялись.

## Sources

Решение основано на `AGENTS.md`, `README.md`, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/memory.md`, `docs/testing/software.md`, `docs/plans/milestone-2-isa-reference-emulator.md`, `docs/adr/README.md` и всеми active ADR, особенно ADR-0010. Использованы также утверждённые component boundaries Milestone 1 и repository conventions.

В репозитории canonical software testing document находится по адресу `docs/testing/software.md`; файла `docs/software.md` нет.

## Scope

Этот документ определяет только архитектурное поведение будущего ISA Reference Emulator:

- atomic execution одной инструкции;
- ownership persistent architectural state;
- execution environment;
- immutable observation boundaries;
- `STRICT` и `HARDWARE_LIKE` policies;
- non-architectural diagnostics.

Production emulator, execution implementation и tests в Task 002 не создаются.

## Atomic step

Одна atomic step имеет строго следующую логическую последовательность:

```text
halted guard
-> fetch
-> decode
-> execute
-> result
```

### Halted guard

Если `HALT_STATE` уже равен `True`, новая instruction не читается и не исполняется. Результат содержит неизменённое architectural state; reset behavior находится за пределами этой atomic step.

### Fetch

Из текущего `PC` читаются два instruction bytes из unified SRAM. Из них формируются fetched instruction и post-fetch PC с утверждённым modulo-4096 behavior. До формирования result промежуточные значения не являются внешне наблюдаемым state.

### Decode

Fetched bytes интерпретируются согласно `docs/isa.md` как opcode и 12-bit operand. Decode не изменяет architectural state и не принимает configuration policy как часть instruction.

### Execute

Instruction semantics применяются к post-fetch state. Normal instruction effects, FLAGS updates, memory effects, branch target и HALT effect формируют одну atomic transition. Для conditional jump проверка `flags_defined_mask` выполняется после complete fetch и до branch action.

### Result

Каждый successful или diagnostic execution возвращает immutable result boundary с resulting architectural snapshot и diagnostics. Частичные изменения state до result наружу не выдаются.

## Architectural state ownership

ISA Reference Emulator владеет persistent state, необходимым для atomic ISA semantics:

- `A` — accumulator value;
- `PC` — byte-addressed 12-bit program counter;
- `FLAGS` concrete values;
- `flags_defined_mask` как software metadata, связанная с FLAGS state;
- unified SRAM contents;
- `HALT_STATE`.

Instruction bytes, opcode и operand являются immutable fetched context внутри одной step и не образуют отдельного долгоживущего execution environment.

Внутренние значения, не требуемые для ISA-visible transition, не являются отдельными public ownership boundaries emulator contract. Их наличие не может добавлять observable semantics.

### Architectural state и execution environment

Architectural state изменяется только по результату atomic instruction transition. Execution environment содержит:

- выбранную execution policy: `STRICT` или `HARDWARE_LIKE`;
- входной полный SRAM image при создании execution context;
- режим выдачи diagnostics.

Execution policy не хранится в architectural snapshot, не меняется instruction и не является частью CPU state.

## Immutable observation boundaries

Contract использует следующие immutable observations:

- `ArchitecturalStateSnapshot` — immutable values `A`, `PC`, concrete FLAGS, `flags_defined_mask`, SRAM image и `HALT_STATE`;
- `FetchedInstruction` — immutable opcode и operand текущей atomic step;
- `ExecutionResult` — immutable resulting snapshot и ordered diagnostics;
- `Diagnostic` — immutable non-architectural observation с severity и diagnostic identifier.

Snapshots не предоставляют mutable references на SRAM или другие state holders. Повторное чтение observation не изменяет emulator state. Execution policy не включается в `ArchitecturalStateSnapshot`.

ISA Reference Emulator не обещает наблюдаемость промежуточных значений fetch, decode или execute. Наблюдаемым является только input snapshot, resulting snapshot и diagnostics result.

## STRICT execution policy

При conditional jump, который читает architecturally undefined flag:

1. instruction уже полностью fetched;
2. post-fetch PC уже определён;
3. проверяется `flags_defined_mask`;
4. возвращается non-architectural diagnostic `UNDEFINED_CONDITIONAL_FLAG`;
5. branch action не выполняется;
6. PC сохраняется в post-fetch состоянии;
7. `HALT_STATE` не устанавливается.

Другие architectural effects этой instruction не должны быть частично опубликованы при таком diagnostic result.

## HARDWARE_LIKE execution policy

При conditional jump используется concrete physical value требуемого FLAGS field независимо от его `flags_defined_mask`.

- execution продолжается;
- branch action определяется concrete flag value;
- `flags_defined_mask` не изменяется;
- policy не становится частью architectural state;
- допускается warning diagnostic как non-architectural observation.

Concrete FLAGS values и defined metadata остаются различными сущностями: undefined flag имеет concrete value, но не является architecturally defined для `STRICT` policy.

## Non-architectural diagnostics

Diagnostics являются output observation execution environment и не являются architectural state.

Обязательный diagnostic identifier:

```text
UNDEFINED_CONDITIONAL_FLAG
```

Diagnostic не устанавливает `HALT_STATE`, не изменяет `flags_defined_mask`, не меняет ISA encoding и не может сам по себе изменить PC. В `STRICT` он сопровождает отказ от branch action; в `HARDWARE_LIKE` optional warning не останавливает execution.

## Explicit exclusions

В Task 002 не реализуются emulator, simulator, CPU object, instruction execution, opcode decoder, DATA BUS, MAR cycles, MICROSTEP, `control word`, EEPROM, clock edges, hardware или Raspberry Pi integration. Не изменяются ISA, Architecture, Microarchitecture, Control Word, Memory Model или ADR.

Эти exclusions относятся к scope текущей документационной задачи. Они не изменяют будущий Milestone 2 deliverable, которым остаётся отдельная реализация ISA Reference Emulator в последующих phases.

## Verification

Документ проверен `./scripts/check-docs`, `./scripts/verify` и `git diff --check`. Новые tests и production code отсутствуют. Hardware verification не выполнялась; hardware status — `NOT_TESTED`.

## Architectural compliance

Contract не добавляет новых ISA instructions, opcode, registers, memory behavior, reset behavior или diagnostics, меняющих architecture. Execution policy, snapshots и diagnostics явно отделены от architectural CPU state.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
4ba49b8 docs: define ISA emulator execution contract
```

Push не выполняется в рамках текущей documentation task.

## Follow-up

Следующая задача — M2-003: добавить opcode и decoded instruction values. Режимы `STRICT`/`HARDWARE_LIKE` и `UNDEFINED_CONDITIONAL_FLAG` уже зафиксированы в этом report и [документе software testing](../../testing/software.md).

## Связанные решения и документы

- [План Milestone 2](../../plans/milestone-2-isa-reference-emulator.md) определяет phase и dependency context.
- [ISA R8 v1](../../isa.md) является источником instruction encoding и semantics.
- [Архитектура R8 v1](../../architecture.md) и [локальная проверка software](../../testing/software.md) задают emulator boundary и verification rules.
- [ADR-0010](../../adr/0010-deterministic-software-model-semantics.md) фиксирует deterministic software-model behavior.
