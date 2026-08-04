# R8 v1: архитектурный пакет

Этот пакет содержит утверждённую архитектурную основу проекта R8 v1.

## Цель

R8 v1 — автономный 8-битный TTL CPU с unified 4 KB SRAM, assembler, Raspberry Pi loader и демонстрационными программами. На текущем этапе CPU и его software models ещё не реализованы.

## Источники истины

Приоритет источников определён в `AGENTS.md`. Утверждённые архитектурные документы:

- `docs/architecture.md`
- `docs/isa.md`
- `docs/microarchitecture.md`
- `docs/control-word.md`
- `docs/memory.md`
- `docs/adr/README.md` и перечисленные там ADR

## Карта monorepo

- `specs/` — будущие machine-readable definitions.
- `cpu/` — будущие component models.
- `emulator/` — будущий ISA reference emulator.
- `simulator/` — будущий control-word-driven simulator.
- `assembler/` — будущий assembler.
- `microcode/` — будущие definitions и generated artifacts.
- `loader/` — будущий image/loader tooling.
- `hardware/` — будущая hardware integration.
- `programs/` — будущие программы.
- `tests/` — foundation и будущие test layers.
- `scripts/` — воспроизводимые repository checks.
- `docs/` — нормативные документы и отчёты.

`compiler/` в R8 v1 не создаётся.

## Локальная разработка

Требуется Python `3.13` или совместимый Python 3.12+. Для установки `uv` и зависимостей см. `docs/testing/software.md`.

Основная проверка:

```bash
uv sync --dev
./scripts/verify
```

## Статус

Текущая работа относится к Milestone 0 — Repository Foundation. Реализация CPU, ISA emulator, microarchitecture simulator, assembler и loader не начата. Hardware status: `NOT_TESTED`.

## Управление проектом

- `AGENTS.md` — repository-wide policy.
- `docs/repository-structure.md` — утверждённая структура monorepo.
- `docs/plans/milestone-0-repository-foundation.md` — план Milestone 0.
- `docs/reports/milestone-0-readiness-review.md` — readiness review.
