# Структура monorepo R8 v1

## Статус

Утверждённое предложение по foundation для Milestone 0.

## Цели

Структура должна разделять architectural reference behavior и microarchitectural execution, иметь canonical sources для ISA, control-word и microcode, поддерживать deterministic tests, изолировать hardware-facing code, обеспечивать reproducible generated artifacts и не включать future compiler в R8 v1.

## Области

```text
specs/       machine-readable definitions
cpu/         component models и state containers
emulator/    atomic ISA reference emulator
simulator/   control-word-driven microarchitecture simulator
assembler/   parser, symbols, encoder, CLI
microcode/   definitions, validator, generator, generated artifacts
loader/      image и ownership protocols
hardware/    adapters, drivers, bring-up, tests, reports, BOM, schematics
programs/    examples, diagnostics, expected results
tests/       unit, isa, control_word, microcode, microarchitecture, parity,
             assembler, loader, integration, fixtures
scripts/     minimal reproducible checks
docs/        architecture, ADR, plans, milestones, testing, reports
```

Milestone 0 создаёт только действительно нужные package boundaries и markers. Generated binaries и `.gitkeep` не добавляются. `compiler/` implementation directory не создаётся.

## Ответственность

`specs/` — canonical machine-readable inputs, не добавляющие semantics вне Markdown. `cpu/` — reusable component models без instruction decoder и complete CPU loop. `emulator/` — atomic architectural behavior без microsteps. `simulator/` — real control words, buses, microsteps и rising-edge transitions; он не вызывает atomic emulator.

`assembler/` позднее должен выдавать exact 4096-byte image и reject overflow. `microcode/` содержит declarative sequences и reproducible generated outputs; generated files вручную не редактируются. `loader/` разделяет image handling и ownership; `hardware/` содержит physical adapters, где `PASS` возможен только после explicit user confirmation.

`tests/` разделяет test layers. `scripts/` содержит обычные local entry points; OpenCode workflow commands отложены.
