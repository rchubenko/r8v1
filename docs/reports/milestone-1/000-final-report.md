# Milestone 1 — Component Models

## Goal

Создать детерминированные software models отдельных R8 v1 CPU components, проверить их width/range/reset invariants и component-level interactions без реализации полного CPU, emulator или simulator.

## Sources

Итог основан на `AGENTS.md`, `README.md`, `docs/plans/milestone-1-component-models.md`, reports Tasks 1–21, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/memory.md`, `docs/adr/README.md` и всех активных ADR. Проверены package layout, `cpu/`, tests, `docs/testing/software.md`, `pyproject.toml` и repository verification scripts.

## Completed work

Завершены Tasks 1–22:

- зафиксирована спецификация Milestone 1 и workflow;
- добавлены width/value primitives и `FixedWidthRegister`;
- определены A/B boundaries, MAR, PC и IR;
- реализованы ADD, SUB, unified ALU, DATA BUS resolver и address selector;
- реализованы FLAGS values, defined mask и FLAGS latch policy с exhaustive coverage;
- реализованы SRAM, full-image replacement, MICROSTEP counter и HALT latch;
- проведена оценка component-state container: `DEFERRED AS UNNECESSARY`;
- добавлены component-level integration tests;
- выполнены documentation update, architectural drift review и полная regression.

## Implemented component boundaries

- Width/value primitives: строгая проверка 4-bit, 8-bit и 12-bit значений без masking.
- `FixedWidthRegister`: общее storage boundary с initial/reset value, read, load и reset.
- A/B register boundary: независимые 8-bit `FixedWidthRegister` instances без отдельных wrappers.
- `MemoryAddressRegister`: отдельный 12-bit MAR с reset `0x000`.
- `ProgramCounter`: 12-bit byte-addressed counter с load, reset и modulo increment.
- `InstructionRegister`: независимые IRH/IRL bytes и derived opcode/operand views.
- ALU: stateless ADD/SUB operations через unified `evaluate()` API с immutable result и concrete flags.
- DATA BUS resolver: `HIGH_Z`/`None`, single producer и contention detection.
- Address selector: выбор PC или IR operand на отдельном 12-bit address path.
- FLAGS values: immutable concrete Z/C/S/O values, defined mask и `FlagsSnapshot`.
- FLAGS policy: stateless full-defined, partial-defined, preserve и reset policies.
- SRAM: fixed 4096-byte zero-filled storage с validated read/write.
- Image replacement: atomic replacement полной image ровно 4096 bytes.
- `MicrostepCounter`: самостоятельный T0–T15 counter с modulo increment, return T0 и reset.
- `HaltLatch`: самостоятельный boolean latch с latch, hold и reset.
- Component-level integration tests: deterministic checks совместимости boundaries и local reset separation.

Task 20 общего component-state container не создала: canonical ownership набора components пока не нужен и не добавляет отдельной ответственности.

## Component interactions

Проверены только component-level связи:

- IR operand -> address selector;
- PC value -> address selector, включая `0xFFF -> 0x000` wrap;
- ALU result -> FLAGS latch policy;
- SRAM read byte -> single DATA BUS producer;
- local reset boundaries для stateful components;
- сохранение SRAM contents при reset остальных components.

Эти tests передают готовые значения между boundaries и не являются CPU execution tests.

## Explicit exclusions

Milestone 1 намеренно не реализует:

- CPU execution;
- fetch;
- instruction execution;
- control-word execution;
- clock orchestration;
- rising edge;
- CPU reset coordinator;
- emulator;
- simulator;
- hardware adapters;
- EEPROM model;
- Raspberry Pi GPIO layer;
- opcode decoder, microcode, branch logic, assembler и loader.

Milestone 1 intentionally does not implement an emulator or a simulator.

Также отсутствуют complete CPU object, HALT blocking, memory ownership orchestration и full CPU state transition. Это не недоработки Milestone 1, а границы следующего этапа разработки.

## Regression summary

- Total tests: `589 passed`.
- Component integration tests: `31 passed`.
- `./scripts/verify`: PASS.
- `git diff --check`: PASS.
- Formatting, lint, mypy и documentation checks: PASS.
- Generated artifacts: отсутствуют.
- Hardware verification: не выполнялась.
- Hardware status: `NOT_TESTED`.

## Architectural compliance

Проверка scope и production diff не выявила изменений в:

- architecture;
- ISA;
- microarchitecture;
- control-word specification;
- memory model;
- active ADR.

Новые public APIs ограничены утверждёнными component models и stateless services. CPU object, simulator, instruction semantics, control-word execution и clock orchestration отсутствуют. Architectural drift не обнаружен.

## Performance

```text
time ./scripts/verify: real 3.979s
pytest: 589 passed in 2.99s
```

Runtime остаётся практичным для полной regression. Timing не закрепляется жёстким assertion.

## Remaining work

Следующий milestone посвящён объединению проверенных components в software CPU layers и соответствующим последующим проверкам. Новые primitive models Milestone 1 для этого не требуются.

Hardware status остаётся `NOT_TESTED`; hardware integration и physical verification не выполнялись.

## Result

Milestone 1 completed successfully.
