# ADR-0010: Детерминированная семантика software models

## Статус

Принято

## Контекст

Утверждённые ISA и microarchitecture намеренно моделируют аппаратные детали: concrete FLAGS outputs, undriven DATA BUS, modulo counters, HALT latching и persistent SRAM. Software models и parity tests нуждаются в deterministic rules для этих случаев без переопределения physical или architectural behavior.

## Решение

### Допустимость flags

Physical FLAGS всегда содержат concrete binary values. Software models дополнительно поддерживают `flags_defined_mask`.

- RESET определяет Z, C, S и O.
- ADD/SUB определяют Z, C, S и O.
- LDI/LDA определяют только Z и S.
- Instructions, сохраняющие FLAGS, также сохраняют `flags_defined_mask`.

Parity сравнивает `flags_defined_mask` и values только для flags, отмеченных как defined. Strict simulation выдаёт diagnostic при чтении undefined flag conditional jump. Hardware-like diagnostic mode может продолжить с concrete physical value.

### Допустимость DATA BUS

Undriven DATA BUS представляется как `HIGH_Z`/`None`. Любой DATA BUS consumer требует ровно one producer. Consumers: `E_A`, `E_B`, `E_IRH`, `E_IRL`, `RAM_WE`. `E_MAR` использует отдельный 12-bit address path. One producer без consumer разрешён для bring-up и debugging.

### Фронт HALT

HALT использует canonical neutral control word. На его rising edge `HALT_STATE` становится 1. Последующие clock edges удерживают microstep counter и не меняют architectural CPU state. RESET имеет priority, очищает HALT и возвращает counter в T0. Validators отвергают HALT с register, PC или memory write actions.

### Поведение PC на границе

PC — 12-bit modulo counter: `0xFFF + 1 = 0x000`. Fetch через address-space boundary определён. Instruction alignment не требуется, любой 12-bit byte address может быть jump target. Assembler не wrap layout и отвергает images больше 4096 bytes.

### Software SRAM и исполняемые образы

Новая software machine имеет 4096 bytes, initialized to `0x00`. Standard executable image ровно 4096 bytes; code начинается в `0x000`, data следует за code, remainder zero-filled. Loading заменяет всю software SRAM. RESET не очищает SRAM. Physical SRAM до loading unspecified. Hardware parity требует от Pi loader установить full image до RESET release.

## Последствия

Положительные:

- parity tests are deterministic without pretending unspecified flags have architectural meaning;
- invalid microcode bus use is detected explicitly;
- HALT and boundary fetch behavior are identical across models;
- assembler, emulator, simulator, and loader share one image contract.

Отрицательные:

- software state includes metadata not present as a physical register;
- strict and hardware-like diagnostic modes must both be tested;
- hardware loading always writes or guarantees a full 4096-byte image.
