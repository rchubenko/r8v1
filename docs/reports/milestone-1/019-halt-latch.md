# Task M1-019: HALT latch

## Summary

Добавлена самостоятельная детерминированная модель HALT latch. Она хранит boolean state, устанавливается операцией `latch()` и сохраняет `True` до вызова `reset()`.

## Sources

Решение основано на `AGENTS.md`, `README.md`, `docs/plans/milestone-1-component-models.md`, `docs/reports/milestone-1/README.md`, `docs/reports/milestone-1/018-microstep-counter.md`, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/memory.md`, `docs/adr/README.md` и всеми активными ADR, особенно ADR-0006, ADR-0008 и ADR-0010. Реализация сверена с `cpu/register.py`, `cpu/microstep.py`, `cpu/program_counter.py`, `cpu/sram.py`, `cpu/__init__.py`, существующими stateful component tests, `docs/testing/software.md`, `pyproject.toml` и `scripts/verify`.

## Design decision

Выбран named type `HaltLatch` с прямой boolean implementation.

- Read API: read-only property `is_halted` с actual type `bool`.
- Latch operation: `latch()` без arguments, устанавливает state в `True` и idempotent при повторном вызове.
- Reset operation: `reset()` без arguments, очищает state в `False` и является idempotent.
- Constructor не принимает configurable initial value.
- `FixedWidthRegister` не используется, поскольку HALT latch является boolean state, а не 4/8/12-bit storage component.
- Отдельный `hold()` отсутствует: удержание является естественным состоянием latch между `latch()` и `reset()`.

## Latch state

```text
initial/reset = False
latch = True
True remains True until reset
```

Модель не представляет clock edge и не декодирует `HALT` bit, opcode или control word.

## Hold and reset

После `latch()` repeated reads и repeated `latch()` сохраняют `True`. `reset()` переводит только этот latch в `False`; повторный `latch()` после reset снова устанавливает `True`.

System-wide reset priority, asynchronous assertion и synchronized release остаются orchestration concern согласно ADR-0006.

## Component separation

`HaltLatch` не содержит references на другие CPU components и не вызывает их methods. Модель:

- не блокирует PC;
- не блокирует MICROSTEP;
- не изменяет registers;
- не изменяет SRAM;
- не управляет DATA BUS;
- не управляет clock.

Последующая блокировка architectural state после HALT относится будущему simulator/clock orchestration layer.

## Changes

- Добавлены `cpu.halt.HaltLatch` и public export через `cpu/__init__.py`.
- Добавлены unit tests для construction, boolean state, constructor API, idempotent latch, hold, reset, relatch, read-only property и instance isolation.
- Обновлён milestone index; hash commit оставлен `—` до создания commit.

## Public API

```python
from cpu import HaltLatch

halt = HaltLatch()
assert halt.is_halted is False

halt.latch()
assert halt.is_halted is True

halt.reset()
assert halt.is_halted is False
```

## Tests

Добавлено 10 test cases. Проверены initial `False`, actual boolean type, отсутствие configurable constructor state, `latch()` без arguments, idempotent latch, hold until reset, idempotent reset, reset latched state, relatch after reset, read-only state и instance isolation.

Integration tests с PC, MICROSTEP, registers или SRAM не создавались: отсутствие orchestration подтверждается границами production API и этим report.

## Performance

```text
time ./scripts/verify: real 3.925s
pytest: 558 passed in 2.94s
```

Runtime остаётся практичным для полного regression run. Timing не закрепляется жёстким assertion.

## Verification

`time ./scripts/verify`, полный pytest, formatting, lint, mypy и documentation checks прошли. `git diff --check` также прошёл. Hardware verification не выполняется; hardware status — `NOT_TESTED`.

## Architectural compliance

Не добавлены control-word decode, opcode handling, reserved opcode handling, halt reason, canonical HALT validation, CPU blocking orchestration, clock/rising edge, reset coordinator, instruction execution, emulator, simulator или hardware work.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
model: add HALT latch
```

Push и tag не выполняются.

## Follow-up

Следующая задача — Task 20: условный component-state container. HALT edge semantics и блокировка CPU state остаются за будущим simulator/clock orchestration layer.
