# Архитектура R8 v1

## Статус

**Статус:** Утверждённая архитектурная база
**Цель:** R8 v1
**Тип:** 8-bit accumulator-based TTL CPU

Документ задаёт системную архитектуру. ISA, microarchitecture, control word и memory behavior описаны в отдельных документах.

## 1. Цель проекта

R8 v1 — autonomous 8-bit TTL CPU, способный загружать и исполнять programs из memory без участия Raspberry Pi в формировании control signals. Raspberry Pi может оставаться загрузчиком программ, испытательным стендом, отладчиком и монитором состояния.

R8 v1 включает CPU, unified SRAM, assembler, loader и demonstration programs. R8-Lang compiler, Stack Pointer, CALL/RET, PUSH/POP, interrupts, user peripherals, logical ALU operations и CPU monitor/bootloader отложены.

## 2. Архитектурные параметры

| Свойство | Значение |
|---|---|
| Разрядность данных | 8 bit |
| Разрядность адреса | 12 bit |
| Address space | 4096 bytes |
| Разрядность instruction | 16 bit |
| Формат instruction | 4-bit opcode + 12-bit operand |
| Модель памяти | Unified Von Neumann memory |
| Program counter | Byte-addressed |
| Основная DATA BUS | 8 bit |
| Address path | Separate 12-bit path |
| Flags | Z, C, S, O |
| Final CU | EEPROM microcode-based |

## 3. Набор регистров

| Register | Width | Назначение |
|---|---:|---|
| A | 8 | Accumulator и первый ALU input |
| B | 8 | Внутренний второй ALU operand |
| PC | 12 | Address следующего instruction byte |
| IRH | 8 | Opcode в bits 7..4 и operand bits 11..8 в bits 3..0 |
| IRL | 8 | Operand bits 7..0 |
| MAR | 12 | Текущий SRAM address |
| FLAGS | 4 | Z, C, S, O |
| MICROSTEP | 4 | Текущий microstep T0..T15 |

B не управляет DATA BUS, а только подаёт значение в ALU. Architectural output register и Stack Pointer в v1 отсутствуют; будущие output devices должны использовать memory-mapped I/O.

## 4. Тракт данных

Используется одна общая 8-bit DATA BUS для byte transfers и отдельный 12-bit address path для memory addressing.

```text
A ───────────────┐
                 │
B ──> ALU ───────┼──> DATA BUS ──> A / B / IRH / IRL / SRAM write
                 │
IRH / IRL ───────┤
SRAM ────────────┘
```

Одновременно DATA BUS может управляться не более чем одним source. Выбор кодируется через `OE_SEL`.

### Связь с FLAGS

FLAGS обновляются автоматически при записи Register A. Decoded A-load action управляет и A register load-enable, и FLAGS register load-enable:

```text
FLAGS_LOAD_INTERNAL = A_LOAD
```

ADD и SUB определяют все четыре flags. LDI и LDA определяют Z и S, а C и O оставляют concrete hardware-like values, которые architectural unspecified. Independent `FLAGS_LOAD` bit в v1 control word отсутствует.

### Адресный тракт и fetch path

```text
PC ───────────────┐
                  ├──> Address Source MUX ──> MAR ──> SRAM A[11:0]
IR operand ───────┘
```

`operand[11:8] = IRH[3:0]`, `operand[7:0] = IRL[7:0]`. IR operand также имеет direct path к PC load inputs.

```text
PC -> MAR -> SRAM -> DATA BUS -> IRH/IRL
```

PC не проходит через IR как промежуточный address register.

## 5. Модель памяти

Code и data используют unified SRAM address space `0x000..0xFFF`. Programs загружаются с `0x000`, data assembler размещает после code. Hardware не защищает code от writes; overwriting и execution data разрешены.

## 6. Модель instruction

Каждая instruction занимает два bytes:

```text
byte 0: opcode[3:0] + operand[11:8]
byte 1: operand[7:0]
```

PC byte-addressed и обычно increment дважды за fetch. Это 12-bit modulo counter: `0xFFF + 1 = 0x000`. Fetch через boundary определён: byte 0 в `0xFFF`, byte 1 в `0x000`, после fetch PC равен `0x001`. Выравнивание не требуется.

Утверждённая v1 ISA: NOP, LDI, LDA, ADD, SUB, STA, JMP, JC, JZ, JN, JV, HLT. Opcodes `0xB`–`0xE` reserved.

## 7. Блок управления

Развитие проходит через software simulation, hybrid bring-up и autonomous operation. Final CU использует two EEPROMs, формирующие 16-bit control word по opcode и MICROSTEP. Conditional branch decisions выполняет отдельная combinational branch logic; flags не входят в EEPROM address.

## 8. Контракт тактового сигнала

Все sequential CPU elements используют общий rising-edge clock:

```text
control stable -> propagation delay -> rising edge -> state latch -> control release
```

Используется один `CPU_CLK_IN`. Raspberry Pi даёт deterministic single-step pulses во время software-driven и hybrid bring-up. Pi control signals нельзя использовать с free-running autonomous clock. Clock-source switching разрешён только при active reset.

## 9. Контракт RESET

Reset — системный сигнал вне control word. Sources: power-on reset, manual reset button и Raspberry Pi reset output. Assertion asynchronous, deassertion synchronized, priority над HALT и normal execution.

| Component | Value |
|---|---|
| PC | `0x000` |
| IRH, IRL | `0x00` |
| A, B | `0x00` |
| FLAGS | `0000` |
| FLAGS defined mask | Z, C, S, O defined in software models |
| MAR | `0x000` |
| MICROSTEP | `T0` |
| HALT | cleared |

## 10. Стратегия software/hardware

R8 использует software-first co-design. ISA reference emulator выполняет instructions atomically. Microarchitecture simulator должен исполнять те же programs через microsteps, control words, buses, register latching, clock edges и memory cycles, не вызывая atomic ISA implementations.

Software models ведут `flags_defined_mask`. Parity сравнивает mask и только architecturally defined flag values. Strict simulation диагностирует conditional jump с undefined flag; hardware-like diagnostic mode может использовать concrete physical value.

Hardware вводится после complete software CPU: software CPU -> hardware DATA BUS/A/B -> hardware ALU/FLAGS -> hardware PC/IR/MAR/SRAM -> EEPROM CU -> autonomous clock.

## 11. Политика hardware

Primary supply — 5 V. 74HC/74HCT допустимы после level validation. Raspberry Pi GPIO нельзя напрямую подвергать unsafe 5 V signals; нужны level shifters/buffers. IC требуют decoupling, unused inputs — defined levels. Hardware test status можно отметить `PASS` только после physical confirmation.

## 12. Repository и release model

R8 — monorepo. `compiler/` reserved для later versions и не входит в R8 v1 deliverable. `main` должен быть stable; для milestone используется feature branch, commits должны быть atomic, tags создаются только для completed milestones, verified commits push в configured remote. Hardware-related merge требует physical hardware `PASS`.

## 13. Источник истины

Утверждённые written specifications — source of truth. Приоритет: architecture/ISA, microarchitecture/control-word, generated microcode, software implementations, hardware implementation. Emulator и physical wiring не могут silently redefine architectural behavior.

## Связанные решения и документы

- [ISA R8 v1](isa.md) определяет кодирование и семантику инструкций.
- [Микроархитектура](microarchitecture.md) описывает исполнение ISA через microsteps.
- [Control Word](control-word.md) задаёт управляющие поля для микроархитектуры.
- [Архитектура memory](memory.md) уточняет unified SRAM и image contract.
- [Активные ADR](adr/README.md) фиксируют принятые архитектурные решения.
