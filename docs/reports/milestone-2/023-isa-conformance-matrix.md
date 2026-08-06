# Task M2-023: Add the Complete ISA Conformance Matrix

## Summary

Добавлен отдельный test-side conformance layer для всех 16 opcode `0x0..0xF`. Matrix machine-checkable и связывает каждую `Opcode` row с category, architectural effects и boundary class. Проверки используют public `ArchitecturalState.step()` и immutable `StepResult`; production code не изменялся.

## Sources

Работа сверена с `AGENTS.md`, `README.md`, `docs/architecture.md`, `docs/isa.md`, `docs/memory.md`, `docs/testing/software.md`, планом Milestone 2, reports index, M2-002, reports M2-003 through M2-022, active ADR including ADR-0008/ADR-0010, production package `emulator/`, reusable `cpu/` contracts, existing emulator tests and verification scripts.

## Scope

В scope входят complete ISA conformance manifest, representative positive/preservation/boundary cases, PC/memory/FLAGS/diagnostic/HALT/reset/policy matrices и systematic coverage checks. Existing lower-level exhaustive ADD/SUB tests сохраняются и не дублируются полностью. Новые instruction semantics, production registries, bounded runner, simulator parity и hardware verification не добавлялись.

## Matrix design

`tests/test_isa_conformance.py` содержит frozen `ConformanceRow` и `CONFORMANCE_MATRIX` из ровно 16 rows:

```text
NOP, LDI, LDA, ADD, SUB, STA, JMP, JC,
JZ, JN, JV, RESERVED_B, RESERVED_C, RESERVED_D, RESERVED_E, HLT
```

Каждая row содержит:

- typed opcode;
- instruction category;
- explicit architectural effect labels;
- boundary class.

Test проверяет, что matrix равна `tuple(Opcode)`, не содержит duplicate rows и отдельно представляет reserved opcodes и HLT.

## Coverage

- NOP: PC/IR fetch, full preservation и fetch wrap at `0xFFE`/`0xFFF`.
- LDI: immediate low-byte extraction, representative operands, Z/S definition and C/O preservation.
- LDA: current SRAM reads at full 12-bit representative addresses and Z/S definition.
- ADD/SUB: representative arithmetic values, modulo results and exact Z/C/S/O values; exhaustive matrices remain in existing tests.
- STA: exact one-byte mutation, edge addresses, FLAGS preservation and current-memory behavior.
- JMP: full and odd targets with architectural preservation.
- JZ/JN: defined taken/not-taken behavior, target and preservation cases.
- JC/JV: defined and undefined paths under STRICT/HARDWARE_LIKE with ERROR/WARNING diagnostics.
- Reserved `0xB..0xE`: separate rows, decode, illegal-opcode diagnostic, offending opcode, HALT and halted guard.
- HLT: HALT, no diagnostic, halted guard and reset/resume with SRAM persistence.

Cross-cutting checks cover pre/post `StepResult`, PC wrap, SRAM mutation matrix, FLAGS/mask categories, diagnostic matrix, HALT matrix, reset baseline and policy exclusion from architectural observations.

Self-modifying execution and finite multi-step sequences are covered without an unbounded loop or production bounded runner. All multi-step cases use explicit finite calls to `step()`.

## Existing coverage relation

Existing modules remain the detailed unit and instruction coverage for individual handlers, including exhaustive `256 x 256` ADD/SUB tests. The new module is intentionally an overview/conformance layer: it asserts the complete opcode manifest and cross-cutting architectural contract rather than replacing or copying lower-level exhaustive coverage.

## Changes

- `tests/test_isa_conformance.py` — complete opcode manifest and ISA conformance tests.
- `docs/reports/milestone-2/023-isa-conformance-matrix.md` — этот report.
- `docs/reports/milestone-2/README.md` — M2-023 marked `COMPLETED` с report link.

Production code, ISA, architecture, ADR, execution contract, milestone plan, task numbering и phase mapping не изменялись.

## Tests

Targeted conformance suite: `125 passed`.

Coverage includes all opcode rows, public `step()`/`StepResult` contract, instruction decode, pre/post PC and IR, memory effects, FLAGS values and masks, branch paths, diagnostics, HALT, reset, boundary fetch, policy matrix, self-modifying behavior and finite halted/diagnostic sequences.

## Verification

- `./scripts/verify` — PASS.
- `./scripts/check-docs` — PASS.
- `git diff --check` — PASS.
- Formatting, lint и mypy выполняются через `./scripts/verify`.
- Generated artifacts отсутствуют.
- Hardware status: `NOT_TESTED`.

## Architectural compliance

Изменения находятся только в `tests/` и task report/index. Не добавлены production behavior, opcode, registers, memory/reset semantics, bounded runner, simulator parity, microsteps, DATA BUS, control words, cycle timing, assembler, loader или hardware coupling. `cpu/` remains reusable component layer.

## Commit

Atomic commit:

```text
b8327d1 test: add complete ISA conformance coverage
```

## Result

`COMPLETED`

## Follow-up

Следующая задача — M2-024: добавить integration programs. Push этой задачи не выполняется; Phase F final workflow остаётся отдельным.
