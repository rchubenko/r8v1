# Task M2-024: Add Hand-Encoded Multi-Instruction Integration Programs

## Summary

Добавлен integration test layer с hand-encoded multi-instruction programs. Все fixtures являются exact 4096-byte images, загружаются через `ArchitecturalState.load_image()` и выполняются только через public `step()` с explicit finite calls или test-local hard bound. Assembler, parser и production runner не используются.

## Sources

Работа сверена с `AGENTS.md`, `README.md`, `docs/architecture.md`, `docs/isa.md`, `docs/memory.md`, `docs/testing/software.md`, планом Milestone 2, reports index, M2-002, reports M2-003 through M2-023, ADR-0001, ADR-0005, ADR-0008, ADR-0010, production `emulator/`, `ArchitecturalState`, `StepResult`, exact image-loading API, existing conformance tests и verification scripts.

## Scope

Integration layer проверяет exact bytes, exact fetched instruction sequence, intermediate `StepResult` transitions и explicit final architectural state. Production code, ISA semantics, assembler, loader, bounded runner, simulator parity, cycle timing и hardware не изменялись.

## Test organization

Все tests находятся в `tests/test_emulator_integration_programs.py`. Test-only helpers ограничены:

- zero-filled exact image construction с явными `(address, bytes)` placements;
- exact finite step execution;
- bounded `run_until_halt(max_steps)` с обязательным limit;
- final snapshot assertions и opcode sequence extraction.

Ни один helper не принимает mnemonic source, не кодирует instructions и не дублирует fetch/decode/execute.

## Programs

### Arithmetic

`ARITHMETIC_IMAGE` starts at `0x000` with bytes:

```text
10 05 30 10 40 11 50 12 F0 00
```

This is `LDI 0x005`, `ADD 0x010`, `SUB 0x011`, `STA 0x012`, `HLT`; data bytes are `FB` at `0x010` and `01` at `0x011`. The sequence checks carry/zero transition after ADD, sign/no-borrow transition after SUB, result write `M[0x012]=FF`, flags/mask and final HLT snapshot.

### Defined branches

`DEFINED_BRANCH_IMAGE` uses JZ at `0x002`, JN at odd target `0x009`, and JC at `0x019` after ADD defines C. Skipped LDI/HLT bytes prove that taken branches alter the fetched sequence. Final target `0x021` contains LDI/HLT.

### STRICT undefined conditional

`STRICT_IMAGE` bytes are:

```text
10 42 70 08 10 99 F0 00
```

The explicit two-step sequence `LDI 0x042 -> JC 0x008` stops after `UNDEFINED_CONDITIONAL_FLAG ERROR`; PC remains post-fetch `0x004`, HALT remains false and the later LDI is not executed.

### HARDWARE_LIKE undefined conditional

`HARDWARE_LIKE_IMAGE` uses the same JC sequence with not-taken code at `0x004` and taken code at `0x008`. Parameterized concrete C `0/1` cases verify WARNING diagnostics, concrete branch selection, continued explicit execution and unchanged `Z|S` mask.

### Finite loop

`LOOP_IMAGE` hand-encodes counter initialization, `LDA`, `SUB`, `STA`, `JZ` and `JMP` around addresses `0x100`/`0x101`. Counter `3` reaches zero after exactly 17 fetched instructions. `_run_until_halt(..., max_steps=20)` is a test-local hard bound; no unbounded loop exists.

### Self-modifying program

`SELF_MODIFYING_IMAGE` encodes `LDI 0x0F0`, `STA 0x010`, `JMP 0x010`, with initial future bytes `00 00`. STA changes only byte `0x010` to `F0`; the next result fetches `HLT 0x000` from current SRAM.

### Boundary fetch

`BOUNDARY_IMAGE` places `10` at `0xFFF`, `42` at `0x000`, and HLT at `0x001`. The first result decodes LDI `0x042`, has pre-PC `0xFFF` and post-PC `0x001`; the next result executes HLT.

### Reserved, HALT and reset

`RESERVED_IMAGE` executes LDI then reserved `0xB` with operand `0x123`, returns `ILLEGAL_OPCODE`, halts, produces an already-halted result with no repeated diagnostic, then resets and resumes from image address `0x000` while preserving the exact SRAM image. HLT behavior is also covered by the arithmetic and boundary programs.

## Determinism and final state

Programs assert exact decoded instruction sequences, diagnostics, branch PC transitions, final A/PC/IR/FLAGS/mask/HALT state and relevant SRAM bytes. The arithmetic program is executed on independent equal states and produces equal `StepResult` sequences and final snapshots. All image fixtures assert exact length `4096` and `bytes` type.

## Changes

- `tests/test_emulator_integration_programs.py` — hand-encoded integration programs and bounded execution tests.
- `docs/reports/milestone-2/024-multi-instruction-integration-programs.md` — этот report.
- `docs/reports/milestone-2/README.md` — M2-024 marked `COMPLETED` с report link.

Source-of-truth documents, ISA, architecture, ADR и milestone plan не изменялись.

## Tests

- Targeted integration tests: `11 passed`.
- Programs cover arithmetic, defined branches, STRICT, HARDWARE_LIKE, finite loop, self-modifying code, boundary fetch, reserved opcode, HLT/reset/resume and determinism.
- All multi-step execution is exact-count or hard-bounded.

## Verification

- `./scripts/verify` — PASS.
- `./scripts/check-docs` — PASS.
- `git diff --check` — PASS.
- Full regression: `1275 passed`.
- Formatting, lint и mypy выполняются через `./scripts/verify`.
- Generated artifacts отсутствуют.
- Hardware status: `NOT_TESTED`.

## Architectural compliance

Изменения находятся только в `tests/` и task report/index. Не добавлены production encoding API, assembler, loader, run loop, bounded production helper, simulator, microsteps, DATA BUS, control words, cycle timing или hardware coupling. `cpu/` and `emulator/` production boundaries не изменялись.

## Commit

Atomic commit:

```text
b4612c8 test: add ISA emulator integration programs
```

## Result

`COMPLETED`

## Follow-up

Следующая задача — M2-025: проверить boundary and drift cases. Push этой задачи не выполняется; Phase F final workflow остаётся отдельным.
