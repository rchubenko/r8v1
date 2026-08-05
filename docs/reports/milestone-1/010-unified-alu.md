# Task M1-010: Unified ALU model

## Summary

Добавлена минимальная публичная модель ALU без состояния, объединяющая утверждённые операции ADD и SUB через единый `evaluate()` API.

## Sources

Решение основано на `AGENTS.md`, `README.md`, `docs/plans/milestone-1-component-models.md`, `docs/reports/milestone-1/README.md`, reports Tasks 8–9, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/adr/README.md` и всех активных ADR. Реализация сверена с `cpu/alu_add.py`, `cpu/alu_sub.py`, `cpu/values.py`, `cpu/__init__.py`, существующими tests, `docs/testing/software.md`, `pyproject.toml` и `scripts/verify`.

## Design decision

Выбрана функция без состояния `evaluate(mode, a, b) -> ALUResult`. Объект ALU, конструктор, ссылки на регистры и сохранение последнего результата не добавлялись.

Используется enum `ALUMode` только со значениями `ADD` и `SUB`. Значения enum являются symbolic strings (`"add"` и `"sub"`), а не числовыми кодами control word.

Результат унифицирован через отдельный immutable `ALUResult` с полями `result`, `zero`, `carry`, `sign` и `overflow`. Существующие `AddResult`, `SubtractResult`, `add()` и `subtract()` сохранены без изменений и остаются public API для low-level tests и использования.

`evaluate()` делегирует вычисление существующей функции ADD или SUB и только преобразует её результат в `ALUResult`. Raw integers и другие значения в качестве mode отклоняются через `TypeError`.

Numeric `ALU_MODE` decoding отсутствует намеренно: значения `000` и `001` принадлежат control-word layer и будут обрабатываться отдельной будущей ответственностью.

## Public API

```python
from cpu import ALUMode, ALUResult, evaluate

result = evaluate(ALUMode.ADD, 0x7F, 0x01)
assert result == ALUResult(
    result=0x80,
    zero=False,
    carry=False,
    sign=True,
    overflow=True,
)
```

## Dispatch behavior

- `ALUMode.ADD` вызывает существующую `add()` и сохраняет её арифметику и flags.
- `ALUMode.SUB` вызывает существующую `subtract()` и сохраняет её арифметику и flags.
- `evaluate()` всегда возвращает `ALUResult`.
- Raw integers, включая `0` и `1`, не принимаются как mode.
- Reserved modes и numeric decoder отсутствуют.
- Вызовы не имеют общего изменяемого состояния.

## Changes

- Добавлены `ALUMode`, `ALUResult` и `evaluate()` в `cpu/alu.py`.
- Добавлены public exports через `cpu/__init__.py`.
- Добавлены unified ALU unit tests с dispatch parity для ADD и SUB.
- Обновлён milestone index; hash commit оставлен `—`.

## Tests

Добавлено 32 тестовых случая. Проверены состав enum, symbolic values, dispatch parity для representative ADD/SUB cases, единый immutable result type, parity полей с legacy result types, invalid mode, raw numeric modes, invalid operands, stateless behavior и отсутствие control-word decoder. Существующие exhaustive ADD/SUB tests также выполняются в полной регрессии.

## Verification

Targeted tests, форматирование, lint и mypy проходят. Полная проверка `./scripts/verify` выполняется перед commit и включает backward compatibility tests, exhaustive ADD/SUB tests и documentation checks.

Hardware verification не выполнялась; hardware status — `NOT_TESTED`.

## Architectural compliance

Architecture, ISA, microarchitecture, control word, memory model и активные ADR не изменены. Numeric `ALU_MODE` decoding, reserved ALU modes, FLAGS register/latch, A/B orchestration, instruction execution, control-word execution, emulator, simulator и hardware work отсутствуют.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
model: add unified ALU interface
```

Hash текущего commit будет указан в Git metadata; push и tag не выполняются.

## Follow-up

Следующая задача — Task 11: DATA BUS resolver. FLAGS values, defined mask и FLAGS latch остаются в Tasks 13–15.
