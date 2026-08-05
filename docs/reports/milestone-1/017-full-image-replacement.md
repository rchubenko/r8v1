# Task M1-017: Full-image replacement

## Summary

Расширена модель `SRAM` атомарной полной заменой software memory image размером ровно 4096 bytes.

## Sources

Решение основано на `AGENTS.md`, `README.md`, `docs/plans/milestone-1-component-models.md`, `docs/reports/milestone-1/README.md`, `docs/reports/milestone-1/016-sram-storage.md`, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/memory.md`, `docs/adr/README.md` и всеми активными ADR, особенно ADR-0001, ADR-0007 и ADR-0010. Реализация сверена с `cpu/sram.py`, `cpu/values.py`, `cpu/__init__.py`, существующими tests и exception conventions, `docs/testing/software.md`, `pyproject.toml` и `scripts/verify`.

## Design decision

Добавлен один метод `SRAM.replace_image(image)`. Принимаются только `bytes` и `bytearray`; arbitrary iterable, list, string, path, file object и sparse mapping не принимаются. Для invalid image добавлен минимальный `InvalidMemoryImage(ValueError)`, а invalid container type вызывает `TypeError`.

Validation order:

1. проверить input type;
2. проверить exact length `SRAM_SIZE`;
3. создать defensive `bytearray` copy;
4. заменить internal storage одним присваиванием.

До последнего шага existing storage не изменяется. `bytes` и `bytearray` уже гарантируют byte range, поэтому отдельная validation каждого элемента не нужна и общий iterable contract не вводится.

Snapshot/export не добавлялся: exhaustive read-based tests проверяют complete contents без расширения public API.

## Image contract

```text
image size = exactly 4096 bytes
image offset 0 -> SRAM address 0x000
image offset 4095 -> SRAM address 0xFFF
replacement = complete, no merge/padding/wrap
```

Метод не анализирует contents image, не выполняет assembler layout, zero-filling, padding, truncation или relocation.

## Validation and atomicity

Invalid type и invalid length отклоняются до mutation. Error length содержит expected и actual sizes. При любой ошибке прежнее содержимое всех 4096 bytes сохраняется. Replacement не выполняется через публичные `write()` calls и не создаёт промежуточное частичное состояние.

Для `bytearray` создаётся независимая копия: дальнейшая mutation caller-owned input не влияет на SRAM.

## Replacement behavior

После успешной замены каждый SRAM address равен byte с тем же image offset. Следующая valid replacement полностью уничтожает логическое содержимое предыдущей image. Обычный `write()` после replacement изменяет только выбранный byte.

## CPU reset persistence

Replacement не связана с CPU reset. SRAM по-прежнему не имеет `reset()` или `clear()` API; CPU reset не очищает загруженный image. Новый `SRAM()` остаётся zero-filled. Ownership, loader и physical read-back workflow не реализуются.

## Changes

- Добавлены `SRAM.replace_image()` и `InvalidMemoryImage`.
- Добавлен public export `InvalidMemoryImage` через `cpu/__init__.py`.
- Добавлены tests zero/patterned images, full overwrite, length/type rejection, atomicity, defensive copy, repeated replacement, write interaction и instance isolation.
- Обновлён milestone index; hash commit оставлен `—`.

## Public API

```python
from cpu import SRAM, SRAM_SIZE

image = bytes(address & 0xFF for address in range(SRAM_SIZE))
memory = SRAM()
memory.replace_image(image)

assert memory.read(0x000) == image[0]
assert memory.read(0xFFF) == image[0xFFF]
```

Invalid length:

```python
memory.replace_image(b"\x00")  # InvalidMemoryImage
```

## Tests

Добавлено 16 test cases. Проверены zero image, deterministic patterned image со всеми 4096 addresses, second complete replacement, length boundaries, invalid types, atomic failure, defensive bytearray copy, write/replacement interaction, repeated replacement и instance isolation. Существующие 38 SRAM storage tests Task 16 также проходят.

## Performance

```text
time ./scripts/verify: real 4.714s
pytest: 532 passed in 3.03s
```

Runtime остаётся практичным для полного regression run. Timing не закрепляется жёстким assertion.

## Verification

Перед commit выполняются `time ./scripts/verify`, полный pytest, formatting, lint, mypy, documentation checks и `git diff --check`. Hardware verification не выполняется; hardware status — `NOT_TESTED`.

## Architectural compliance

Architecture, ISA, microarchitecture, control word, memory model и активные ADR не изменены. Assembler layout, padding, truncation, partial/offset loading, file I/O, loader, ownership, reset/clear, MAR/DATA BUS integration, memory control signals, emulator, simulator и hardware work отсутствуют.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
model: add SRAM full-image replacement
```

Hash текущего commit будет указан в Git metadata; push и tag не выполняются.

## Follow-up

Следующая задача — Task 18: MICROSTEP counter. Image loading не расширяется в loader protocol.
