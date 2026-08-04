# Milestone 0: Repository Foundation

> Этот план сохранён как normative scope Milestone 0. Поясняющий текст переведён на русский; identifiers, paths, commands и commit names сохранены.

## Goal

Create a stable, reproducible monorepo foundation that enforces the approved R8 v1 architecture before any CPU, emulator, simulator, assembler, loader, or hardware implementation begins.

## Milestone result

At completion:

- active architecture documents and ADRs form one internally consistent baseline;
- repository-wide agent rules are present;
- the approved monorepo skeleton exists;
- a minimal deterministic build and test harness works from a clean checkout;
- architectural consistency and generated-artifact checks have defined entry points;
- no CPU behavior has been implemented;
- `main` is stable and ready for Milestone 1 component models.

## Sources

- `AGENTS.md`;
- `docs/architecture.md`;
- `docs/isa.md`;
- `docs/microarchitecture.md`;
- `docs/control-word.md`;
- `docs/memory.md`;
- accepted ADRs listed in `docs/adr/README.md`.

## Milestone scope

- normative documentation updates for approved software-model semantics;
- ADR index and ADR-0010;
- root `AGENTS.md`;
- monorepo directory skeleton;
- language/build manifest selection;
- minimal test framework;
- minimal reproducible repository scripts;
- documentation and architecture consistency checks;
- contribution and verification documentation.

## Non-goals

- CPU component behavior;
- ISA execution;
- control-word classes or generated microcode;
- microarchitecture simulation;
- assembler parsing or encoding;
- Raspberry Pi GPIO code;
- SRAM loader implementation;
- hardware schematics or wiring;
- OpenCode custom commands, subagents, or complex automation;
- CI beyond a minimal local reproducibility baseline;
- compiler work.

## Task 0.1 — Finalize the architecture baseline

### Goal

Commit the approved normative clarifications without changing unrelated architecture.

### Scope

- defined-mask and undefined-flag diagnostic semantics;
- HIGH_Z DATA BUS and producer/consumer invariant;
- canonical neutral HALT word and edge semantics;
- 12-bit PC wraparound and boundary fetch;
- exact 4096-byte executable image and software SRAM initialization;
- active ADR index.

### Non-goals

- selecting additional behavior;
- implementation code;
- physical circuit decisions.

### Acceptance criteria

- exactly one active ADR-0005 exists;
- ADR-0010 is accepted and indexed;
- ISA, microarchitecture, control-word, memory, and architecture documents agree;
- no unrelated opcode, register, control-word field, microsequence, reset, clock, or ownership rule changes;
- all internal Markdown links resolve.

### Tests

- search for duplicate ADR numbers;
- search for contradictory `FLAGS_LOAD` statements;
- check heading and link consistency;
- review normative statements against the approved decisions.

### Documentation

- affected normative documents;
- `docs/adr/README.md`;
- ADR-0010.

### Recommended commits

```text
spec: define deterministic software model semantics
spec: align normative documents with ADR-0010
```

## Task 0.2 — Add repository governance

### Goal

Establish repository-wide rules before implementation starts.

### Scope

- sources-of-truth order;
- no-guessing and architecture-change policy;
- required development sequence;
- stable `main` rules;
- hardware verification statuses;
- test-layer separation;
- generated-artifact and documentation policy;
- planning, review, and commit requirements.

### Non-goals

- OpenCode command implementation;
- automated branch or merge management;
- CI enforcement.

### Acceptance criteria

- root `AGENTS.md` exists;
- it uses exactly `NOT_TESTED`, `PASS`, `FAIL`, and `BLOCKED` for hardware status;
- it explicitly forbids inferred hardware `PASS`;
- it requires specification → software → tests → hardware → regression → documentation;
- it requires the complete software CPU before hardware integration;
- it explicitly defers workflow commands.

### Tests

- policy checklist review;
- search for required status names and development sequence;
- confirm no conflicting workflow policy exists.

### Documentation

- `AGENTS.md` only.

### Recommended commit

```text
docs: add repository agent policy
```

## Task 0.3 — Create the monorepo skeleton

### Goal

Create the approved package and directory boundaries without production behavior.

### Scope

- directories defined in `docs/repository-structure.md`;
- package markers only where required by the chosen language;
- root README updates;
- `.gitignore`;
- one build/project manifest;
- no empty generated binaries committed.

### Non-goals

- placeholder CPU classes;
- speculative APIs;
- dead production modules;
- compiler directory.

### Acceptance criteria

- all approved top-level directories exist;
- package discovery/import smoke test succeeds;
- no production file claims unimplemented behavior;
- repository structure matches its document;
- clean checkout has no required manual setup beyond documented tool installation.

### Tests

- directory-layout check;
- import/package discovery smoke test;
- `git diff --check`;
- clean-tree check after build/test.

### Documentation

- root README repository map;
- `docs/repository-structure.md`.

### Recommended commits

```text
build: create monorepo skeleton
docs: document repository structure
```

