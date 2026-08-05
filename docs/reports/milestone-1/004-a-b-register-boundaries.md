# Task M1-004: A and B register boundaries

## Summary

Зафиксирована граница Register A и Register B поверх существующего `FixedWidthRegister`. Новые production classes, aliases и tests не добавлены.

## Sources

Решение основано на `AGENTS.md`, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/adr/README.md` и активных ADR, а также на `cpu/register.py`, `cpu/values.py`, `cpu/__init__.py` и report Task 3.

## Design decision

Выбран вариант B: A и B в будущих component-state boundaries будут представлены отдельными экземплярами generic `FixedWidthRegister`:

```python
a = FixedWidthRegister(width=8, reset_value=0x00)
b = FixedWidthRegister(width=8, reset_value=0x00)
```

Решение закрепляет следующие invariants через существующий register API:

- A имеет width 8 и reset value `0x00`;
- B имеет width 8 и reset value `0x00`;
- initial value каждого экземпляра равен `0x00`;
- `load`, `reset`, read-only `value` и strict validation переиспользуются без изменений;
- A и B являются разными экземплярами и не разделяют state.

Semantic ownership A и B появится в будущем state container и соответствующих integration boundaries. A может участвовать в будущем FLAGS load event, а B может подавать значение в ALU и не управлять DATA BUS; эти связи не являются частью Task 4.

Отдельные classes сейчас не добавляют invariants или behavior: оба типа имеют одинаковый width, reset и API. Пустые wrappers или aliases нарушили бы KISS и создали premature abstraction без дополнительного type safety.

## Alternatives considered

Вариант A с `RegisterA` и `RegisterB` рассмотрен и отклонён. Тонкие наследники могли бы скрыть width и reset parameters, но не добавили бы нового поведения, validation или устойчивого type contract, необходимого текущим tests и state boundaries. Их появление на этом этапе также могло бы преждевременно перенести будущие connection semantics в register types.

## Changes

- Создан этот design report.
- В milestone index Task 4 отмечена как `COMPLETED` и получила ссылку на report.
- Production API `cpu` не изменён.
- Task 3 implementation и tests не изменены.

## Tests

Новые tests не добавлялись: новый production API отсутствует, а контракт `FixedWidthRegister` уже покрыт unit tests Task 3. Tests для A/B wiring, FLAGS, ALU и DATA BUS остаются вне scope.

## Verification

Выполнены `./scripts/verify` и `git diff --check`. Проверено, что diff содержит только Task 4 documentation changes.

## Architectural compliance

Architecture, ISA, microarchitecture, control word, memory model и активные ADR не изменены. Не добавлены FLAGS behavior, ALU behavior, DATA BUS behavior, clock semantics, instruction execution, emulator, simulator или hardware work. Hardware status — `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
docs: define A and B register boundaries
```

Hash текущего commit намеренно не записывается до следующего documentation update.

## Follow-up

Будущие state boundaries должны создать независимые экземпляры `FixedWidthRegister` для A и B. Task 5 — MAR; она не входит в текущий commit.
