# Task M1-020: Component-state container

## Summary

Проведена оценка необходимости общего component-state container. На текущем этапе production container не добавлен: существующие component models уже имеют самостоятельные boundaries, а общий объект не добавляет полезного invariant или lifecycle responsibility.

## Sources

Решение основано на `AGENTS.md`, `README.md`, `docs/plans/milestone-1-component-models.md`, `docs/reports/milestone-1/README.md`, reports Tasks 3–19, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/memory.md`, `docs/adr/README.md` и всеми активными ADR, особенно ADR-0001, ADR-0004, ADR-0005, ADR-0006, ADR-0007 и ADR-0010. Реализация и boundaries сверены со всеми modules в `cpu/`, `cpu/__init__.py`, всеми component unit tests, package/API и typing conventions, `docs/testing/software.md`, `pyproject.toml` и `scripts/verify`.

## Need assessment

Текущего consumer общего container нет. Задачи 1–19 реализуют и тестируют самостоятельные models напрямую: `FixedWidthRegister`, `InstructionRegister`, `MemoryAddressRegister`, `ProgramCounter`, `MicrostepCounter`, `HaltLatch`, `SRAM`, immutable `FlagsSnapshot` и stateless functions.

Потенциальная польза container сводится к созданию canonical набора экземпляров и упрощению будущих structural/integration tests. Сейчас такой набор не требуется утверждённым test boundary: Task 21 может выполнять допустимые связи напрямую между отдельными models, например передавать `InstructionRegister.operand` в `select_address()` или результат `evaluate()` в FLAGS policy.

Container не добавил бы нового invariant без одновременного решения нерешённых lifecycle boundaries. Он либо только дублировал бы ручное создание объектов, либо стал бы premature CPU abstraction. Ни один текущий consumer не требует ownership общего набора.

## Decision

`DEFERRED AS UNNECESSARY`

Production component-state container, public API и искусственные structural tests не создаются. Это штатное завершение условной Task 20, а не блокировка или ошибка.

## Considered composition

Рассмотрены следующие fields:

- A и B: отдельные `FixedWidthRegister(width=8, reset_value=0x00)` имеют ясные boundaries, но без container уже полностью определены Task 4; группировка не добавляет ownership.
- PC: существующий `ProgramCounter` имеет собственные width, reset и modulo behavior; общий container не нужен для этого invariant.
- IR: существующий `InstructionRegister` самостоятельно владеет IRH/IRL и derived views; его composition не требует внешнего holder.
- MAR: существующий `MemoryAddressRegister` является отдельным 12-bit stateful boundary; address selection остаётся отдельной stateless function.
- MICROSTEP: существующий `MicrostepCounter` имеет собственный lifecycle и implicit hold; orchestration не входит в Task 20.
- HALT: существующий `HaltLatch` имеет собственный lifecycle; HALT blocking и edge semantics принадлежат будущему simulator/clock layer.
- FLAGS: не включены, поскольку существует только immutable `FlagsSnapshot` и stateless FLAGS policy; mutable FLAGS holder отсутствует.
- SRAM: не включена, поскольку SRAM имеет отдельный lifecycle, CPU reset не очищает её, а ownership относится loader/hardware boundaries согласно ADR-0007.

Такой анализ не изменяет архитектуру, ISA, memory model или ADR.

## FLAGS state

Сейчас доступны immutable `FlagValues`, `FlagsDefinedMask` и `FlagsSnapshot`, включая `FlagsSnapshot.reset()`. FLAGS latch policy реализована stateless functions. Mutable FLAGS register или holder не утверждён.

Создание container с initial snapshot сделало бы API неполным: было бы не определено, как заменять snapshot без добавления mutable FLAGS lifecycle или latch orchestration. Поэтому FLAGS не включены и новый `FlagsRegister`, `set_flags()` или mutable wrapper не создавались.

## SRAM ownership

`SRAM` остаётся отдельным stateful component с независимым zero-filled construction и без `reset()`/`clear()`. CPU reset не очищает SRAM. Loader ownership, CPU ownership и break-before-make относятся ADR-0007 и будущим loader/hardware layers.

Включение SRAM в общий container сейчас смешало бы CPU component grouping с memory ownership и lifecycle coordination. Поэтому SRAM не включена; ADR-0001, ADR-0007 и software image contract не изменены.

## Changes

- Production code не изменялся.
- Public API `cpu` не изменялся.
- Новые unit tests и placeholder tests не добавлялись.
- Создан этот design report.
- Обновлён milestone index; Task 20 отмечена как `COMPLETED` с решением `DEFERRED AS UNNECESSARY`.

## Tests

Новые production tests отсутствуют, поскольку production container не создавался. Существующие component tests остаются прямыми unit tests отдельных boundaries и не дублируются.

Task 21 может выполнять допустимые component-level integration tests напрямую между independent models, без общего container и без mini-simulator.

## Performance

```text
time ./scripts/verify: real 3.905s
pytest: 558 passed in 2.95s
```

Runtime остаётся практичным для полного regression run. Timing не закрепляется жёстким assertion.

## Verification

После documentation changes выполнены `time ./scripts/verify` и `git diff --check`. Formatting, lint, mypy, pytest и documentation checks проходят. Hardware verification не выполняется; hardware status — `NOT_TESTED`.

## Architectural compliance

Не добавлены `step()`, `execute()`, `decode()`, `fetch()`, `tick()`, `clock()`, `clock_edge()`, `reset_all()`, `run()`, `load_instruction()` или `apply_control_word()`.

Не добавлены instruction semantics, opcode/control-word decode, fetch T0–T3, microcode, branch logic, DATA BUS/address orchestration, A/FLAGS simultaneous latch, memory cycle, HALT blocking, reset coordinator, emulator, simulator, loader или hardware work.

Компоненты продолжают создаваться независимо; их local `reset()` methods не координируются общим API.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
docs: assess component state container
```

Push и tag не выполняются.

## Follow-up

Следующая задача — Task 21: component-level integration tests. Container может быть пересмотрен только при появлении конкретного consumer, который требует canonical ownership набора компонентов и не вводит complete CPU abstraction.
