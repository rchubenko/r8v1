# Task M1-008: ALU ADD

## Summary

Добавлена stateless 8-bit ADD operation с immutable result object и concrete flags Z, C, S, O.

## Sources

Решение основано на `AGENTS.md`, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/adr/README.md` и активных ADR, а также на `cpu/values.py`, `cpu/register.py`, `cpu/__init__.py` и reports Tasks 2 и 7.

## Design decision

Выбрана простая stateless function `add(a, b) -> AddResult`. Stateful ALU object, clock, reset и сохранение последнего результата не добавлялись.

`AddResult` реализован как `@dataclass(frozen=True, slots=True)`. Frozen result предотвращает изменение результата и flags после вычисления. Result object ADD-specific, потому что unified ALU API и SUB относятся к будущим Tasks 9–10.

Выбран exhaustive test для всех `256 x 256 = 65536` пар: для 8-bit операции он остаётся быстрым и даёт полное покрытие арифметики и flags. Ожидаемые значения tests вычисляются независимой формулой.

FLAGS latch отсутствует: Task 8 только возвращает concrete result и flags, не записывая их в A или FLAGS.

## Arithmetic and flags

```text
wide_sum = A + B
result = wide_sum & 0xFF
Z = result == 0x00
C = wide_sum > 0xFF
S = bool(result & 0x80)
O = (~(A7 XOR B7)) AND (A7 XOR R7)
```

Inputs проходят существующую `validate_byte`; input masking и input modulo normalization отсутствуют.

## Changes

- Добавлены `cpu.alu_add.add` и immutable `AddResult`.
- Добавлены public exports `add` и `AddResult` через `cpu/__init__.py`.
- Добавлены unit tests ADD.
- Обновлён milestone index; hash текущего commit оставлен `—` до следующего documentation update.

## Public API

```python
result = add(0x7F, 0x01)

result.result
result.zero
result.carry
result.sign
result.overflow
```

## Tests

Проверены basic arithmetic, carry/wrap, zero, sign, positive и negative signed overflow, flag combinations, invalid operands, error context, immutability и stateless calls. Exhaustive test проверяет все 65536 input combinations.

## Verification

Выполнены `./scripts/verify` и `git diff --check`. Полный набор tests включает предыдущие tests Tasks 2–7 и новые ADD tests.

## Architectural compliance

Architecture, ISA, microarchitecture, control word, memory model и активные ADR не изменены. SUB, ALU mode dispatcher, unified ALU, FLAGS register/latch, A/B orchestration, instruction execution, control-word decode, emulator, simulator и hardware work отсутствуют. Hardware status — `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
model: add ALU addition
```

Hash текущего commit намеренно не записывается до следующего documentation update.

## Follow-up

Следующая задача — Task 9: ALU SUB. FLAGS latch и unified ALU API остаются вне текущего commit.
