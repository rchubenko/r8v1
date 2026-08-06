# Task M2-021: Add Deterministic Step Results

## Summary

`ArchitecturalState.step()` теперь всегда возвращает immutable `StepResult`. Result содержит fetched instruction, pre-step snapshot, post-step snapshot и optional diagnostic. Уже установленный HALT представлен явно через `instruction=None`, без fake instruction или повторного diagnostic.

## Sources

Работа сверена с `AGENTS.md`, `README.md`, `docs/architecture.md`, `docs/isa.md`, `docs/testing/software.md`, планом Milestone 2, index reports, M2-002, reports M2-003 through M2-020, ADR-0010, existing `ArchitecturalState`, `ArchitecturalStateSnapshot`, `step()`, `fetch_instruction()`, `execute_instruction()`, `DecodedInstruction`, diagnostic types и emulator test conventions.

## Scope

В scope входят immutable deterministic result boundary, pre/post architectural observations, explicit halted-step representation, optional full memory capture, diagnostic propagation и conformance-oriented tests. Cycle timing, traces, run loop, bounded execution, simulator state, serialization и hardware integration не входят в задачу.

## Design decision

Добавлен frozen slots dataclass:

```python
StepResult(
    instruction: DecodedInstruction | None,
    pre_state: ArchitecturalStateSnapshot,
    post_state: ArchitecturalStateSnapshot,
    diagnostic: Diagnostic | None,
)
```

`StepResult` экспортируется из `emulator`. Все поля typed и immutable; `DecodedInstruction`, `ArchitecturalStateSnapshot`, `Diagnostic` и captured memory являются detached value observations.

Canonical sequence:

```text
capture pre-state
-> halted guard
-> fetch/decode
-> execute
-> capture post-state
-> StepResult
```

При уже установленном HALT `step()` возвращает `StepResult(None, pre_state, pre_state, None)`. Для normal instruction, HLT, reserved opcode и diagnostic branch return type одинаков.

### Memory observation

`step(include_memory=False)` использует lightweight snapshots без full SRAM copy. При `include_memory=True` pre/post snapshots содержат detached immutable `bytes` image. Existing `ArchitecturalStateSnapshot` переиспользуется; новый snapshot type не создан.

### Policy and diagnostics

Policy передаётся в `step()` и не является полем `StepResult`. Diagnostic находится только в result и не попадает в architectural state или snapshots. Existing STRICT/HARDWARE_LIKE behavior, HLT и reserved-opcode diagnostics сохранены.

`fetch_instruction()` и `execute_instruction()` продолжают возвращать свои lower-level values. `step()` только композирует их и строит result, не дублируя instruction semantics.

## Changes

- `emulator/result.py` — immutable `StepResult` value type с runtime type validation.
- `emulator/state.py` — unified `StepResult` return, pre/post snapshot capture и `include_memory` option.
- `emulator/__init__.py` — public `StepResult` export.
- `tests/test_emulator_result.py` — result type, normal/branch/diagnostic/HLT/reserved cases, memory capture, determinism и detachment.
- `tests/test_emulator_step.py` — adaptation of M2-020 integration assertions to unified result contract.
- `tests/test_emulator_hlt.py` и `tests/test_emulator_reserved_opcode.py` — adaptation to `.diagnostic` result observation.
- `docs/reports/milestone-2/021-deterministic-step-result.md` — этот report.
- `docs/reports/milestone-2/README.md` — M2-021 marked `COMPLETED` с report link.

Source-of-truth documents, ISA, architecture, ADR и milestone plan не изменялись.

## Tests

Проверены:

- immutability, typed fields, equality и deterministic value behavior;
- NOP pre/post result;
- LDI, LDA, ADD, SUB и STA architectural changes;
- JMP, JZ, JN, JC и JV branch results;
- STRICT ERROR и HARDWARE_LIKE WARNING results;
- HLT и reserved-opcode results;
- already halted result с `instruction=None` и equal pre/post states;
- boundary fetch и existing all-opcode regression;
- lightweight и explicit full-memory snapshots;
- self-modifying SRAM behavior через previous step tests;
- reset/resume и old-result detachment;
- independent equal states producing equal results;
- policy отсутствует в result и snapshots; diagnostics не наследуются state.

Targeted M2-021 and affected emulator tests: `113 passed`.

## Verification

- `./scripts/verify` — PASS.
- `./scripts/check-docs` — PASS.
- `git diff --check` — PASS.
- Formatting, lint и mypy выполняются через `./scripts/verify`.
- Generated artifacts отсутствуют.
- Hardware status: `NOT_TESTED`.

## Architectural compliance

Изменения находятся в `emulator/`, tests и task report. Не добавлены ISA instructions, opcode, registers, memory/reset semantics, policy state, diagnostic history, cycle timing, DATA BUS, microsteps, control words, simulator, run loop, bounded helper, serialization, assembler, loader или hardware coupling. Final result остаётся software observation boundary для conformance и future parity preparation.

## Commit

Atomic commit reference будет зафиксирован итоговым commit этой задачи без amend или второго documentation commit. До создания commit в report и index используется pending commit reference; фактический hash указывается в итоговом отчёте.

## Result

`COMPLETED`

## Follow-up

Следующая задача — M2-022: добавить bounded execution helper. Push этой задачи не выполняется; Phase E push checkpoint остаётся после M2-022.
