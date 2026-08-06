# Микроархитектура R8 v1

## Статус

**Статус:** Утверждённая база

Одна microarchitectural definition используется в программном simulator, Raspberry Pi-driven hybrid hardware и autonomous EEPROM CU; generated microcode общий для всех трёх сред.

## 1. Компоненты и правила шины

Система содержит 8-bit DATA BUS, 12-bit address source MUX, MAR, unified asynchronous SRAM, A, B, ADD/SUB ALU, FLAGS, 12-bit PC, IRH/IRL, 4-bit MICROSTEP, two EEPROMs, branch logic и подсистему clock/reset.

Источники DATA BUS: A, ALU result, IRH, IRL, SRAM. Получатели: A, B, IRH, IRL, SRAM write input. B не управляет DATA BUS. Ровно zero или one source может управлять шиной; no source = `HIGH_Z`/`None`, multiple sources = contention fault.

```text
Any DATA BUS consumer requires exactly one DATA BUS producer.
```

Consumers: `E_A`, `E_B`, `E_IRH`, `E_IRL`, `RAM_WE`. `E_MAR` использует отдельный 12-bit address path и не является consumer. `OE_NONE` допустим с `E_NONE`, `E_MAR`, PC operations, `STEP_END`, HALT; consumer с `OE_NONE` — validation error. Producer без consumer допустим для bring-up/debugging.

Address MUX выбирает PC или IR operand и latches значение в MAR; MAR постоянно управляет SRAM address. IR operand имеет direct path к PC parallel-load inputs.

## 2. Тактируемая модель состояния

Все изменения состояния происходят на общем rising edge, если RESET не active:

```text
decode opcode + microstep
-> control word -> decode sources/destinations
-> combinational paths stabilize -> rising edge
-> latch state -> advance или return T0
```

MICROSTEP reset to T0, increment на accepted CPU clock, return T0 при `STEP_END`, hold при HALT. RESET имеет priority над HALT и STEP_END, clears `HALT_STATE`, returns T0 и marks all FLAGS defined в software models.

Microcode address: `microcode_address[7:4] = IRH[7:4]`, `microcode_address[3:0] = MICROSTEP`; всего 256 addresses. Two 8-bit EEPROM outputs form 16-bit control word.

## 3. Fetch

T0: `ADDR_SEL=PC`, `E_SEL=MAR`, rising edge `MAR <- PC`.

T1: `OE_SEL=SRAM`, `E_SEL=IRH`, `PC_OP=INC`; `IRH <- SRAM[MAR]`, `PC <- PC + 1`.

T2: `ADDR_SEL=PC`, `E_SEL=MAR`, `MAR <- PC`.

T3: `OE_SEL=SRAM`, `E_SEL=IRL`, `PC_OP=INC`; `IRL <- SRAM[MAR]`, `PC <- PC + 1`.

После T3 IRH/IRL содержат instruction, PC указывает на следующий instruction byte, execution starts T4. PC modulo 4096, поэтому fetch через `0xFFF -> 0x000` допустим и после boundary fetch PC `0x001`.

## 4. Микропоследовательности instructions

NOP: T4 `STEP_END=1`.

LDI: T4 `OE_SEL=IRL`, `E_SEL=A`, `STEP_END=1`; A и связанные FLAGS latch, Z/S loaded, C/O unspecified.

LDA: T4 IR operand в MAR; T5 `OE_SEL=SRAM`, `E_SEL=A`, `STEP_END=1`.

STA: T4 IR operand в MAR; T5 `OE_SEL=A`, `RAM_WE=1`, `STEP_END=1`.

ADD/SUB: T4 IR operand в MAR; T5 `OE_SEL=SRAM`, `E_SEL=B`; T6 `ALU_MODE=ADD` или `SUB`, `OE_SEL=ALU`, `E_SEL=A`, `STEP_END=1`.

JMP: T4 `PC_OP=LOAD`, `STEP_END=1`; `PC <- IR operand`.

JC/JZ/JN/JV: T4 `PC_OP=CONDITIONAL_LOAD`, `STEP_END=1`; branch logic выбирает flag, при false condition сохраняется post-fetch PC.

HLT: T4 canonical neutral HALT word; на edge `HALT_STATE <- 1`, затем counter и architectural state hold до RESET. Reserved opcode на T4 также устанавливает HALT.

## 5. FLAGS, reset и validation

`FLAGS_LOAD_INTERNAL = decoded E_A`. При `E_SEL=A` A и FLAGS latch вместе; иначе FLAGS сохраняются. ADD/SUB define all flags, LDI/LDA только Z/S, остальные operations preserve FLAGS. Software models ведут `flags_defined_mask`, strict mode diagnoses undefined conditional flag, hardware-like mode может branch по concrete value.

RESET asynchronous assertion, synchronized deassertion, execution resumes T0 с PC `0x000`. HALT blocks microstep progression и normal updates, но не reset и не memory ownership.

Simulator/driver должны detect multiple drivers, invalid codes, `RAM_WE` без source, simultaneous ownership, undefined PC operand, execution beyond T15, reserved opcode без halt, consumer без producer и HALT с write actions.

## Связанные решения и документы

- [Архитектура R8 v1](architecture.md) задаёт registers, buses, clock и reset boundaries.
- [ISA R8 v1](isa.md) является источником instruction semantics.
- [Control Word](control-word.md) определяет encoding управляющих полей.
- [ADR-0003](adr/0003-eeprom-control-unit.md), [ADR-0004](adr/0004-separate-address-path.md) и [ADR-0009](adr/0009-clock-transition.md) фиксируют связанные hardware decisions.
