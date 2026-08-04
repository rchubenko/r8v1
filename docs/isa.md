# ISA R8 v1

## Статус

**Статус:** Утверждённая база
**Instruction width:** 16 bit
**Data width:** 8 bit
**Address width:** 12 bit

## 1. Кодирование

```text
bits 15..12: opcode
bits 11..0 : operand
byte 0 = opcode[3:0] : operand[11:8]
byte 1 = operand[7:0]
```

PC byte-addressed и при обычном fetch increments PC twice. Арифметика PC выполняется по модулю 4096: `0xFFF + 1 = 0x000`. Выравнивание не требуется: byte 0 может быть в `0xFFF`, byte 1 — в `0x000`, после fetch PC равен `0x001`.

## 2. Таблица opcode

| Opcode | Mnemonic | Operand | Описание |
|---:|---|---|---|
| `0x0` | NOP | ignored | Нет операции |
| `0x1` | LDI | 8-bit immediate | Загрузить immediate в A |
| `0x2` | LDA | 12-bit address | Загрузить byte из memory в A |
| `0x3` | ADD | 12-bit address | Прибавить byte memory к A |
| `0x4` | SUB | 12-bit address | Вычесть byte memory из A |
| `0x5` | STA | 12-bit address | Записать A в memory |
| `0x6` | JMP | 12-bit address | Безусловный переход |
| `0x7` | JC | 12-bit address | Переход при C = 1 |
| `0x8` | JZ | 12-bit address | Переход при Z = 1 |
| `0x9` | JN | 12-bit address | Переход при S = 1 |
| `0xA` | JV | 12-bit address | Переход при O = 1 |
| `0xB` | RESERVED | — | Недопустимо в v1 |
| `0xC` | RESERVED | — | Недопустимо в v1 |
| `0xD` | RESERVED | — | Недопустимо в v1 |
| `0xE` | RESERVED | — | Недопустимо в v1 |
| `0xF` | HLT | ignored | Остановить CPU |

`0xB`–`0xE` reserved для будущих versions. Назначений в v1 нет.

## 3. Регистры и flags

`A` — 8-bit accumulator, `B` — internal 8-bit ALU operand, `PC` — 12-bit program counter, `M[x]` — byte memory, `operand` — bits `11..0`, `imm8` — bits `7..0`.

Flags: Z (zero), C (carry/no-borrow), S (sign), O (signed overflow).

```text
Z = 1 if result == 0x00, otherwise 0
S = result[7]
C after ADD = carry out of bit 7
C after SUB = 1 when no borrow, 0 when borrow
```

Для ADD: `O = (~(A7 XOR B7)) AND (A7 XOR R7)`. Для SUB: `O = (A7 XOR B7) AND (A7 XOR R7)`, где `R7` — result bit 7.

## 4. Обновление FLAGS

FLAGS обновляются при каждой записи в Register A; independent architectural or microcode-level `FLAGS_LOAD` command отсутствует:

```text
FLAGS_LOAD_INTERNAL = A_LOAD
```

ADD/SUB определяют Z, C, S, O. LDI/LDA определяют только Z/S; C/O содержат concrete hardware-like values, но architectural unspecified. JC/JV сразу после LDI/LDA использовать нельзя.

Software models дополнительно ведут `flags_defined_mask`:

- RESET: Z, C, S, O defined;
- ADD/SUB: Z, C, S, O defined;
- LDI/LDA: только Z и S defined;
- instructions, сохраняющие FLAGS, сохраняют mask.

Parity сравнивает mask и values только для defined flags. Strict simulation диагностирует conditional jump по undefined flag. Hardware-like diagnostic mode может продолжить с concrete physical value.

## 5. Семантика instructions

### NOP

`A`, `B`, PC-after-fetch, FLAGS и memory не изменяются; operand ignored; flags preserved.

### LDI `imm8`

```text
A <- imm8
Z <- (A == 0)
S <- A[7]
C, O <- unspecified
```

Operand должен быть в диапазоне `0x000..0x0FF`; assembler отвергает большее значение.

### LDA `address`

```text
A <- M[address]
Z <- (A == 0)
S <- A[7]
C, O <- unspecified
```

### ADD `address`

```text
A <- A + M[address] mod 256
Z <- zero(result)
C <- unsigned carry out
S <- result[7]
O <- signed overflow
```

### SUB `address`

```text
A <- A - M[address] mod 256
Z <- zero(result)
C <- no-borrow
S <- result[7]
O <- signed overflow
```

### STA `address`

`M[address] <- A`; flags preserved.

### JMP `address`

`PC <- address`; flags preserved.

### JC, JZ, JN, JV `address`

Если соответствующий flag (C, Z, S, O) равен 1, `PC <- address`; иначе PC сохраняет значение после fetch. Flags preserved.

### HLT

`HALT <- 1`. Состояние CPU остаётся неизменным до reset, operand ignored, flags preserved.

## 6. Зарезервированные opcode

Выполнение `0xB`, `0xC`, `0xD` или `0xE` вызывает illegal-opcode halt:

```text
HALT <- 1
```

Debugger может определить `ILLEGAL_OPCODE` по IRH; dedicated architectural halt-reason register не требуется.

## 7. Таблица обновления flags

| Instruction | Z | C | S | O |
|---|---|---|---|---|
| NOP | preserve | preserve | preserve | preserve |
| LDI | result | unspecified | result[7] | unspecified |
| LDA | result | unspecified | result[7] | unspecified |
| ADD | result | carry | result[7] | overflow |
| SUB | result | no-borrow | result[7] | overflow |
| STA/JMP/JC/JZ/JN/JV/HLT | preserve | preserve | preserve | preserve |

## 8. Адресация и совместимость в будущем

Memory operands — absolute 12-bit byte addresses. Indirect, relative и register-addressed ADD/SUB отсутствуют. Instructions и data используют общее address space; любой 12-bit byte address может быть jump target. Opcodes `0xB..0xE` остаются unused; изменения ISA требуют новой architecture version и ADR.
