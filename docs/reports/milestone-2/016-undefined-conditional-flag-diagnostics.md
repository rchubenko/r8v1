# Task M2-016: Implement Undefined Conditional Flag Diagnostics

## Summary

Добавлен execution-environment boundary для чтения architecturally undefined conditional flags. Реализованы typed `STRICT` и `HARDWARE_LIKE` policies, immutable diagnostics и deterministic flag resolution без изменения architectural state.

## Sources

Работа сверена с [`AGENTS.md`](../../../AGENTS.md), [README проекта](../../../README.md), [архитектурой](../../architecture.md), [ISA](../../isa.md), [software testing policy](../../testing/software.md), [планом Milestone 2](../../plans/milestone-2-isa-reference-emulator.md), [execution contract M2-002](002-emulator-execution-contract.md), reports M2-003 through M2-015, [ADR-0005](../../adr/0005-flags-update-on-a-write.md), [ADR-0010](../../adr/0010-deterministic-software-model-semantics.md), existing FLAGS/mask/snapshot APIs и emulator test conventions.

## Scope

В scope входят только execution policy representation, immutable diagnostic representation и reusable conditional flag resolution. JC/JV branch mutation, dispatcher, execution result aggregation и hardware execution не реализуются.

## Design decision

`emulator.policy` содержит:

- `ExecutionPolicy.STRICT`;
- `ExecutionPolicy.HARDWARE_LIKE`;
- typed `DiagnosticIdentifier` и `DiagnosticSeverity`;
- immutable `Diagnostic`;
- immutable `ConditionalFlagResolution`;
- `resolve_conditional_flag(flag, flags, policy)`.

Resolution возвращает concrete flag value, `branch_allowed` и optional diagnostic, но не изменяет PC или другой architectural state.

## Policy behavior

- Defined flag: обе policies используют concrete value и возвращают no diagnostic.
- Undefined flag under `STRICT`: branch запрещён, возвращается `UNDEFINED_CONDITIONAL_FLAG` с severity `ERROR`.
- Undefined flag under `HARDWARE_LIKE`: concrete value используется, branch разрешён, возвращается deterministic `WARNING` diagnostic.

Always-warning в `HARDWARE_LIKE` выбран как простая deterministic strategy для будущего execution result boundary. Warning является non-architectural observation.

Defined-mask проверяется в resolution после fetch context доступен и до будущей branch mutation. M2-016 не меняет JZ/JN и не исполняет JC/JV.

## State and snapshot boundary

Policy, diagnostics и resolution не являются частью `ArchitecturalState` или `ArchitecturalStateSnapshot`. Resolution не изменяет A, PC, IR, SRAM, concrete FLAGS, `flags_defined_mask` или HALT.

## Changes

- `emulator/policy.py` — policies, typed diagnostics и conditional flag resolution.
- `emulator/__init__.py` — public policy boundary exports.
- `tests/test_emulator_policy.py` — policy, diagnostic, defined/undefined C/O, determinism, state and snapshot exclusion tests.
- `docs/reports/milestone-2/016-undefined-conditional-flag-diagnostics.md` — этот report.
- `docs/reports/milestone-2/README.md` — статус и report link для M2-016.

Source-of-truth documents, ISA, active ADR и milestone plan не изменялись.

## Tests

Проверены:

- typed distinct policy values;
- defined flags with values 0/1 under both policies без diagnostic;
- undefined C/O with concrete values 0/1 under STRICT и ERROR diagnostic;
- undefined C/O with concrete values 0/1 under HARDWARE_LIKE и WARNING diagnostic;
- immutable typed diagnostics and repeated equal resolution;
- policy/diagnostic absence from architectural state and snapshots;
- post-fetch PC/HALT/state preservation при resolution;
- deterministic repeated HARDWARE_LIKE resolution;
- NOP, LDI, LDA, ADD, SUB, STA, JMP, JZ и JN regression; JC/JV execution оставались отдельной задачей M2-017.

## Verification

- Targeted policy and prior emulator tests: `299 passed`.
- Full regression: `988 passed`.
- `./scripts/verify` — PASS; formatting, lint и mypy — PASS.
- `./scripts/check-docs` — PASS.
- `git diff --check` — PASS.
- Generated artifacts отсутствуют.

## Architectural compliance

Implementation находится в `emulator/` и не добавляет policy в CPU state или snapshots. Не добавлены JC/JV, branch PC mutation для C/O, `UNDEFINED_CONDITIONAL_FLAG` handling в instruction execution, halt reason, dispatcher, simulator, microcode, control-word decode, assembler, loader или hardware coupling. Policy remains execution-environment configuration.

Hardware status: `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Expected atomic commit:

```text
emulator: add undefined flag execution policies
```

Push не выполняется в рамках этой задачи.

## Follow-up

Следующая задача — M2-017: реализовать JC и JV. Push не выполняется в рамках этой задачи.
