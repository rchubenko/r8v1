# Task M1-021: Component-level integration tests

## Summary

Добавлен небольшой набор детерминированных integration tests, связывающих outputs и inputs уже реализованных component boundaries. Production code, component-state container и public API не изменялись.

## Sources

Решение основано на `AGENTS.md`, `README.md`, `docs/plans/milestone-1-component-models.md`, `docs/reports/milestone-1/README.md`, `docs/reports/milestone-1/020-component-state-container.md`, reports Tasks 3–19, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/memory.md`, `docs/adr/README.md` и всеми активными ADR, особенно ADR-0001, ADR-0004, ADR-0005, ADR-0006 и ADR-0010. Tests сверены со всеми modules в `cpu/`, существующими component unit tests, `docs/testing/software.md`, pytest conventions, `pyproject.toml` и `scripts/verify`.

## Test-layer boundary

Tests передают уже готовый результат одного component boundary в stateless selector, resolver или policy и проверяют результат следующего boundary.

Production orchestration не добавлена. Container из Task 20 не требуется: каждый test создаёт собственные independent component instances. Tests не являются simulator tests и не моделируют instruction execution, complete CPU transition, clock edge или control word.

## IR operand to address selector

Настоящий `InstructionRegister` независимо загружает IRH и IRL, после чего `ir.operand` передаётся в `select_address(AddressSource.IR_OPERAND, ...)`.

Проверены cases:

- `IRH=0x00`, `IRL=0x00` -> `0x000`;
- `IRH=0x0F`, `IRL=0xFF` -> `0xFFF`;
- `IRH=0xAF`, `IRL=0xFF` -> `0xFFF`;
- `IRH=0xF1`, `IRL=0x23` -> `0x123`.

Отдельно подтверждено, что opcode `0xF` не входит в operand, selector не изменяет IR, не загружает MAR и не выполняет fetch.

## PC value to address selector

Настоящий `ProgramCounter` устанавливается через `load()`, его `value` передаётся в `select_address(AddressSource.PC, ...)`.

Проверены boundaries `0x000`, `0x001`, `0x7FF`, `0x800`, `0xFFF`. Дополнительно проверено `0xFFF -> increment() -> 0x000` и передача wrapped value в selector.

Selector не изменяет PC или IR operand; MAR и numeric `ADDR_SEL` decoding отсутствуют.

## ALU result to FLAGS policy

Unified `evaluate()` передаёт `ALUResult` в `latch_flags_for_alu_write()`.

Проверены representative cases:

- ADD: `0x00 + 0x00`, `0x7F + 0x01`, `0xFF + 0x01`, `0x80 + 0x80`;
- SUB: `0x00 - 0x01`, `0x80 - 0x01`, `0x7F - 0xFF`, `0x01 - 0x01`.

Для каждого case проверены result byte, concrete Z/C/S/O, соответствие snapshot values, all-defined mask и сохранение ALU result. Арифметика в test не дублируется вторым production path.

## SRAM byte to DATA BUS resolver

Настоящий `SRAM` получает writes и возвращает byte через `read()`, после чего значение передаётся как единственный producer в `resolve_data_bus([memory_value])`.

Проверены representative pairs:

- `0x000 -> 0x00`;
- `0x001 -> 0x01`;
- `0x7FF -> 0x7F`;
- `0x800 -> 0x80`;
- `0xFFF -> 0xFF`.

Отдельно подтверждено:

- `resolve_data_bus([0x00]) == 0x00` — нулевой byte является driven value;
- `resolve_data_bus([]) is None` — отсутствие producer является `HIGH_Z`;
- SRAM не знает DATA BUS, resolver не знает SRAM;
- consumers, `OE_SRAM` и memory cycle не моделируются.

## Reset boundaries

Проверены только local reset operations без общего reset coordinator:

- независимые A/B как `FixedWidthRegister(width=8, reset_value=0x00)`;
- `ProgramCounter` -> `0x000`;
- `MemoryAddressRegister` -> `0x000`;
- `InstructionRegister` -> zeroed IRH/IRL и views;
- `MicrostepCounter` -> T0;
- `HaltLatch` -> `False`;
- `FlagsSnapshot.reset()` -> values `0000` и all-defined mask.

Отдельно проверено, что записанный byte SRAM сохраняется после local reset остальных stateful components. SRAM не участвует в CPU reset и не получает reset/clear call.

## Changes

- Добавлен `tests/test_cpu_component_integration.py`.
- Production code не изменялся.
- Создан этот report.
- Обновлён milestone index; Task 21 отмечена как `COMPLETED`, hash commit оставлен `—`.

## Tests

Добавлено 31 test case из 15 test functions, включая parametrized IR operand, PC boundary, ALU/FLAGS и SRAM/DATA BUS cases.

Все tests создают собственные stateful instances, не используют module-level mutable state, общий container или полный CPU fixture и не зависят от порядка запуска.

## Performance

```text
time ./scripts/verify: real 3.852s
pytest: 589 passed in 2.89s
```

Runtime остаётся практичным для полного regression run. Timing не закрепляется жёстким assertion.

## Verification

Targeted integration tests: `31 passed`. Полная проверка `./scripts/verify`, `git diff --check`, formatting, lint, mypy, полный pytest и documentation checks прошли. Hardware verification не выполняется; hardware status — `NOT_TESTED`.

## Architectural compliance

Не добавлены fetch T0–T3, instruction/opcode execution, control-word decode/execution, `OE_SEL`, `E_SEL`, numeric `ADDR_SEL`, `PC_OP`, `RAM_WE`, `STEP_END`, complete rising edge, simultaneous latching, microcode, EEPROM lookup, branch logic, conditional jumps, HALT blocking, reset priority orchestration, emulator, simulator или hardware work.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
test: add component integration coverage
```

Push и tag не выполняются.

## Follow-up

Следующая задача — Task 22: documentation and milestone regression. Component integration остаётся ограниченной independent boundaries; complete CPU execution и simulator layers не начинаются.
