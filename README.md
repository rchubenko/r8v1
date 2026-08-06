# R8 v1: архитектурный пакет

Этот пакет содержит утверждённую архитектурную основу проекта R8 v1.

## Цель

R8 v1 — автономный 8-битный TTL CPU с unified 4 KB SRAM, assembler, Raspberry Pi loader и демонстрационными программами. Component models Milestone 1 реализованы; полный CPU ещё не собран.

## Источники истины

Приоритет источников определён в `AGENTS.md`. Утверждённые архитектурные документы:

- `docs/architecture.md`
- `docs/isa.md`
- `docs/microarchitecture.md`
- `docs/control-word.md`
- `docs/memory.md`
- `docs/adr/README.md` и перечисленные там ADR

## Карта monorepo

- [`specs/`](specs/README.md) — будущие машиночитаемые definitions.
- [`cpu/`](cpu/README.md) — component models Milestone 1.
- [`emulator/`](emulator/README.md) — будущий эталонный ISA emulator.
- [`simulator/`](simulator/README.md) — будущий simulator, управляемый control word.
- [`assembler/`](assembler/README.md) — будущий assembler.
- [`microcode/`](microcode/README.md) — будущие definitions и generated artifacts.
- [`loader/`](loader/README.md) — будущий image/loader tooling.
- [`hardware/`](hardware/README.md) — будущая hardware integration.
- [`programs/`](programs/README.md) — будущие программы.
- [`tests/`](tests/test_foundation.py) — foundation, component unit tests и component-level integration tests.
- [`scripts/`](scripts/README.md) — воспроизводимые проверки репозитория.
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

Milestone 0 — Repository Foundation и Milestone 1 — Component Models завершены. Реализация CPU execution, ISA emulator, simulator микроархитектуры, assembler и loader не начата. Статус аппаратной проверки: `NOT_TESTED`.

## Управление проектом

- [`AGENTS.md`](AGENTS.md) — общие правила репозитория.
- [`docs/repository-structure.md`](docs/repository-structure.md) — утверждённая структура monorepo.
- [`docs/adr/README.md`](docs/adr/README.md) — индекс активных ADR.
- [`docs/testing/software.md`](docs/testing/software.md) — локальная проверка software.
- [`docs/plans/milestone-0-repository-foundation.md`](docs/plans/milestone-0-repository-foundation.md) — план Milestone 0.
- [`docs/reports/milestone-0-readiness-review.md`](docs/reports/milestone-0-readiness-review.md) — проверка готовности.
- [`docs/plans/milestone-1-component-models.md`](docs/plans/milestone-1-component-models.md) — план Milestone 1.
- [`docs/reports/milestone-1/README.md`](docs/reports/milestone-1/README.md) — индекс отчётов Milestone 1.
- [`docs/reports/milestone-1/000-final-report.md`](docs/reports/milestone-1/000-final-report.md) — итоговый отчёт Milestone 1.
