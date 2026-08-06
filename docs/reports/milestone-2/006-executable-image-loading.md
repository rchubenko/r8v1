# Task M2-006: Executable image loading

## Summary

Добавлена deterministic boundary загрузки полного software executable image в SRAM ISA Reference Emulator. `ArchitecturalState.load_image()` использует существующее atomic `SRAM.replace_image()` и не изменяет остальные architectural fields.

## Sources

Работа сверена с [`AGENTS.md`](../../../AGENTS.md), [README проекта](../../../README.md), [архитектурой](../../architecture.md), [ISA](../../isa.md), [memory contract](../../memory.md), [software testing policy](../../testing/software.md), [планом Milestone 2](../../plans/milestone-2-isa-reference-emulator.md), [execution contract M2-002](002-emulator-execution-contract.md), [report M2-004](004-architectural-emulator-state.md), [report M2-005](005-architectural-reset.md), [ADR-0001](../../adr/0001-unified-memory.md), [ADR-0007](../../adr/0007-memory-ownership.md), [ADR-0010](../../adr/0010-deterministic-software-model-semantics.md), SRAM API и существующими package/test conventions.

## Scope

В scope входили только software image loading boundary, exact 4096-byte validation, atomic SRAM replacement, invalid-size atomicity и preservation других architectural fields. Assembler, physical loader, ownership protocol и hardware writes не реализованы.

## Design decision

Canonical API:

```python
ArchitecturalState.load_image(image: object) -> None
```

API принимает `bytes` или `bytearray`, как разрешено existing `SRAM.replace_image()`. Он делегирует проверку типа и exact length `SRAM_SIZE == 4096`, затем atomic replacement. Mutable input копируется SRAM component и не удерживается state.

## Image contract and preservation

Valid image содержит ровно 4096 bytes с byte values `0x00..0xFF`. Invalid sizes отвергаются до mutation и не изменяют SRAM. Loading заменяет весь image, но сохраняет A, PC, IR, FLAGS, `flags_defined_mask` и HALT. Loading не вызывает reset.

После `load_image()` отдельный `reset()` возвращает registers и HALT к reset values, сохраняя загруженный SRAM image.

## Reused components and boundaries

Использован существующий `SRAM.replace_image()` без изменения `cpu/`. Не добавлены assembler semantics, physical loader, `MEM_OWNER`, GPIO, read-back protocol или hardware arbitration.

## Changes

- `emulator/state.py` — `ArchitecturalState.load_image()`.
- `tests/test_emulator_image.py` — valid, invalid, atomicity, preservation и independence tests.
- `docs/reports/milestone-2/006-executable-image-loading.md` — этот report.
- `docs/reports/milestone-2/README.md` — статус и report link для M2-006.

Source-of-truth documents, ISA, active ADR и milestone plan не изменялись.

## Tests

Проверены:

- deterministic non-trivial 4096-byte image и boundary bytes;
- complete replacement без остаточных SRAM values;
- invalid sizes `0`, `1`, `4095`, `4097` и `8192`;
- отсутствие partial mutation после invalid image;
- сохранение A, PC, IR, FLAGS/mask и HALT;
- reset после loading с сохранением image;
- bytearray input copy semantics;
- независимость SRAM между state instances.

Image loading не интерпретирует code, data, opcode или assembler layout.

## Verification

- Targeted image-loading tests: `11 passed`; combined image/reset/state tests: `28 passed`.
- `./scripts/verify` — PASS.
- `git diff --check` — PASS.
- formatting, lint и mypy — PASS.
- documentation checks — PASS.
- Full regression: `670 passed`.
- Generated artifacts отсутствуют.

## Architectural compliance

Implementation находится в `emulator/`, использует существующий atomic SRAM API и не зависит от assembler, loader, simulator, microcode или hardware. Loading не добавляет reset, fetch, execution loop, snapshots или diagnostics.

Hardware status: `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
0655304 emulator: add executable image loading
```

## Follow-up

Следующая задача — M2-007: реализовать atomic instruction fetch и post-fetch PC behavior. Push не выполняется в рамках этой задачи.
