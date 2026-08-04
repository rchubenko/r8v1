# ISA R8 v1

## Статус

**Статус:** Approved baseline
**Instruction width:** 16 bit
**Data width:** 8 bit
**Address width:** 12 bit

## 1. Encoding

```text
bits 15..12: opcode
bits 11..0 : operand
byte 0 = opcode[3:0] : operand[11:8]
byte 1 = operand[7:0]
```

PC byte-addressed и normal fetch increments PC twice. PC arithmetic modulo 4096: `0xFFF + 1 = 0x000`. Alignment не требуется: byte 0 может быть в `0xFFF`, byte 1 — в `0x000`, после fetch PC равен `0x001`.

## 2. Opcode table

| Opcode | Mnemonic | Operand | Описание |
|---:|---|---|---|
| `0x0` | NOP | ignored | No operation |
| `0x1` | LDI | 8-bit immediate | Load immediate into A |
| `0x2` | LDA | 12-bit address | Load byte from memory into A |
| `0x3` | ADD | 12-bit address | Add memory byte to A |
| `0x4` | SUB | 12-bit address | Subtract memory byte from A |
| `0x5` | STA | 12-bit address | Store A into memory |
| `0x6` | JMP | 12-bit address | Unconditional jump |
| `0x7` | JC | 12-bit address | Jump if C = 1 |
| `0x8` | JZ | 12-bit address | Jump if Z = 1 |
| `0x9` | JN | 12-bit address | Jump if S = 1 |
| `0xA` | JV | 12-bit address | Jump if O = 1 |
| `0xB` | RESERVED | — | Illegal in v1 |
| `0xC` | RESERVED | — | Illegal in v1 |
| `0xD` | RESERVED | — | Illegal in v1 |
| `0xE` | RESERVED | — | Illegal in v1 |
| `0xF` | HLT | ignored | Halt CPU |

`0xB`–`0xE` reserved для future versions. Assignments в v1 нет.

## 3. Registers и flags

`A` — 8-bit accumulator, `B` — internal 8-bit ALU operand, `PC` — 12-bit program counter, `M[x]` — byte memory, `operand` — bits `11..0`, `imm8` — bits `7..0`.

Flags: Z (zero), C (carry/no-borrow), S (sign), O (signed overflow).

```text
Z = 1 if result == 0x00, otherwise 0
S = result[7]
C after ADD = carry out of bit 7
C after SUB = 1 when no borrow, 0 when borrow
```

Для ADD: `O = (~(A7 XOR B7)) AND (A7 XOR R7)`. Для SUB: `O = (A7 XOR B7) AND (A7 XOR R7)`, где `R7` — result bit 7.

## 4. FLAGS update

FLAGS update whenever Register A is written; independent architectural or microcode-level `FLAGS_LOAD` command отсутствует:

```text
FLAGS_LOAD_INTERNAL = A_LOAD
```

ADD/SUB определяют Z, C, S, O. LDI/LDA определяют только Z/S; C/O содержат concrete hardware-like values, но architectural unspecified. JC/JV сразу после LDI/LDA использовать нельзя.

Software CPU models дополнительно ведут `flags_defined_mask`:

- RESET: Z, C, S, O defined;
- ADD/SUB: Z, C, S, O defined;
- LDI/LDA: только Z и S defined;
- instructions, сохраняющие FLAGS, сохраняют mask.

Parity сравнивает mask и values только для defined flags. Strict simulation диагностирует conditional jump по undefined flag. Hardware-like diagnostic mode может продолжить с concrete physical value.

## 5. Instruction semantics

### NOP

`A`, `B`, PC-after-fetch, FLAGS и memory unchanged; operand ignored; flags preserved.

### LDI `imm8`

```text
A <- imm8
Z <- (A == 0)
S <- A[7]
C, O <- unspecified
```

Operand должен быть `0x000..0x0FF`; assembler отвергает больший value.

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

Если соответствующий flag (C, Z, S, O) равен 1, `PC <- address`; иначе PC сохраняет post-fetch value. Flags preserved.

### HLT

`HALT <- 1`. CPU state остаётся stable до reset, operand ignored, flags preserved.

## 6. Reserved opcodes

Execution `0xB`, `0xC`, `0xD` или `0xE` вызывает illegal-opcode halt:

```text
HALT <- 1
```

Debugger может определить `ILLEGAL_OPCODE` по IRH; dedicated architectural halt-reason register не требуется.

## 7. Flag update table

| Instruction | Z | C | S | O |
|---|---|---|---|---|
| NOP | preserve | preserve | preserve | preserve |
| LDI | result | unspecified | result[7] | unspecified |
| LDA | result | unspecified | result[7] | unspecified |
| ADD | result | carry | result[7] | overflow |
| SUB | result | no-borrow | result[7] | overflow |
| STA/JMP/JC/JZ/JN/JV/HLT | preserve | preserve | preserve | preserve |

## 8. Addressing и future compatibility

Memory operands — absolute 12-bit byte addresses. Indirect, relative и register-addressed ADD/SUB отсутствуют. Instructions и data share address space; любой 12-bit byte address может быть jump target. Opcodes `0xB..0xE` остаются unused; future ISA changes требуют новой architecture version и ADR.
