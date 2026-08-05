# Task M1-007: Instruction Register

## Summary

Добавлена самостоятельная модель Instruction Register с независимыми 8-bit storage elements `IRH` и `IRL`, read-only views `opcode` и `operand`, а также reset.

## Sources

Решение основано на `AGENTS.md`, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/memory.md`, `docs/adr/README.md` и активных ADR, а также на `cpu/register.py`, `cpu/values.py`, `cpu/program_counter.py`, `cpu/mar.py`, `cpu/__init__.py` и reports Tasks 3–6.

## Design decision

Выбран composition: `InstructionRegister` содержит два независимых экземпляра `FixedWidthRegister` ширины 8 с reset value `0x00`. Composition отражает архитектурное требование независимой загрузки `IRH` и `IRL` и не скрывает их как один mutable 16-bit register.

Используются properties `high` и `low`, а также методы `load_high(value)` и `load_low(value)`. Внешнему коду не выдаются внутренние storage objects, поэтому их validation нельзя обойти.

Views вычисляются динамически по утверждённым формулам:

```text
opcode = (IRH >> 4) & 0xF
operand = ((IRH & 0xF) << 8) | IRL
```

Reserved opcode `0xB..0xE` не интерпретируется внутри IR: он возвращается как обычное 4-bit значение. IR не вызывает HALT, не проверяет mnemonic и не выполняет instruction semantics. Fetch отсутствует.

## Changes

- Добавлен `cpu.instruction_register.InstructionRegister`.
- Добавлен минимальный public export через `cpu/__init__.py`.
- Добавлены unit tests Instruction Register.
- Обновлён milestone index; hash текущего commit оставлен `—` до следующего documentation update.

## Public API

```python
ir = InstructionRegister()
ir.load_high(0x15)
ir.load_low(0xAA)

high = ir.high
low = ir.low
opcode = ir.opcode
operand = ir.operand

ir.reset()
```

## Tests

Проверены:

- initial reset bytes и views;
- отсутствие configurable constructor parameters;
- независимые valid loads `IRH` и `IRL`;
- invalid `-1`, `0x100`, `True`, `False`, неподходящий тип для обоих bytes;
- `InvalidComponentValue`, error context и сохранение обоих bytes после failed load;
- opcode boundaries и reserved opcode `0xB..0xE` без HALT/exception;
- operand boundaries и исключение opcode bits из operand;
- динамическое обновление views;
- reset и instance isolation.

## Verification

Выполнены `./scripts/verify` и `git diff --check`. Полный набор tests включает предыдущие tests Tasks 2–6 и новые Instruction Register tests.

## Architectural compliance

Architecture, ISA, microarchitecture, control word, memory model и активные ADR не изменены. Instruction Register не выполняет instruction decoding, reserved opcode HALT, fetch orchestration, PC/MAR/SRAM integration, clock semantics или instruction execution. Emulator, simulator и hardware work отсутствуют. Hardware status — `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
model: add instruction register
```

Hash текущего commit намеренно не записывается до следующего documentation update.

## Follow-up

Следующая задача — Task 8: ALU ADD. Fetch и control-word behavior остаются вне текущего commit.
