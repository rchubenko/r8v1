# ADR-0003: Микрокодовый блок управления на EEPROM

## Статус

Принято

## Контекст

Final CPU должен работать без формирования Raspberry Pi control signals. Жёстко заданный combinational CU было бы трудно изменять и документировать.

## Решение

Использовать две 8-bit EEPROM для формирования 16-bit control word.

Microcode address:

```text
opcode[3:0] + microstep[3:0]
```

Conditional flags вычисляются отдельной branch logic и не входят в EEPROM address.

## Последствия

Положительные:

- microcode генерируется, проверяется и доступен для review;
- до 16 microsteps на opcode;
- нет дублирования по flag combinations;
- Pi-driven hybrid control использует идентичные control words.

Отрицательные:

- требуется workflow программирования EEPROM;
- требуются microstep counter и decode logic;
- EEPROM access timing входит в clock budget.
