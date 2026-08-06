# ADR-0004: Отдельный 12-разрядный адресный тракт

## Статус

Принято

## Контекст

В R8 есть 8-bit DATA BUS, но PC, MAR и instruction operands имеют ширину 12 bits. Передача addresses через DATA BUS потребовала бы нескольких cycles и split registers.

## Решение

Использовать:

- один общий 8-bit DATA BUS;
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

## Связанные решения и документы

- [Архитектура R8 v1](../architecture.md) задаёт отдельный address path.
- [Микроархитектура](../microarchitecture.md) описывает его использование через MAR.
- [Архитектура memory](../memory.md) показывает путь address source к SRAM.
