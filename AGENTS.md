# Правила проекта R8 v1

## 1. Scope

R8 v1 — autonomous 8-bit TTL CPU с unified 4 KB SRAM, assembler, loader и demonstration programs. Raspberry Pi может быть loader, test bench, debugger, state monitor и temporary microcode driver, но в final autonomous CPU не формирует control signals.

R8-Lang compiler, stack, CALL/RET, PUSH/POP, interrupts, logical ALU operations, user peripherals и CPU-resident monitor вне scope R8 v1 без отдельной architecture version.

## 2. Источники истины

Порядок приоритета:

1. accepted ADRs из `docs/adr/README.md`;
2. `docs/architecture.md` и `docs/isa.md`;
3. `docs/microarchitecture.md`, `docs/control-word.md`, `docs/memory.md`;
4. machine-readable specifications и generated microcode;
5. software implementations;
6. hardware implementations;
7. tests и reports.

Нижний уровень не может молча переопределять верхний. Replacing ADR обязан указать superseded ADR; conflicting ADR не могут одновременно быть active. При conflict или insufficient behavior: остановить затронутую работу, сообщить gap, указать components/tests, предложить варианты и не выбирать architecture decision самостоятельно.

## 3. Запрет предположений

Нельзя изобретать ISA encoding/semantics, flags, registers, memory model, address path, control word, microsteps, reset, HALT, clock, SRAM ownership или loader image format. Implementation details допустимы только без изменения observable behavior и должны быть зафиксированы в plan/design documentation.

Architecture changes для opcode/semantics, flags, registers, memory/image, control word, microsteps, reset, HALT, clock или ownership требуют explicit task, ADR/normative update, updates всех specs, tests и approval.

## 4. Development order

```text
specification -> software -> tests -> hardware -> regression -> documentation
```

Hardware status software-only milestones — `NOT_TESTED`. Complete software CPU обязателен до hardware integration: component models, ISA reference emulator, control-word model/generated microcode, microarchitecture simulator, parity, assembler, programs. ISA emulator atomic; simulator derives behavior из real control words, buses, microsteps и rising-edge transitions и не вызывает atomic implementations.

## 5. Git и main

`main` stable. В main попадают только complete approved changes с passing checks, current docs/generated artifacts, accurate hardware status, no unrelated diff и clean tree. Один feature/milestone branch на coherent work, commits atomic. Не смешивать specification, tooling, scripts и documentation без причины. Tags — только completed milestones. Verified commits push в configured remote.

## 6. Hardware statuses

Использовать ровно эти статусы:

- `NOT_TESTED` — physical test не выполнялся;
- `PASS` — user физически выполнил test и подтвердил expected result;
- `FAIL` — user физически выполнил test и сообщил incorrect result;
- `BLOCKED` — physical test невозможен из-за отсутствующего или неисправного prerequisite.

Agent никогда не может выводить hardware `PASS` из simulation, compilation, static analysis, expected behavior, photographs, previous versions или inference. Только explicit user confirmation даёт `PASS`.

## 7. Test layers

Разделять component unit, ISA conformance, control-word validation, microcode generation, microarchitecture microstep, emulator/simulator parity, assembler, loader, hardware component, hardware subsystem и full CPU regression tests. Higher-level simulation не заменяет lower-level physical test. Tests deterministic и reproducible из repository commands. Parity сравнивает `flags_defined_mask` и values только defined flags; strict undefined-flag diagnostics и hardware-like mode проверяются отдельно.

## 8. Invalid states

Models, validators и drivers должны reject/detect multiple DATA BUS producers, consumer без ровно одного producer, reserved encodings, `RAM_WE` без valid producer, invalid PC operation, HALT с write actions, non-canonical HALT, microcode beyond T15, simultaneous CPU/Pi ownership и reserved opcode без HALT. One producer без consumer разрешён для bring-up/debugging.

## 9. Generated artifacts и docs

Generated microcode, EEPROM images, opcode tables, listings и другие derived files имеют один canonical source, вручную не редактируются, generation deterministic. Verification обязан обнаруживать stale artifacts. Документация различает approved architecture, proposed decisions, software verification, physical verification и deferred work; simulated hardware не описывается как physical `PASS`.

## 10. Planning, review и commits

Перед implementation plan должен содержать goal, sources, scope, non-goals, modules, blockers, acceptance criteria, tests, documentation и atomic commits. При unresolved architecture decision затронутая implementation останавливается.

Review проверяет consistency с ADR/specs, accidental architecture changes, deterministic behavior, bus/control validity, test adequacy, parity, generated artifacts, docs, hardware status, unrelated changes и repository cleanliness. Перед commit: relevant verification, complete diff review, docs sync, generated-artifact check, no overstated hardware result, no unrelated files. Commit messages concise и imperative с prefixes `spec:`, `model:`, `emulator:`, `sim:`, `microcode:`, `assembler:`, `loader:`, `hardware:`, `test:`, `docs:`, `build:`.

OpenCode workflow commands намеренно deferred до повторяющейся repository work.
