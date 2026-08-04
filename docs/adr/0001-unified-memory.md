# ADR-0001: Unified 4 KB Memory

## Status

Accepted

## Контекст

R8 нужны code и data storage при понятных CPU, assembler, loader и debugging model. Ранее рассматривались раздельные program и data memories.

## Решение

Использовать одно byte-addressed 4 KB SRAM address space для code и data.

- Address range: `0x000..0xFFF`.
- Instructions занимают два bytes.
- PC считает bytes.
- Code начинается в `0x000`.
- Assembler размещает data сразу после code.

## Последствия

Положительные:

- единая address model;
- один loader target;
- более простая absolute addressing;
- более простые debugger и assembler;
- поддержка будущего self-modifying или monitor-style software.

Отрицательные:

- fetch требует два SRAM reads;
- program bytes можно перезаписать;
- data может исполняться как code;
- code/data layout должен обрабатываться assembler.
