# Milestone 0: Repository Foundation

## Цель и результат

Создать stable и reproducible monorepo foundation, которая enforces approved R8 v1 architecture до CPU, emulator, simulator, assembler, loader или hardware implementation.

К завершению active documents и ADR согласованы, governance присутствует, skeleton создан, deterministic build/test harness работает из clean checkout, architecture checks имеют entry points, CPU behavior не реализован, а `main` готов к Milestone 1 component models.

## Источники и scope

Источники: `AGENTS.md`, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/memory.md` и accepted ADR из `docs/adr/README.md`.

Scope: approved normative clarifications, ADR index/ADR-0010, root governance, monorepo skeleton, language/build manifest, minimal test framework, reproducible scripts, documentation и architecture consistency checks.

Non-goals: CPU component behavior, ISA execution, control-word classes, generated microcode, microarchitecture simulation, assembler, Raspberry Pi GPIO, SRAM loader, schematics, OpenCode commands/subagents/complex automation, CI beyond local baseline и compiler.

## Последовательные задачи

### Task 0.1 — Architecture baseline

Проверить `flags_defined_mask`, undefined-flag modes, `HIGH_Z`, producer/consumer invariant, canonical HALT, PC boundary, exact 4096-byte image, software SRAM initialization и active ADR index. Не выбирать новые behavior и не менять ISA, registers, control word, microsequences, reset, clock или ownership.

Acceptance: ровно один active ADR-0005, ADR-0010 accepted/indexed, ISA/microarchitecture/control-word/memory/architecture согласованы, links исправны. Checks: duplicate ADR scan, `FLAGS_LOAD` review, heading/link check и manual normative review.

### Task 0.2 — Repository governance

Закрепить sources-of-truth order, no-guessing policy, development sequence, stable `main`, hardware statuses, test-layer separation, generated-artifact policy, documentation, review и commit requirements. OpenCode commands, merge automation и CI не добавлять.

Acceptance: root `AGENTS.md` требует `NOT_TESTED`, `PASS`, `FAIL`, `BLOCKED`, запрещает inferred hardware `PASS`, требует specification -> software -> tests -> hardware -> regression -> documentation и complete software CPU до hardware integration. Проверка — policy checklist.

### Task 0.3 — Monorepo skeleton

Создать approved package boundaries и только нужные package markers, root README, `.gitignore` и один manifest. Не создавать `compiler/`, placeholder production classes, speculative APIs или generated binaries.

Acceptance: approved top-level boundaries существуют, package discovery/import smoke test проходит, structure соответствует `docs/repository-structure.md`, manual setup документирован. Проверки: layout, import smoke test, `git diff --check`, clean-tree check.

### Task 0.4 — Software toolchain

Закрепить supported Python version, `pyproject.toml`, `uv`, lockfile, Ruff, mypy и pytest. Runtime dependencies не добавлять без необходимости.

Acceptance: clean install из manifest/lock, formatter/static/test checks проходят, ошибки дают non-zero exit code, глобальные undeclared dependencies не нужны. Проверки: version report, install и intentional failure propagation.

### Task 0.5 — Deterministic test harness

Добавить только package metadata, deterministic runner, layout, required-document, ADR и Markdown-link tests. ISA/CPU behavior tests не добавлять.

Acceptance: repeated runs одинаковы, clean checkout проходит, test failure имеет non-zero exit code.

### Task 0.6 — Reproducible scripts

Создать `scripts/verify` и `scripts/check-docs`. `verify` запускает Ruff format, Ruff lint, mypy, pytest, docs checks и `git diff --check`. Scripts не изменяют source, не commit/push и не выполняют hardware actions. `scripts/generate` не создаётся до появления generated artifacts.

### Task 0.7 — Architecture consistency gates

Механически проверять required files, unique ADR numbers, index completeness, reserved opcode range, control-word width/reserved bit, memory/image constants и independent `FLAGS_LOAD`. Разрешать `FLAGS_LOAD_INTERNAL` и explicit negative statements. Не заменять human review natural-language theorem checker.

Acceptance: duplicated ADR, missing index entry и invalid machine-checkable constants fail с file locations; approved baseline passes. Нужны positive/negative deterministic fixtures.

### Task 0.8 — Documentation и clean checkout

Обновить README, `docs/testing/software.md`, command map, prerequisites, generated-artifact policy и clean-checkout instructions. Проверить links, `git diff --check`, clean-tree и отсутствие overstated hardware claims.

### Task 0.9 — Final regression

Проверить полный diff, architecture consistency, docs, generated artifacts, scope и clean checkout. Добавить `docs/milestones/milestone-0-report.md` с exact verification performed. Не начинать Milestone 1 и physical testing.

Acceptance: `scripts/verify` проходит, CPU/emulator/simulator/assembler/loader behavior отсутствует, hardware status `NOT_TESTED`, `main` stable.

### Task 0.10 — Stable `main`

После полного review merge feature branch в stable `main`, повторно выполнить verification и только затем push. Tag до завершения merge и verification не создавать; optional tag — `v1-m0-foundation`.

## Atomic commits

```text
docs: translate project documentation to Russian
docs: establish R8 v1 architecture baseline
build: create monorepo skeleton
build: configure Python development toolchain
test: add repository foundation checks
scripts: add reproducible verification commands
docs: document local software verification
```

Commits можно объединять только если resulting commit cohesive, independently verifiable и легко revertible. Перед каждым commit: relevant tests, complete diff review, docs sync, generated-artifact check, no unrelated files и `git diff --check`.

## Milestone exit gate

```text
architecture baseline consistent
AGENTS.md approved
monorepo structure present
foundation tests pass
architecture gates pass
hardware status = NOT_TESTED
main stable
```

OpenCode workflow commands остаются deferred до повторяющейся repository work.
