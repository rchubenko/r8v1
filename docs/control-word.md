# Control Word R8 v1

## Статус

**Статус:** Утверждённая база
**Width:** 16 bit
**Storage:** two 8-bit EEPROMs

## 1. Раскладка битов

| Bits | Field | Width |
|---|---|---:|
| `15` | HALT | 1 |
| `14` | STEP_END | 1 |
| `13` | RESERVED | 1 |
| `12` | RAM_WE | 1 |
| `11..10` | PC_OP | 2 |
| `9` | ADDR_SEL | 1 |
| `8..6` | ALU_MODE | 3 |
| `5..3` | E_SEL | 3 |
| `2..0` | OE_SEL | 3 |

```text
control_word =
    (HALT << 15) | (STEP_END << 14) | (RESERVED << 13) |
    (RAM_WE << 12) | (PC_OP << 10) | (ADDR_SEL << 9) |
    (ALU_MODE << 6) | (E_SEL << 3) | OE_SEL
```

`EEPROM LOW -> control_word[7:0]`, `EEPROM HIGH -> control_word[15:8]`. Microcode address: `A[7:4] = opcode`, `A[3:0] = microstep`.

## 2. Кодировки

`OE_SEL` выбирает единственный источник DATA BUS: `000 OE_NONE`, `001 OE_A`, `010 OE_ALU`, `011 OE_IRH`, `100 OE_IRL`, `101 OE_SRAM`; `110` и `111` reserved.

`E_SEL` выбирает действие: `000 E_NONE`, `001 E_A`, `010 E_B`, `011 E_IRH`, `100 E_IRL`, `101 E_MAR`; `110` и `111` reserved. `E_MAR` использует отдельный 12-bit address path и не потребляет DATA BUS.

`ALU_MODE`: `000 ALU_ADD`, `001 ALU_SUB`; `010..111` reserved. `ADDR_SEL=0` выбирает PC, `ADDR_SEL=1` — IR operand. Если `E_SEL != E_MAR`, ADDR_SEL не имеет architectural effect.

`PC_OP`: `00 PC_HOLD`, `01 PC_INC`, `10 PC_LOAD`, `11 PC_COND_LOAD`. Conditional load выбирает C/Z/S/O по opcode через external branch logic.

`RAM_WE=1` означает запись byte с DATA BUS в `SRAM[MAR]`; CPU должен владеть memory, DATA BUS должен иметь valid source, MAR — valid address. Physical `/WE`, `/OE`, `/CE` формируются memory-control и ownership arbitration.

## 3. Связь с FLAGS

Independent flags-load command отсутствует. Decoded `E_A` — событие load-enable для FLAGS:

```text
FLAGS_LOAD_INTERNAL = E_A
```

При latch A на rising edge одновременно latch FLAGS. При другом `E_SEL` FLAGS preserve. Z берётся из byte, записываемого в A, S — bit 7, C/O — outputs ALU. Поэтому ADD/SUB определяют все flags, LDI/LDA — Z/S, а C/O unspecified. Bit 13 должен быть zero.

## 4. STEP_END и HALT

`STEP_END` исполняет текущую microinstruction и возвращает microstep counter в T0 вместо increment. Его можно комбинировать с действиями над register, PC или memory.

HALT использует canonical neutral control word:

```text
HALT = 1
STEP_END = 0
RESERVED = 0
RAM_WE = 0
PC_OP = PC_HOLD
ADDR_SEL = 0
ALU_MODE = ALU_ADD
E_SEL = E_NONE
OE_SEL = OE_NONE
```

На rising edge `HALT_STATE` становится 1. Затем microstep counter и architectural CPU state удерживаются до RESET. RESET имеет priority, очищает HALT и возвращает counter в T0. Reserved opcodes используют тот же neutral HALT word на T4.

## 5. Правила валидации

Generator должен отвергать: reserved OE/E/ALU codes; `RAM_WE=1` с `OE_NONE`; bit 13 = 1; `OE_SRAM` вместе с RAM_WE; E_MAR с undefined address source; invalid PC operations; sequences, не завершающиеся к T15; non-canonical HALT или HALT с write action; multiple DATA BUS sources; DATA BUS consumer без ровно одного producer; conditional jump по undefined flag в strict mode.

`OE_NONE` означает no producer (`HIGH_Z`/`None`). Consumers: `E_A`, `E_B`, `E_IRH`, `E_IRL`, `RAM_WE`; `E_MAR` не consumer. One producer без consumer разрешён для bring-up/debugging. Control word использует logical active-high semantics; physical inversion остаётся в decoder/interface circuitry.

## Связанные решения и документы

- [Микроархитектура](microarchitecture.md) использует эти поля в microstep sequences.
- [Архитектура R8 v1](architecture.md) задаёт границы registers, buses и control unit.
- [ADR-0003](adr/0003-eeprom-control-unit.md) фиксирует EEPROM-based control unit.
- [ADR-0005](adr/0005-flags-update-on-a-write.md) фиксирует внутреннюю связь A-load и FLAGS.
