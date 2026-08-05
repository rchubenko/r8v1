# Task M1-011: DATA BUS resolver

## Summary

Добавлен минимальный stateless resolver 8-битной DATA BUS. Он различает отсутствие producer, единственный byte producer и contention нескольких producers.

## Sources

Решение основано на `AGENTS.md`, `README.md`, `docs/plans/milestone-1-component-models.md`, `docs/reports/milestone-1/README.md`, `docs/reports/milestone-1/010-unified-alu.md`, `docs/architecture.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/isa.md`, `docs/memory.md`, `docs/adr/README.md` и всеми активными ADR, особенно ADR-0010. Реализация сверена с `cpu/values.py`, `cpu/__init__.py`, существующими exception conventions, immutable value conventions, tests, `docs/testing/software.md`, `pyproject.toml` и `scripts/verify`.

## Design decision

Выбрана stateless function `resolve_data_bus(producers) -> int | None`, принимающая любой `Iterable` producer values. Producer metadata не добавлялась: на этом уровне resolver решает только cardinality и byte value, а source naming относится к будущему simulator/diagnostics layer.

Canonical `HIGH_Z` представлен как `None`; отдельный singleton или electrical-state hierarchy не создавались.

Для нескольких producers добавлен project-specific `DataBusContention`, наследующий `RuntimeError`. Его сообщение содержит количество producers и значения в детерминированном порядке входной коллекции. Invalid byte values используют существующий `InvalidComponentValue`.

Сначала весь iterable materialize-ся и каждый value проходит `validate_byte`, затем проверяется cardinality. Поэтому invalid producer всегда обнаруживается до contention, в том числе в коллекции с несколькими producers. Input collection не изменяется.

Consumers, `OE_SEL`, source enable selection и control-word decoding отсутствуют, поскольку resolver не знает, существует ли consumer.

## Bus states

```text
0 producers -> None
1 producer  -> byte
2+ producers -> contention
```

Даже одинаковые values от двух producers являются contention: `[0x42, 0x42]` не объединяется в одного producer.

## Validation and contention

Каждый producer должен быть целым значением в диапазоне `0x00..0xFF`. `bool`, отрицательные значения, значения от `0x100` и неподходящие типы отклоняются без masking и modulo normalization.

Пустая коллекция разрешается как `HIGH_Z`. Один producer возвращается без изменения. Два или более valid producers вызывают `DataBusContention`.

## Changes

- Добавлены `cpu.data_bus.resolve_data_bus` и `DataBusContention`.
- Добавлены public exports через `cpu/__init__.py`.
- Добавлены unit tests для HIGH_Z, single producer, contention, equal-value contention, validation order и stateless behavior.
- Обновлён milestone index; hash commit оставлен `—`.

## Public API

```python
from cpu import DataBusContention, resolve_data_bus

value = resolve_data_bus([])
assert value is None

value = resolve_data_bus([0x42])
assert value == 0x42

try:
    resolve_data_bus([0x12, 0x34])
except DataBusContention:
    pass
```

## Tests

Проверены canonical `None`, пустые list/tuple/iterator, граничные single producer values `0x00`, `0x01`, `0x7F`, `0x80`, `0xFF`, генератор producers, два и более producers, contention при одинаковых values, diagnostic message, invalid first/later producer, validation order, неизменность input list и stateless behavior.

## Verification

Targeted tests, форматирование, lint и mypy проходят. Полная проверка `./scripts/verify` выполняется перед commit и включает предыдущие exhaustive ADD/SUB tests, unified ALU tests и новые DATA BUS tests.

Hardware verification не выполнялась; hardware status — `NOT_TESTED`.

## Architectural compliance

Architecture, ISA, microarchitecture, control word, memory model и активные ADR не изменены. Consumers, `OE_SEL` decoding, control-word behavior, register/memory latching, clock semantics, simulator и hardware work отсутствуют. Resolver не проверяет consumer без producer и допускает один producer без consumer для bring-up/debugging.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
model: add data bus resolver
```

Hash текущего commit будет указан в Git metadata; push и tag не выполняются.

## Follow-up

Следующая задача — Task 12: address source selector. Consumer semantics и `OE_SEL` decoding остаются вне Task 11.
