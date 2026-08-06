# Task M2-017: Implement JC and JV

## Summary

Добавлены atomic JC и JV после fetch. Обе инструкции получают execution policy через keyword-only execution-environment input, используют reusable conditional flag resolution и возвращают non-architectural `Diagnostic | None` без расширения architectural state.

## Sources

Работа сверена с [`AGENTS.md`](../../../AGENTS.md), [README проекта](../../../README.md), [архитектурой](../../architecture.md), [ISA](../../isa.md), [микроархитектурой](../../microarchitecture.md), [Control Word](../../control-word.md), [software testing policy](../../testing/software.md), [планом Milestone 2](../../plans/milestone-2-isa-reference-emulator.md), [execution contract M2-002](002-emulator-execution-contract.md), reports M2-003 through M2-016, [ADR-0005](../../adr/0005-flags-update-on-a-write.md), [ADR-0010](../../adr/0010-deterministic-software-model-semantics.md), existing `ExecutionPolicy`, `resolve_conditional_flag()`, FLAGS/ProgramCounter APIs и emulator test conventions.

## Scope

В scope входят только JC/JV execution, policy input, minimal diagnostic return extension и defined/undefined C/O branch behavior. HLT, reserved opcode halt, dispatcher, complete step result, JC/JV microarchitecture и hardware execution не реализуются.

## Design decision

`ArchitecturalState.execute_instruction()` получил keyword-only параметр:

```python
execute_instruction(
    instruction: DecodedInstruction,
    *,
    policy: ExecutionPolicy | None = None,
) -> Diagnostic | None
```

Existing instructions сохраняют `None` return behavior. JC/JV требуют explicit policy, вызывают `resolve_conditional_flag()` для C/O и применяют PC mutation только если resolution разрешает branch и concrete value равен `True`.

## Branch behavior

- Defined C/O: обе policies одинаково branch по concrete value и возвращают `None` diagnostic.
- Undefined C/O under `STRICT`: resolution возвращает ERROR `UNDEFINED_CONDITIONAL_FLAG`; branch не выполняется, PC остаётся post-fetch.
- Undefined C/O under `HARDWARE_LIKE`: resolution использует concrete value и WARNING; true condition загружает target, false condition сохраняет post-fetch PC.
- Full 12-bit и odd targets поддерживаются; fetch ordering не изменён.

## State and snapshot boundary

JC/JV изменяют только PC на taken branch. A, IR, SRAM, concrete FLAGS, `flags_defined_mask` и HALT сохраняются. Policy и diagnostic не являются полями `ArchitecturalState` или `ArchitecturalStateSnapshot`.

## Changes

- `emulator/state.py` — policy-aware JC/JV execution and `Diagnostic | None` return boundary.
- `tests/test_emulator_jc_jv.py` — defined/undefined policy paths, integrations, targets, boundary fetch and preservation tests.
- `tests/test_emulator_execution.py` — unsupported-opcode regression перенесён на HLT.
- `tests/test_emulator_lda.py` — unsupported-opcode regression перенесён на HLT.
- `docs/reports/milestone-2/017-jc-and-jv.md` — этот report.
- `docs/reports/milestone-2/README.md` — статус и report link для M2-017.
- Reports M2-013..M2-016 — stale unsupported-fixture descriptions synchronized with current supported scope.

Source-of-truth documents, ISA, active ADR и milestone plan не изменялись.

## Tests

Проверены:

- defined JC/JV under both policies for C/O values 0/1;
- undefined C/O under STRICT with concrete values 0/1, ERROR diagnostic and no branch;
- undefined C/O under HARDWARE_LIKE with concrete values 0/1, WARNING diagnostic and concrete branch decision;
- LDI/LDA integration preserving Z/S-only mask and undefined C/O;
- ADD/SUB integration with defined C/O and no diagnostic under either policy;
- full 12-bit and odd targets;
- boundary fetch `0xFFF -> 0x000` for strict and hardware-like paths;
- A/IR/SRAM/FLAGS/mask/HALT preservation;
- explicit policy requirement and existing-instruction `None` compatibility;
- policy/snapshot exclusion and JC/JV regression with HLT and reserved opcodes still unsupported.

## Verification

- Targeted JC/JV, policy, JZ/JN, JMP, STA, SUB, ADD и LDA tests: `339 passed`.
- Full regression: `1028 passed`.
- `./scripts/verify` — PASS; formatting, lint и mypy — PASS.
- `./scripts/check-docs` — PASS.
- `git diff --check` — PASS.
- Generated artifacts отсутствуют.

## Architectural compliance

Implementation находится в `emulator/` и переиспользует `resolve_conditional_flag()`, `ExecutionPolicy`, typed diagnostics и `ProgramCounter`. Не добавлены EEPROM branch logic, external combinational branch logic, JC/JV state fields, `PC_OP` decode, MAR, DATA BUS, control-word decode, microsteps, clock, dispatcher, simulator, assembler, loader или hardware coupling. HLT и reserved opcode halt остаются отдельными задачами.

Hardware status: `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Expected atomic commit:

```text
emulator: implement JC and JV
```

Push не выполняется в рамках этой задачи.

## Follow-up

Следующая задача — M2-018: реализовать HLT. Push не выполняется в рамках этой задачи.
