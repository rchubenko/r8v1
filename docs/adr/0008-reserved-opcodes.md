# ADR-0008: Reserve Opcodes 0xB Through 0xE

## Status

Accepted

## Контекст

Logical operations, CALL/RET, stack support и extension prefixes могут понадобиться позже, но их hardware и semantic requirements не входят в v1.

## Решение

Не назначать opcodes `0xB`, `0xC`, `0xD` и `0xE` в v1.

Execution этих opcodes вызывает illegal-opcode halt.

3-bit ALU mode field остаётся доступным для future logical operations без изменения control-word width.

## Последствия

Положительные:

- v1 остаётся minimal;
- future ISA design не ограничен premature assignments;
- сохраняется hardware expansion space.

Отрицательные:

- в v1 нет AND/OR/XOR и stack instructions;
- некоторым algorithms нужны memory-based workarounds или deferment.
