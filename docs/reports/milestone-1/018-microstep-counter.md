# Task M1-018: MICROSTEP counter

## Summary

Добавлена самостоятельная модель 4-bit MICROSTEP counter со состояниями T0..T15, reset в T0, modulo-16 increment и explicit return в T0.

## Sources

Решение основано на `AGENTS.md`, `README.md`, `docs/plans/milestone-1-component-models.md`, `docs/reports/milestone-1/README.md`, reports Tasks 3, 6 и 17, `docs/architecture.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/isa.md`, `docs/memory.md`, `docs/adr/README.md` и всеми активными ADR, особенно ADR-0003, ADR-0006, ADR-0009 и ADR-0010. Реализация сверена с `cpu/register.py`, `cpu/values.py`, `cpu/program_counter.py`, `cpu/__init__.py`, соответствующими tests, package/API conventions, `docs/testing/software.md`, `pyproject.toml` и `scripts/verify`.

## Design decision

Выбран named type `MicrostepCounter`, реализованный наследованием от `FixedWidthRegister`, как ранее `ProgramCounter` и `MemoryAddressRegister`. Width всегда 4, reset value всегда `0x0`, а component-specific operations добавляют только increment и return T0.

Состояние представлено integer value `0x0..0xF`, соответствующими T0..T15. Отдельный symbolic enum не добавлялся: integer representation непосредственно переиспользует утверждённый 4-bit register boundary и не вводит дополнительный public type.

Наследованный `load()` остаётся доступен для низкоуровневой установки состояния и strict nibble validation, что соответствует существующему subclass convention. Tests microstep transitions не зависят от arbitrary load и достигают состояний через increment.

Hold является implicit: отсутствие вызова `increment()`, `return_to_t0()` или `reset()` сохраняет state. Explicit no-op `hold()` не добавлялся.

`return_to_t0()` отделён от `reset()`: первый является обычной component action для завершения sequence, второй — reset behavior самого counter. Оба приводят значение к T0, но не затрагивают другие components.

Modulo-16 increment из T15 в T0 является корректным behavior counter. Ошибка выполнения microcode beyond T15 не реализуется; она относится к будущему validator/simulator layer.

## Counter states

```text
T0..T15 represented by values 0x0..0xF
reset = T0
```

## Increment and wraparound

```text
next = (current + 1) & 0xF
T15 + 1 -> T0
```

Increment не моделирует clock edge, accepted pulse, control word или microcode sequence validation.

## Return T0

`return_to_t0()` переводит любое состояние T0..T15 в T0, является idempotent и не декодирует `STEP_END`.

## Hold and reset

Implicit hold сохраняет текущее значение при отсутствии transition operation. `reset()` возвращает только этот counter в T0. System reset priority, asynchronous assertion и synchronized release остаются вне Task 18.

## Changes

- Добавлены `cpu.microstep.MicrostepCounter` и public export через `cpu/__init__.py`.
- Добавлены unit tests construction, sequence, wraparound, repeated cycles, return T0, implicit hold, reset, isolation, inherited validation и range invariant.
- Обновлён milestone index; hash commit оставлен `—`.

## Public API

```python
from cpu import MicrostepCounter

counter = MicrostepCounter()
counter.increment()
assert counter.value == 1

counter.return_to_t0()
assert counter.value == 0

counter.reset()
```

## Tests

Добавлено 16 test cases. Проверены полный sequence T0..T15, wraparound, 16/17 increments, несколько cycles, explicit return T0 из representative states, implicit hold, reset, instance isolation, inherited strict load validation и сохранение range `0..15` после 1000 increments.

## Performance

```text
time ./scripts/verify: real 4.652s
pytest: 548 passed in 3.06s
```

Runtime остаётся практичным для полного regression run. Timing не закрепляется жёстким assertion.

## Verification

Перед commit выполняются `time ./scripts/verify`, полный pytest, formatting, lint, mypy, documentation checks и `git diff --check`. Hardware verification не выполняется; hardware status — `NOT_TESTED`.

## Architectural compliance

Не добавлены execution-beyond-T15 error, microcode validation, `STEP_END` decoding, HALT integration, clock/rising edge, instruction execution, emulator, simulator или hardware work.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
model: add microstep counter
```

Hash текущего commit будет указан в Git metadata; push и tag не выполняются.

## Follow-up

Следующая задача — Task 19: HALT latch. Microcode sequence validation и clock orchestration остаются за будущими layers.
