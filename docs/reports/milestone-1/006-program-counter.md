# Task M1-006: Program Counter

## Summary

Добавлена самостоятельная модель Program Counter как фиксированного 12-bit byte-addressed stateful component.

## Sources

Решение основано на `AGENTS.md`, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/memory.md`, `docs/adr/README.md` и активных ADR, а также на `cpu/register.py`, `cpu/values.py`, `cpu/mar.py`, `cpu/__init__.py` и reports Tasks 3–5.

## Design decision

Выбран named type `ProgramCounter`, реализованный наследованием от `FixedWidthRegister`.

Parallel load выражен существующим `load(value)`: он принимает уже подготовленный 12-bit address и сохраняет строгую validation без masking, truncation или modulo. Explicit `load_parallel()` не добавлялся.

Hold реализован неявно: отсутствие вызова `load()` или `increment()` сохраняет текущее значение. Отдельный no-op `hold()` не добавлялся, чтобы не расширять API без самостоятельного поведения.

Modulo применяется только в `increment()`, поскольку `0xFFF -> 0x000` является утверждённым поведением PC. Generic `FixedWidthRegister.load()` не получает modulo semantics.

Fetch orchestration отсутствует: PC не читает SRAM, не выбирает IR operand, не загружает MAR и не выполняет два increment за instruction.

## Changes

- Добавлен `cpu.program_counter.ProgramCounter`.
- Добавлен метод `increment()` с modulo `0x1000`.
- Добавлен минимальный public export через `cpu/__init__.py`.
- Добавлены unit tests Program Counter.
- Обновлён milestone index; hash текущего commit оставлен `—` до следующего documentation update.

## Public API

```python
pc = ProgramCounter()
pc.load(0xABC)
pc.increment()
current = pc.value
pc.reset()
```

## Tests

Проверены:

- width `12`, reset `0x000` и initial value `0x000`;
- отсутствие configurable constructor parameters;
- parallel load адресов `0x000`, `0x001`, `0x7FF`, `0x800`, `0xFFF`;
- invalid `-1`, `0x1000`, `True`, `False`, неподходящий тип;
- `InvalidComponentValue`, error context и сохранение state после failed load;
- increment `0x000 -> 0x001`, `0x001 -> 0x002`, `0xFFE -> 0xFFF`, `0xFFF -> 0x000`;
- последовательные increment после wrap;
- implicit hold;
- reset после load, increment и wrap;
- изоляция двух PC instances.

## Verification

Выполнены `./scripts/verify` и `git diff --check`. Полный набор tests включает предыдущие tests Tasks 2–5 и новые Program Counter tests.

## Architectural compliance

Architecture, ISA, microarchitecture, control word, memory model и активные ADR не изменены. Не добавлены fetch orchestration, IR/MAR integration, jump/branch behavior, `PC_OP` decoding, clock semantics, instruction execution, emulator, simulator или hardware work. Hardware status — `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
model: add program counter
```

Hash текущего commit намеренно не записывается до следующего documentation update.

## Follow-up

Следующая задача — Task 7: Instruction Register. Fetch sequence и address source selector остаются вне текущего commit.
