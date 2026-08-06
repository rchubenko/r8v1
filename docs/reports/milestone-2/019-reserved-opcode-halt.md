# Task M2-019: Halt on Reserved Opcodes

## Summary

Реализовано execution reserved opcodes `0xB..0xE`: каждый fetched reserved instruction latch-ит HALT, сохраняет architectural state и возвращает immutable `ILLEGAL_OPCODE` diagnostic с фактически fetched `Opcode`.

## Sources

Работа сверена с [`AGENTS.md`](../../../AGENTS.md), [README проекта](../../../README.md), [архитектурой](../../architecture.md), [ISA](../../isa.md), [software testing policy](../../testing/software.md), [планом Milestone 2](../../plans/milestone-2-isa-reference-emulator.md), [execution contract M2-002](002-emulator-execution-contract.md), reports M2-003 through M2-018, [ADR-0008](../../adr/0008-reserved-opcodes.md), [ADR-0010](../../adr/0010-deterministic-software-model-semantics.md), existing `Opcode`/`DecodedInstruction`, `HaltLatch`, diagnostic APIs, fetch/reset/step boundaries и emulator test conventions.

## Scope

В scope входят reserved opcode execution, illegal-opcode halt, IR-derived diagnostic classification, policy independence, halted-step behavior и reset interaction. New ISA semantics, halt-reason register, control-word behavior, edge timing и hardware execution не реализуются.

## Design decision

`DiagnosticIdentifier.ILLEGAL_OPCODE` добавлен в existing diagnostic boundary. `Diagnostic` получил optional typed `opcode: Opcode | None` payload, сохраняя compatibility для existing diagnostics. Reserved `RESERVED_B`, `RESERVED_C`, `RESERVED_D` и `RESERVED_E`:

```text
HALT_STATE <- True
return Diagnostic(ILLEGAL_OPCODE, ERROR, fetched_opcode)
```

Diagnostic создаётся из supplied fetched `DecodedInstruction`; persistent diagnostic state отсутствует.

## Architectural behavior

Reserved opcode behavior эквивалентен HLT для A, post-fetch PC, IR, SRAM, concrete FLAGS, `flags_defined_mask` и HALT, с единственным non-architectural отличием: HLT возвращает `None`, reserved opcode возвращает `ILLEGAL_OPCODE` ERROR. Policy input не влияет на результат.

Halted `step()` calls возвращают `None`, не выполняют fetch и не повторяют diagnostic. Reset очищает HALT, не сохраняет diagnostic и разрешает execution resume при сохранении SRAM.

## Changes

- `emulator/policy.py` — `ILLEGAL_OPCODE` identifier и typed offending opcode diagnostic payload.
- `emulator/state.py` — four reserved-opcode halt branches returning ERROR diagnostic.
- `tests/test_emulator_reserved_opcode.py` — all opcode/operand, preservation, HLT comparison, policy, reset, halted-step and boundary tests.
- `tests/test_emulator_execution.py` — removed obsolete generic unsupported-reserved assertion.
- `tests/test_emulator_lda.py` — removed obsolete generic unsupported-reserved assertion.
- `docs/reports/milestone-2/019-reserved-opcode-halt.md` — этот report.
- `docs/reports/milestone-2/README.md` — статус и report link для M2-019.
- Reports M2-013..M2-018 — stale generic unsupported descriptions synchronized with reserved-opcode halt behavior.

Source-of-truth documents, ISA, active ADR и milestone plan не изменялись.

## Tests

Проверены:

- all four reserved opcodes separately with operands `0x000`, `0x001`, `0xABC`, `0xFFF`;
- fetched opcode distinction in `ILLEGAL_OPCODE` diagnostic;
- ERROR severity, immutable diagnostic and repeated equality;
- architectural preservation and HLT equivalence;
- no repeated diagnostic/fetch during halted steps;
- reset clears HALT, preserves SRAM and resumes valid instruction execution;
- boundary fetch `0xFFF -> 0x000`;
- policy-independent behavior without halt-reason state;
- NOP, LDI, LDA, ADD, SUB, STA, JMP, JZ, JN, JC, JV and HLT regression.

## Verification

- Targeted reserved-opcode and prior emulator tests: `379 passed`.
- Full regression: `1068 passed`.
- `./scripts/verify` — PASS; formatting, lint и mypy — PASS.
- `./scripts/check-docs` — PASS.
- `git diff --check` — PASS.
- Generated artifacts отсутствуют.

## Architectural compliance

Implementation находится в `emulator/` и переиспользует existing `HaltLatch`, fetched `DecodedInstruction`, diagnostic boundary и halted `step()`. Не добавлены architectural halt reason, opcode reassignment, new reserved semantics, control-word/EEPROM entries, microsteps, timing, simulator, dispatcher, assembler, loader или hardware coupling.

Hardware status: `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Expected atomic commit:

```text
emulator: halt on reserved opcodes
```

Push не выполняется в рамках этой задачи.

## Follow-up

Следующая задача — M2-020: реализовать instruction dispatcher. Push не выполняется в рамках этой задачи.
