# ADR-0003: EEPROM Microcoded Control Unit

## Status

Accepted

## Контекст

Final CPU должен работать без формирования Raspberry Pi control signals. Hardwired combinational CU было бы трудно изменять и документировать.

## Решение

Использовать две 8-bit EEPROM для формирования 16-bit control word.

Microcode address:

```text
opcode[3:0] + microstep[3:0]
```

Conditional flags вычисляются отдельной branch logic и не входят в EEPROM address.

## Последствия

Положительные:

- microcode generated, reviewable и testable;
- до 16 microsteps на opcode;
- нет duplication по flag combinations;
- Pi-driven hybrid control использует идентичные control words.

Отрицательные:

- требуется EEPROM programming workflow;
- требуются microstep counter и decode logic;
- EEPROM access timing входит в clock budget.
