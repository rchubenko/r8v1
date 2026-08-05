# Task M1-012: Address source selector

## Summary

Добавлена минимальная stateless/combinational модель выбора источника отдельного 12-битного address path: PC или уже извлечённый IR operand.

## Sources

Решение основано на `AGENTS.md`, `README.md`, `docs/plans/milestone-1-component-models.md`, `docs/reports/milestone-1/README.md`, reports Tasks 5–7 и 11, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/memory.md`, `docs/adr/README.md` и всеми активными ADR, особенно ADR-0004. Реализация сверена с `cpu/program_counter.py`, `cpu/instruction_register.py`, `cpu/mar.py`, `cpu/values.py`, `cpu/__init__.py`, `cpu/alu.py`, существующими enum и stateless API conventions, tests, `docs/testing/software.md`, `pyproject.toml` и `scripts/verify`.

## Design decision

Выбран enum `AddressSource` только со значениями `PC = "pc"` и `IR_OPERAND = "ir_operand"`. Symbolic values не связаны с numeric `ADDR_SEL` encoding.

Выбрана функция без состояния `select_address(source, *, pc, ir_operand) -> int`. Она принимает уже подготовленные integer values, а не `ProgramCounter`, `InstructionRegister` или `MemoryAddressRegister` objects. Это сохраняет независимость component boundaries; object-level wiring откладывается до Task 21.

Сначала проверяется, что `source` является `AddressSource`, затем оба candidate values проходят `validate_address`, и только после этого возвращается выбранное значение. Это означает, что invalid unselected candidate не скрывается выбором другого источника.

MAR latching отсутствует, потому что selector выдаёт combinational 12-bit value, а MAR является отдельным stateful component. Numeric `ADDR_SEL` decoding отсутствует, поскольку он относится к control-word layer.

## Source behavior

```text
PC source -> PC value
IR_OPERAND source -> IR operand value
```

Selector возвращает ровно один из уже валидированных inputs. Он не объединяет values, не изменяет их, не increment-ит PC и не извлекает operand из IRH/IRL.

## Validation

Оба candidate values должны находиться в диапазоне `0x000..0xFFF`. `bool`, отрицательные значения, значения от `0x1000` и неподходящие типы отклоняются через `InvalidComponentValue`. Masking и modulo отсутствуют.

Raw integers, strings и другие значения в качестве source отклоняются через `TypeError`; implicit decoding не выполняется.

## Changes

- Добавлены `cpu.address.AddressSource` и `select_address`.
- Добавлены public exports через `cpu/__init__.py`.
- Добавлены unit tests enum, выбора PC/IR operand, validation order, invalid inputs, no mixing и stateless behavior.
- Обновлён milestone index; hash commit оставлен `—`.

## Public API

```python
from cpu import AddressSource, select_address

address = select_address(
    AddressSource.IR_OPERAND,
    pc=0xABC,
    ir_operand=0x123,
)
assert address == 0x123
```

## Tests

Проверены состав enum и symbolic values, PC boundaries, IR operand boundaries, точное возвращение одного candidate без смешения, invalid source, invalid PC, invalid IR operand, invalid unselected candidate, validation order и stateless behavior. Objects `ProgramCounter`, `InstructionRegister` и `MemoryAddressRegister` в selector unit tests не используются.

## Verification

Targeted tests, форматирование, lint и mypy проходят. Полная проверка `./scripts/verify` выполняется перед commit и включает предыдущие component tests и новые address selector tests.

Hardware verification не выполнялась; hardware status — `NOT_TESTED`.

## Architectural compliance

Architecture, ISA, microarchitecture, control word, memory model и активные ADR не изменены. `ADDR_SEL` bit decoding, MAR latching, PC/IR mutation, DATA BUS, SRAM, clock semantics, fetch, instruction execution, emulator, simulator и hardware work отсутствуют.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
model: add address source selector
```

Hash текущего commit будет указан в Git metadata; push и tag не выполняются.

## Follow-up

Следующая задача — Task 13: Flags value и defined mask. MAR latching и object-level address-path integration остаются вне Task 12.
