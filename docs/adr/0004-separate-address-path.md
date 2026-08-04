# ADR-0004: Separate 12-Bit Address Path

## Status

Accepted

## Контекст

В R8 есть 8-bit DATA BUS, но PC, MAR и instruction operands имеют 12 bits. Передача addresses через DATA BUS потребовала бы нескольких cycles и split registers.

## Решение

Использовать:

- один shared 8-bit DATA BUS;
- отдельный 12-bit address source path;
- PC/IR-operand selector, подающий значение в MAR;
- direct IR-operand path к PC load inputs.

## Последствия

Положительные:

- PC в MAR за один microstep;
- operand в MAR за один microstep;
- более простые fetch и jumps;
- нет MAR high/low transfer protocol.

Отрицательные:

- больше wiring и selection hardware;
- address-path behavior нужно тестировать отдельно от DATA BUS behavior.