## Task 0.4 — Establish the software toolchain

### Goal

Choose and configure one minimal, reproducible development toolchain for upcoming software milestones.

### Scope

- supported runtime version;
- dependency management;
- formatter;
- linter/static analysis;
- test runner;
- deterministic configuration in the repository.

### Non-goals

- framework-heavy application structure;
- packaging for end users;
- performance optimization;
- hardware libraries.

### Acceptance criteria

- supported runtime is documented;
- dependencies install from the committed manifest/lock data;
- formatter check, static check, and empty/basic test suite pass;
- commands return meaningful non-zero exit codes on failure;
- no globally installed undeclared dependency is required.

### Tests

- clean-environment install where practical;
- intentional formatter/linter/test failure confirms propagation;
- version-report command.

### Documentation

- local development prerequisites;
- exact installation and verification commands.

### Recommended commits

```text
build: configure software development toolchain
test: add foundation smoke tests
```

## Task 0.5 — Add minimal reproducible scripts

### Goal

Provide stable shell entry points without introducing OpenCode-specific workflow automation.

### Scope

- `scripts/verify`;
- `scripts/check-docs`;
- `scripts/generate` as a safe no-op or explicit future hook until generated sources exist;
- clear exit-code behavior.

### Non-goals

- `/plan`, `/verify`, `/docs`, `/review`, or `/commit` OpenCode commands;
- subagent orchestration;
- automatic commits or pushes;
- hardware status mutation.

### Acceptance criteria

`scripts/verify` runs, at minimum:

- formatter check;
- static analysis;
- tests;
- documentation checks;
- generated-artifact consistency check when generators exist;
- `git diff --check` or equivalent repository whitespace validation.

The scripts do not modify source files during verification. Temporary build output is ignored and removed or reproducible.

### Tests

- success from a clean repository;
- failure propagation from each underlying check;
- shell syntax validation;
- execution from repository root.

### Documentation

- `docs/testing/software.md`;
- root README command summary.

### Recommended commits

```text
scripts: add reproducible repository checks
docs: document local verification
```

## Task 0.6 — Add architecture consistency checks

### Goal

Catch accidental divergence before implementation grows.

### Scope

Initially lightweight checks for:

- unique active ADR numbers;
- active ADR index completeness;
- reserved opcode range consistency;
- control-word width and reserved bit consistency;
- memory size and image-size consistency;
- required architecture document presence;
- absence of the superseded explicit `FLAGS_LOAD` decision in active sources.

### Non-goals

- full natural-language theorem checking;
- generating architecture from code;
- replacing human review.

### Acceptance criteria

- a deliberately duplicated ADR number fails;
- a missing indexed ADR fails;
- contradictory canonical constants fail where machine-checkable;
- the approved baseline passes;
- checks report actionable file locations.

### Tests

- fixture-based positive and negative tests;
- deterministic output and exit status.

### Documentation

- description of what is and is not mechanically checked.

### Recommended commit

```text
test: add architecture consistency gates
```

## Task 0.7 — Foundation review and milestone closure

### Goal

Verify that Milestone 0 contains governance and infrastructure only and leaves `main` ready for component models.

### Scope

- full diff review;
- architecture consistency review;
- clean-checkout verification;
- documentation review;
- milestone report.

### Non-goals

- adding “small” CPU implementations during cleanup;
- starting Milestone 1 in the same commit;
- physical hardware testing.

### Acceptance criteria

- all Milestone 0 tasks meet their criteria;
- `scripts/verify` passes from a clean checkout;
- no CPU/emulator/simulator/assembler/loader behavior exists;
- hardware status is `NOT_TESTED` and no physical PASS is claimed;
- `main` is stable;
- milestone report lists exact verification performed;
- milestone tag may be created only after merge and verification.

### Tests

- full foundation verification;
- repository cleanliness check;
- manual architecture and scope review.

### Documentation

```text
docs/milestones/milestone-0-report.md
```

### Recommended commits

```text
docs: add milestone 0 verification report
```

Optional tag after completion:

```text
v1-m0-foundation
```

## Suggested atomic commit sequence

1. `spec: define deterministic software model semantics`
2. `spec: align normative documents with ADR-0010`
3. `docs: add repository agent policy`
4. `docs: document repository structure`
5. `build: create monorepo skeleton`
6. `build: configure software development toolchain`
7. `test: add foundation smoke tests`
8. `scripts: add reproducible repository checks`
9. `test: add architecture consistency gates`
10. `docs: document local verification`
11. `docs: add milestone 0 verification report`

Commits may be combined only when the resulting commit remains cohesive, independently verifiable, and easily revertible.

## Milestone exit gate

Milestone 0 is complete only when all of the following are true:

```text
architecture baseline consistent
AGENTS.md approved
monorepo structure present
toolchain reproducible
foundation tests pass
architecture gates pass
documentation current
hardware status = NOT_TESTED
main stable
```

OpenCode workflow commands remain deferred. Their need will be evaluated after real repeated work during Milestones 1–2.
