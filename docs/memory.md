# Архитектура memory R8 v1

## Статус

**Статус:** Утверждённая база
**Model:** Unified SRAM
**Logical capacity:** 4096 x 8 bit

## 1. Address space и interface

Address range `0x000 .. 0xFFF`; все addresses являются byte addresses, code и data shared. SRAM interface: `A[11:0]`, bidirectional `D[7:0]`, chip enable, output enable, write enable. Physical component должен поддерживать 5 V policy или validated compatibility, asynchronous read, deterministic write timing и explicit `/CE`, `/OE`, `/WE`.

```text
PC or IR operand -> Address MUX -> MAR -> SRAM A[11:0]
SRAM D[7:0] <-> DATA BUS
```

Read: MAR, CPU ownership, SRAM read controls, `OE_SEL=OE_SRAM`, destination latch на rising edge. Write: MAR, CPU ownership, valid DATA BUS source, `RAM_WE=1`, compliant write pulse.

## 2. Размещение программы

Assembler загружает code с `0x000`, data размещает сразу после final instruction byte. Instruction занимает два bytes. Code/data image не wrap; code-plus-data больше 4096 bytes отвергается.

## 3. Владение loader

SRAM имеет двух возможных owners: CPU и Raspberry Pi loader. `MEM_OWNER` выбирает ровно одного:

```text
MEM_OWNER = CPU
MEM_OWNER = PI
```

Ownership switch управляет address lines, data direction/drivers, write control и output/chip enable. Exact polarity — board-level decision; software APIs используют symbolic states.

Safe loading: assert RESET, stop architectural clock, select Pi, configure interfaces, write image, optionally read back, disable Pi drivers, select CPU, verify exclusive ownership, release RESET synchronously, start clock. Ownership менять при running CPU запрещено; предпочтителен break-before-make.

Hardware должен предотвращать simultaneous CPU/Pi driving, writes другого owner и spurious write pulse. Timing values записываются в component-specific hardware ADR.

## 4. Защита и reset

v1 не предоставляет ROM/write protection, privilege, memory management или execute protection. Program может overwrite code или execute data. RESET не стирает SRAM: он возвращает CPU state и PC в `0x000`, loaded image сохраняется.

## 5. Контракт software image

Новая software machine содержит ровно 4096 SRAM bytes, initialized to `0x00`. Standard executable image ровно 4096 bytes: code начинается `0x000`, data следует за code, remainder zero-filled. Loading заменяет complete software SRAM. RESET SRAM не очищает. Physical SRAM до loader initialization unspecified; hardware parity требует full image до RESET release.

## Связанные решения и документы

- [Архитектура R8 v1](architecture.md) задаёт unified memory и address path.
- [ISA R8 v1](isa.md) определяет instruction width и absolute memory operands.
- [ADR-0001](adr/0001-unified-memory.md) фиксирует единую SRAM для code и data.
- [ADR-0007](adr/0007-memory-ownership.md) фиксирует исключительное владение SRAM.
