# Локальная проверка software

## Предварительные требования

- Python `3.13.5` или совместимый Python `>=3.12,<3.14`;
- `uv` в PATH.

Проверить версии:

```bash
python3 --version
uv --version
```

Если `uv` отсутствует, установить его безопасным способом в профиль пользователя из официального installer; системные Python packages изменять не нужно.

## Установка зависимостей

Из корня repository:

```bash
uv sync --dev
```

Команда использует committed `pyproject.toml` и `uv.lock`.

## Проверки

Полная проверка:

```bash
./scripts/verify
```

Отдельные проверки:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
./scripts/check-docs
git diff --check
```

Scripts не выполняют commit, push или hardware actions и не изменяют исходные files.

## Границы test layers

В Milestone 0 проверяются только package metadata, deterministic test runner, repository layout, обязательные документы, ADR index/numbering и Markdown links. ISA, CPU components, emulator, simulator, assembler, loader и hardware behavior не тестируются, потому что ещё не реализованы.

Будущие software tests должны быть отделены от simulation tests. Ни один software или simulation test не является hardware `PASS`.

Hardware verification использует только `NOT_TESTED`, `PASS`, `FAIL`, `BLOCKED`; на этом milestone статус остаётся `NOT_TESTED`.
