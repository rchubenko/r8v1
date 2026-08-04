# ADR-0008: Резервирование opcode `0xB`–`0xE`

## Статус

Принято

## Контекст

Logical operations, CALL/RET, stack support и extension prefixes могут понадобиться позже, но их аппаратные и semantic requirements не входят в v1.

## Решение

Не назначать opcode `0xB`, `0xC`, `0xD` и `0xE` в v1.

Выполнение этих opcode вызывает illegal-opcode halt.

3-bit ALU mode field остаётся доступным для future logical operations без изменения control-word width.

## Последствия

Положительные:

- v1 остаётся минимальным;
- будущая ISA design не ограничена преждевременными assignments;
- сохраняется пространство для расширения hardware.

Отрицательные:

- в v1 нет AND/OR/XOR и stack instructions;
- некоторым algorithms нужны memory-based workarounds или deferment.
