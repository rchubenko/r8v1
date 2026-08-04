# ADR-0010: Deterministic Software Model Semantics

## Status

Accepted

## Контекст

Утверждённые ISA и microarchitecture намеренно моделируют hardware details: concrete FLAGS outputs, undriven DATA BUS, modulo counters, HALT latching и persistent SRAM. Software models и parity tests нуждаются в deterministic rules для этих случаев без переопределения physical или architectural behavior.

## Решение

### Flag validity

Physical FLAGS всегда содержат concrete binary values. Software models дополнительно поддерживают `flags_defined_mask`.

- RESET defines Z, C, S, and O.
- ADD/SUB define Z, C, S, and O.
- LDI/LDA define only Z and S.
- Instructions that preserve FLAGS also preserve `flags_defined_mask`.

Parity сравнивает `flags_defined_mask` и values только для marked-defined flags. Strict simulation выдаёт diagnostic при чтении undefined flag conditional jump. Hardware-like diagnostic mode может продолжить с concrete physical value.

### DATA BUS validity

Undriven DATA BUS представляется как `HIGH_Z`/`None`. Любой DATA BUS consumer требует ровно one producer. Consumers: `E_A`, `E_B`, `E_IRH`, `E_IRL`, `RAM_WE`. `E_MAR` использует отдельный 12-bit address path. One producer без consumer разрешён для bring-up и debugging.

### HALT edge

HALT использует canonical neutral control word. На его rising edge `HALT_STATE` становится 1. Последующие clock edges удерживают microstep counter и не меняют architectural CPU state. RESET имеет priority, очищает HALT и возвращает counter в T0. Validators отвергают HALT с register, PC или memory write actions.

### PC boundary behavior

PC — 12-bit modulo counter: `0xFFF + 1 = 0x000`. Fetch через address-space boundary определён. Instruction alignment не требуется, любой 12-bit byte address может быть jump target. Assembler не wrap layout и отвергает images больше 4096 bytes.

### Software SRAM и executable images

Новая software machine имеет 4096 bytes, initialized to `0x00`. Standard executable image ровно 4096 bytes; code начинается в `0x000`, data следует за code, remainder zero-filled. Loading заменяет всю software SRAM. RESET не очищает SRAM. Physical SRAM до loading unspecified. Hardware parity требует от Pi loader установить full image до RESET release.

## Последствия

Positive:

- parity tests are deterministic without pretending unspecified flags have architectural meaning;
- invalid microcode bus use is detected explicitly;
- HALT and boundary fetch behavior are identical across models;
- assembler, emulator, simulator, and loader share one image contract.

Negative:

- software state includes metadata not present as a physical register;
- strict and hardware-like diagnostic modes must both be tested;
- hardware loading always writes or guarantees a full 4096-byte image.
