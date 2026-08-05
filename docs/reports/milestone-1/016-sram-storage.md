# Task M1-016: SRAM storage model

## Summary

Добавлена самостоятельная детерминированная software-модель unified SRAM R8 v1 объёмом 4096 bytes с zero-filled initialization, byte read/write и строгой validation.

## Sources

Решение основано на `AGENTS.md`, `README.md`, `docs/plans/milestone-1-component-models.md`, `docs/reports/milestone-1/README.md`, reports Tasks 2 и 15, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/memory.md`, `docs/adr/README.md` и всеми активными ADR, особенно ADR-0001, ADR-0007 и ADR-0010. Реализация сверена с `cpu/values.py`, `cpu/register.py`, `cpu/mar.py`, `cpu/__init__.py`, существующими exception и package conventions, tests, `docs/testing/software.md`, `pyproject.toml` и `scripts/verify`.

## Design decision

Выбран named component `SRAM` с фиксированным capacity `SRAM_SIZE = 4096`. Internal storage представлен отдельным `bytearray(SRAM_SIZE)` для каждого instance. Constructor не принимает size или initial contents: это конкретная software SRAM R8 v1, а не generic memory abstraction.

Public API ограничен `read(address)` и `write(address, value)`. Snapshot/export не добавлялся: exhaustive read всех 4096 addresses достаточно для Task 16 tests, а image/export contract относится к Task 17.

SRAM не имеет public `reset()`, `clear()` или `initialize()` API. Новый instance создаётся zero-filled; CPU reset не вызывает операции SRAM и не очищает storage.

Validation order для `write()`:

1. validate address;
2. validate byte value;
3. mutate exactly one storage location.

Поэтому failed write не изменяет memory даже при одновременной ошибке address и value.

## Storage contract

```text
capacity = 4096 bytes
addresses = 0x000..0xFFF
initial bytes = 0x00
values = 0x00..0xFF
```

Memory unified: code/data distinction и write protection отсутствуют. Любой valid address может читаться и записываться.

## Read and write behavior

`read(address)` validates a 12-bit address and returns one integer byte without side effects. `write(address, value)` validates address and byte, then updates only selected location. Masking, modulo, truncation, pointer increments и timing semantics отсутствуют.

## Validation and atomicity

Address validation использует существующий `validate_address`, value validation — `validate_byte`, invalid inputs вызывают `InvalidComponentValue`. Invalid address, invalid value, booleans и неподходящие types отвергаются. Invalid write сохраняет прежнее содержимое и соседние bytes.

## CPU reset persistence

CPU reset не изменяет SRAM: у `SRAM` отсутствует очищающий reset API и storage не связан с CPU state. Каждый новый `SRAM()` zero-filled. Full-image replacement, image length validation и loading относятся к Task 17 и здесь не реализованы.

## Changes

- Добавлены `cpu.sram.SRAM` и public constant `SRAM_SIZE`.
- Добавлен минимальный public export через `cpu/__init__.py`.
- Добавлены unit tests zero-fill, read/write boundaries, validation, atomic failed writes, single-byte mutation, repeated operations и instance isolation.
- Обновлён milestone index; hash commit оставлен `—`.

## Public API

```python
from cpu import SRAM

memory = SRAM()
memory.write(0x123, 0xAB)
assert memory.read(0x123) == 0xAB
```

## Tests

Добавлено 38 test cases. Zero-fill проверяется exhaustive read всех 4096 addresses. Дополнительно проверены representative boundaries, valid round-trips, single-byte mutation, invalid read/write inputs, validation order, failed-write preservation, repeated operations, отсутствие `reset`/`clear` и instance isolation.

## Performance

Полная проверка после реализации:

```text
time ./scripts/verify: real 4.546s
pytest: 516 passed in 2.92s
```

Runtime остаётся практичным для полного regression run; timing не закрепляется жёстким assertion.

## Verification

Выполнены `./scripts/verify`, `git diff --check`, formatting, lint, mypy и полный pytest. Hardware verification не выполнялась; hardware status — `NOT_TESTED`.

## Architectural compliance

Architecture, ISA, microarchitecture, control word, memory model и активные ADR не изменены. Full-image replacement, executable image validation, ownership, MAR/DATA BUS integration, memory control signals, timing, clock, fetch, instruction execution, emulator, simulator и hardware work отсутствуют.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
model: add SRAM storage
```

Hash текущего commit будет указан в Git metadata; push и tag не выполняются.

## Follow-up

Следующая задача — Task 17: full-image replacement. Она добавит отдельный image API без изменения базового read/write boundary.
