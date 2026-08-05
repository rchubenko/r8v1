# Task M1-009: ALU SUB

## Summary

Добавлена функция SUB для 8-битных значений без состояния с неизменяемым объектом результата и конкретными флагами Z, C, S, O.

## Sources

Решение основано на `AGENTS.md`, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/adr/README.md` и активных ADR, а также на `cpu/values.py`, `cpu/alu_add.py`, `cpu/__init__.py` и reports Tasks 2 и 8.

## Design decision

Выбрана функция без состояния `subtract(a, b) -> SubtractResult`, согласованная с `add(a, b)`. Для сохранения изоляции Tasks 8–9 используется отдельный неизменяемый `SubtractResult`; общий тип результата и объединённая ALU откладываются до Task 10.

Выбран исчерпывающий тест для всех `256 x 256 = 65536` пар. Он остаётся практичным и симметричен исчерпывающему покрытию Task 8. Ожидаемые значения вычисляются независимыми формулами.

Объединённая ALU и диспетчеризация режимов не добавлялись. Carry явно имеет семантику отсутствия заёма: `C = 1` только когда `A >= B`.

## Arithmetic and flags

```text
result = (A - B) & 0xFF
Z = result == 0x00
C = A >= B
S = bool(result & 0x80)
O = (A7 XOR B7) AND (A7 XOR R7)
```

Входы проходят существующую `validate_byte`; маскирование и нормализация входов по модулю отсутствуют. Модуль применяется только к арифметическому результату.

## Changes

- Добавлены `cpu.alu_sub.subtract` и неизменяемый `SubtractResult`.
- Добавлены public exports `subtract` и `SubtractResult` через `cpu/__init__.py`.
- Добавлены unit tests SUB.
- Обновлён milestone index; hash текущего commit оставлен `—` до следующего documentation update.

## Public API

```python
result = subtract(0x80, 0x01)

result.result
result.zero
result.carry
result.sign
result.overflow
```

## Tests

Проверены базовая арифметика, underflow, carry без заёма, zero, sign, signed overflow, обязательные граничные случаи, недопустимые операнды, контекст ошибки, неизменяемость и вызовы без состояния. Исчерпывающий тест проверяет все 65536 комбинаций входов.

## Verification

Выполнены `./scripts/verify` и `git diff --check`. Полный набор tests включает предыдущие tests Tasks 2–8 и новые SUB tests.

## Architectural compliance

Architecture, ISA, microarchitecture, control word, memory model и активные ADR не изменены. Unified ALU, mode dispatcher, FLAGS register/latch, instruction execution, control-word decode, emulator, simulator и hardware work отсутствуют. Hardware status — `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
model: add ALU subtraction
```

Hash текущего commit намеренно не записывается до следующего documentation update.

## Follow-up

Следующая задача — Task 10: unified public ALU model. FLAGS latch остаётся вне текущего commit.
