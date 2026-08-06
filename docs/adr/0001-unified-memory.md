# ADR-0001: Единая память объёмом 4 КБ

## Статус

Принято

## Контекст

R8 нужны понятные модели хранения code и data, CPU, assembler, loader и debugging. Ранее рассматривались раздельные program и data memories.

## Решение

Использовать одно адресуемое по байтам 4 KB SRAM address space для code и data.

- Диапазон адресов: `0x000..0xFFF`.
- Instructions занимают два bytes.
- PC считает bytes.
- Code начинается в `0x000`.
- Assembler размещает data сразу после code.

## Последствия

Положительные:

- единая address model;
- единый loader target;
- более простая absolute addressing;
- более простые debugger и assembler;
- поддержка будущего self-modifying или monitor-style software.

Отрицательные:

- fetch требует два SRAM reads;
- program bytes можно перезаписать;
- data может исполняться как code;
- code/data layout должен обрабатываться assembler.

## Связанные решения и документы

- [Архитектура memory](../memory.md) описывает unified SRAM contract.
- [Архитектура R8 v1](../architecture.md) задаёт общую memory model.
- [ADR-0007](0007-memory-ownership.md) определяет владение общей SRAM.
