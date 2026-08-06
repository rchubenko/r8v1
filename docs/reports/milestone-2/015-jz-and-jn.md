# Task M2-015: Implement JZ and JN

## Summary

Добавлены atomic conditional jumps JZ и JN после fetch. JZ читает concrete Z, JN читает concrete S; taken branch загружает полный 12-bit operand в PC, false branch сохраняет post-fetch PC.

## Sources

Работа сверена с [`AGENTS.md`](../../../AGENTS.md), [README проекта](../../../README.md), [архитектурой](../../architecture.md), [ISA](../../isa.md), [микроархитектурой](../../microarchitecture.md), [Control Word](../../control-word.md), [software testing policy](../../testing/software.md), [планом Milestone 2](../../plans/milestone-2-isa-reference-emulator.md), [execution contract M2-002](002-emulator-execution-contract.md), reports M2-003 through M2-014, [ADR-0005](../../adr/0005-flags-update-on-a-write.md), [ADR-0010](../../adr/0010-deterministic-software-model-semantics.md), existing FLAGS/ProgramCounter APIs и emulator test conventions.

## Scope

В scope входят только JZ и JN execution после supplied `DecodedInstruction`, taken/not-taken PC behavior, full 12-bit targets и preservation architectural fields/FLAGS. Undefined-flag diagnostics, execution policies, JC, JV, HLT, reserved opcode halt, dispatcher и hardware execution не реализуются.

## Design decision

`ArchitecturalState.execute_instruction()` получил две отдельные ветки:

```text
JZ: if FLAGS.Z == 1: PC <- operand
JN: if FLAGS.S == 1: PC <- operand
```

Conditions читают concrete Z/S values непосредственно из текущего FLAGS snapshot. `flags_defined_mask` не проверяется и не изменяется, поскольку Z/S являются defined flags для этой задачи; diagnostics и policy branching остаются отдельной задачей M2-016.

## Branch behavior

- Taken JZ/JN загружает exact full 12-bit operand в PC.
- False JZ/JN оставляет PC в post-fetch state.
- Odd targets и target `0xFFF` разрешены.
- Дополнительный PC increment или fetch-contract change отсутствуют.

## State preservation

JZ/JN изменяют только PC при taken condition. A, IR, SRAM, concrete FLAGS, `flags_defined_mask` и HALT сохраняются в обоих случаях.

## Changes

- `emulator/state.py` — JZ/JN execution branches.
- `tests/test_emulator_jz_jn.py` — taken/not-taken, targets, masks, preservation и boundary-fetch tests.
- `tests/test_emulator_execution.py` — unsupported-opcode regression перенесён с JZ на JC.
- `tests/test_emulator_lda.py` — unsupported-opcode regression перенесён с JZ на JC.
- `docs/reports/milestone-2/015-jz-and-jn.md` — этот report.
- `docs/reports/milestone-2/README.md` — статус и report link для M2-015.

Source-of-truth documents, ISA, active ADR и milestone plan не изменялись.

## Tests

Проверены:

- JZ taken/not-taken для representative targets `0x000`, `0x001`, `0x123`, `0xABC`, `0xFFF`;
- JN taken/not-taken для тех же targets;
- full target and odd-address support;
- concrete FLAGS combinations и masks Z/S, all, Z-only, S-only без mask changes;
- A/IR/SRAM/HALT preservation;
- false and taken JZ/JN fetched через `0xFFF -> 0x000` с post-fetch PC `0x001`;
- existing NOP, LDI, LDA, ADD, SUB, STA и JMP regression, а также unsupported reserved-opcode rejection.

## Verification

- Targeted JZ/JN, execution, JMP, STA, SUB, ADD и LDA tests: `274 passed`.
- Full regression: `963 passed`.
- `./scripts/verify` — PASS; formatting, lint и mypy — PASS.
- `./scripts/check-docs` — PASS.
- `git diff --check` — PASS.
- Generated artifacts отсутствуют.

## Architectural compliance

Implementation находится в `emulator/` и переиспользует existing FLAGS/ProgramCounter APIs. Не добавлены `UNDEFINED_CONDITIONAL_FLAG`, STRICT/HARDWARE_LIKE branching, JC/JV semantics, `PC_OP` decode, MAR, DATA BUS, control-word decode, microsteps, clock, dispatcher, simulator, assembler, loader или hardware coupling. M2-016 и M2-017 были отдельными последующими задачами.

Hardware status: `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Expected atomic commit:

```text
emulator: implement JZ and JN
```

Push не выполняется в рамках этой задачи.

## Follow-up

Следующая задача — M2-016: реализовать undefined-flag diagnostics. Push не выполняется в рамках этой задачи.
