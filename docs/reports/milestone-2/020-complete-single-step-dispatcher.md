# Task M2-020: Assemble the Complete Atomic Step Dispatcher

## Summary

Собран и проверен единый canonical public execution path `ArchitecturalState.step(...)`. Для не остановленного состояния он выполняет halted guard, current-SRAM fetch, decode через существующий fetch boundary и dispatch через существующий `execute_instruction()`. Для остановленного состояния он возвращает `None` без fetch, повторного diagnostic или architectural mutation.

## Sources

Работа сверена с `AGENTS.md`, `README.md`, `docs/architecture.md`, `docs/isa.md`, `docs/testing/software.md`, планом Milestone 2, index reports, M2-002, reports M2-003 through M2-019, ADR-0010, существующими `ArchitecturalState`, `fetch_instruction()`, `execute_instruction()`, `ExecutionPolicy`, diagnostic types, snapshots, reset/halted behavior и emulator test conventions.

## Scope

В scope входят consolidation existing `step()` boundary, complete opcode dispatch через existing execution handlers, policy input, diagnostic propagation, halted guard и integration verification. Final `StepResult`, bounded execution, run loop, traces, cycles, microsteps, control words и hardware integration не входят в эту задачу.

## Design decision

`ArchitecturalState.step(*, policy: ExecutionPolicy | None) -> Diagnostic | None` остаётся единственным public atomic execution path:

```text
halted guard
-> fetch_instruction()
-> decode внутри fetch boundary
-> execute_instruction(instruction, policy=policy)
-> Diagnostic | None
```

`fetch_instruction()` и `execute_instruction()` остаются lower-level APIs для unit tests и direct-composition verification. `step()` не содержит второй opcode dispatcher и не кэширует instruction stream.

### Halted guard

При `HALT_STATE` `step()` немедленно возвращает `None`. PC, IR, A, FLAGS, `flags_defined_mask`, SRAM и HALT state не изменяются; diagnostic от предыдущего reserved opcode не повторяется. `reset()` очищает HALT и сохраняет SRAM, после чего execution снова начинается с PC `0x000`.

### Opcode dispatch

Единый `execute_instruction()` обрабатывает все sixteen opcode values:

```text
0x0 NOP   0x1 LDI   0x2 LDA   0x3 ADD   0x4 SUB   0x5 STA
0x6 JMP   0x7 JC    0x8 JZ    0x9 JN    0xA JV
0xB..0xE reserved-opcode halt
0xF HLT
```

Для valid `DecodedInstruction` generic unsupported-opcode branch недостижим. Defensive `ValueError` остаётся только для impossible internal opcode state.

### Policy and diagnostics

`JC` и `JV` получают policy только через вызов `step()`. При отсутствии policy existing deterministic `TypeError` возникает после fetch и до branch mutation. `STRICT` возвращает `UNDEFINED_CONDITIONAL_FLAG` с severity `ERROR` и сохраняет post-fetch PC; `HARDWARE_LIKE` возвращает тот же diagnostic с severity `WARNING` и использует concrete C/O value. Reserved opcode возвращает `ILLEGAL_OPCODE` `ERROR`; HLT и normal instructions возвращают `None`.

Policy не сохраняется в architectural state или snapshot, а diagnostics не являются state.

### Atomic observation boundary

Между fetch и execute нет callbacks или public hooks. External observer получает только state до вызова и state/diagnostic после завершения `step()`. Existing handlers сохраняют утверждённые FLAGS, memory, branch, HLT и reset semantics.

## Changes

- `emulator/state.py` — явно закреплён canonical `step()` composition и уточнены execution-boundary docstrings; opcode semantics не продублированы.
- `tests/test_emulator_step.py` — all-opcode dispatch, diagnostics, policy, halted guard, boundary fetch, self-modifying SRAM, reset/resume и direct-composition equivalence.
- `docs/reports/milestone-2/020-complete-single-step-dispatcher.md` — этот report.
- `docs/reports/milestone-2/README.md` — M2-020 marked `COMPLETED` с canonical report link.

Source-of-truth documents, ISA, architecture, ADR и milestone plan не изменялись.

## Tests

Проверены через public `step()`:

- все 16 opcode `0x0..0xF`, включая каждый reserved opcode;
- HLT и reserved halted guard с повторными calls без fetch, mutation или diagnostic;
- normal diagnostic propagation;
- `STRICT` и `HARDWARE_LIKE` undefined JC/JV paths;
- explicit policy requirement для JC/JV;
- defined JC/JV paths;
- fetch через `0xFFE` и `0xFFF`;
- self-modifying STA и fetch текущих SRAM bytes;
- reset/resume с сохранением SRAM;
- direct `fetch_instruction()` + `execute_instruction()` equivalence для representative instructions.

Targeted M2-020 tests: `41 passed`.

## Verification

- `./scripts/verify` — PASS.
- `./scripts/check-docs` — PASS.
- `git diff --check` — PASS.
- Formatting, lint и mypy выполняются через `./scripts/verify`.
- Generated artifacts отсутствуют.
- Hardware status: `NOT_TESTED`.

## Architectural compliance

Изменения остаются в `emulator/` и `tests/`. Не добавлены ISA instructions, opcode, registers, memory/reset semantics, result abstraction, run loop, bounded execution, simulator, microcode, control words, DATA BUS, clock, assembler, loader или hardware coupling. M2-021 сохраняет ownership final `StepResult` boundary.

## Commit

Atomic commit:

```text
6463946 emulator: add atomic ISA step execution
```

## Result

`COMPLETED`

## Follow-up

Следующая задача — M2-021: добавить structured step result. Push этой задачи не выполняется; Phase E push checkpoint остаётся после M2-022.
