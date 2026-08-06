# Task M2-025: Enforce Emulator Package Boundaries and Review Architectural Drift

## Review result

`NO ARCHITECTURAL DRIFT DETECTED`

## Sources

Проверены `AGENTS.md`, `README.md`, repository structure, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/memory.md`, `docs/testing/software.md`, план Milestone 2, reports M2-001 through M2-024, active ADR, весь код `cpu/` и `emulator/`, public exports, tests и verification scripts.

## Package inventory

### `cpu/`

`cpu/` остаётся reusable component-model layer:

- values/address validation: `values.py`, `address.py`;
- registers and architectural component primitives: `register.py`, `program_counter.py`, `instruction_register.py`, `halt.py`;
- FLAGS values/policies: `flags.py`, `flags_policy.py`;
- ALU models: `alu.py`, `alu_add.py`, `alu_sub.py`;
- SRAM: `sram.py`;
- address/bus models: `address.py`, `data_bus.py`;
- isolated reusable MAR and MICROSTEP models: `mar.py`, `microstep.py`.

AST inventory confirms that `cpu/` has no emulator import, opcode dispatcher, complete instruction fetch/execute loop, `step()`, program runner or emulator diagnostic policy.

### `emulator/`

`emulator/` owns the ISA reference layer:

- `instruction.py`: typed `Opcode`, `DecodedInstruction` and decode;
- `state.py`: architectural state, reset, image loading, fetch, execute and canonical `step()`;
- `policy.py`: external execution policies and non-architectural diagnostics;
- `snapshot.py`: immutable architectural observations;
- `result.py`: immutable `StepResult`;
- `__init__.py`: ISA-emulator public exports.

No simulator, microcode, control-word, EEPROM, DATA BUS, clock-edge, GPIO or hardware adapter dependency exists.

## Import and ownership boundaries

Boundary tests in `tests/test_emulator_boundaries.py` parse production modules with AST:

- `emulator -> cpu` is allowed;
- standard-library imports are allowed;
- `emulator -> simulator/microcode/control_word/hardware/gpio/loader/assembler` is forbidden;
- `cpu -> emulator` is forbidden;
- no forbidden execution-layer imports were found.

The emulator canonical ownership path is `ArchitecturalState.step()` -> `fetch_instruction()` -> `execute_instruction()`. `cpu/` exports reusable component APIs, while `emulator/` exports `ArchitecturalState`, decode values, policy/diagnostics, snapshots and `StepResult`.

## Architectural state and result boundaries

Public `ArchitecturalStateSnapshot` fields are exactly `a`, `pc`, `irh`, `irl`, `flags`, `flags_defined_mask`, `halt_state` and optional `memory`. `StepResult` fields are exactly `instruction`, `pre_state`, `post_state` and `diagnostic`.

Boundary tests confirm absence of public architectural fields for B, MAR, MICROSTEP, DATA BUS, control word, EEPROM address, clock phase, policy, diagnostic history and halt reason. Policy and diagnostics remain outside architectural snapshots; `StepResult` contains no timing or trace fields.

The isolated `cpu.MicrostepCounter` and `cpu.MemoryAddressRegister` remain available as reusable component models but are not imported or used by `emulator/` execution.

## Drift review

- Opcode mapping matches the approved `0x0..0xF` ISA, including reserved `0xB..0xE` and HLT `0xF`.
- A, PC, IR, FLAGS, `flags_defined_mask`, SRAM and HALT remain the emulator architectural ownership set.
- LDI/LDA, ADD/SUB and preserving-instruction FLAGS/mask behavior is covered by existing conformance tests and remains unchanged.
- Reset preserves SRAM and restores PC/A/IR/FLAGS/mask/HALT baseline.
- Fetch reads two current-SRAM bytes, increments PC twice modulo 4096 and supports `0xFFF -> 0x000` wrap.
- STRICT, HARDWARE_LIKE, reserved-opcode and HLT diagnostics/HALT semantics remain covered and non-architectural.
- HALT guard prevents subsequent fetch; reset clears HALT; no halt-reason register exists.

No architectural drift or boundary ambiguity was found.

## Changes

- `tests/test_emulator_boundaries.py` — AST import checks, public export/field checks, forbidden concept checks, opcode mapping and focused reset/fetch/diagnostic/HALT invariants.
- `docs/reports/milestone-2/025-package-boundaries-and-architectural-drift.md` — этот report.
- `docs/reports/milestone-2/README.md` — M2-025 marked `COMPLETED` с report link.

Production code, ISA, architecture, microarchitecture, control word, memory model, ADR, execution contract, milestone plan, task numbering и phase mapping не изменялись.

## Tests

- Targeted boundary tests: `10 passed`.
- Existing conformance, integration and unit tests remain unchanged.
- Boundary tests use AST/introspection rather than fragile full-file text comparison; comments and documentation strings do not affect forbidden-identifier checks.

## Verification

- `./scripts/verify` — PASS.
- `./scripts/check-docs` — PASS.
- `git diff --check` — PASS.
- Full regression: `1285 passed`.
- Formatting, lint и mypy выполняются через `./scripts/verify`.
- Generated artifacts отсутствуют.
- Hardware status: `NOT_TESTED`.

## Architectural compliance

`NO ARCHITECTURAL DRIFT DETECTED`. No production refactor, package restructuring, simulator implementation, microcode/control-word execution, hardware integration or Milestone 3 work was performed.

## Commit

Atomic commit reference будет зафиксирован итоговым commit этой задачи без amend или второго documentation commit. До создания commit в report и index используется pending commit reference; фактический hash указывается в итоговом отчёте.

## Result

`COMPLETED`

## Follow-up

Следующая задача — M2-026: final regression and documentation review. Push этой задачи не выполняется.
