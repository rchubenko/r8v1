# Task M2-003: Add opcode and decoded instruction values

## Summary

Реализован минимальный typed decode layer ISA Reference Emulator. Добавлены представления всех 16 opcode, immutable decoded instruction и stateless decode 16-bit instruction value. Instruction execution, fetch orchestration и architectural state не реализованы.

## Sources

Работа сверена с [`AGENTS.md`](../../../AGENTS.md), [README проекта](../../../README.md), [архитектурой](../../architecture.md), [ISA](../../isa.md), [микроархитектурой](../../microarchitecture.md), [Control Word](../../control-word.md), [memory](../../memory.md), [software testing policy](../../testing/software.md), [планом Milestone 2](../../plans/milestone-2-isa-reference-emulator.md), [execution contract M2-002](002-emulator-execution-contract.md), [индексом ADR](../../adr/README.md), активными ADR и существующими conventions package `cpu/` и tests.

## Scope

В scope входили typed opcode values `0x0..0xF`, immutable decoded instruction с typed opcode и 12-bit operand, а также deterministic extraction из 16-bit instruction value. Reserved opcode `0xB..0xE` представлены без execution semantics.

## Design decision

Canonical API:

```python
decode_instruction(instruction: object) -> DecodedInstruction
```

API принимает одно validated 16-bit integer value. Byte API не добавлялся, поскольку существующие component conventions уже предоставляют составление instruction из IRH/IRL, а дублирующая публичная boundary не требуется.

`Opcode` является `Enum` с numeric values `0x0..0xF`. Reserved values представлены отдельными members `RESERVED_B`, `RESERVED_C`, `RESERVED_D` и `RESERVED_E`. `DecodedInstruction` является `@dataclass(frozen=True, slots=True)` с полями `opcode: Opcode` и `operand: int`.

## Changes

- `emulator/__init__.py` — public exports.
- `emulator/instruction.py` — `Opcode`, `DecodedInstruction` и `decode_instruction`.
- `tests/test_emulator_instruction.py` — unit coverage decode/value boundary.
- `pyproject.toml` — package discovery и strict mypy coverage для `emulator/`.
- `docs/reports/milestone-2/003-opcode-and-decoded-instruction-values.md` — этот report.
- `docs/reports/milestone-2/README.md` — статус и report link для M2-003.

Source-of-truth documents, ISA, active ADR и milestone plan после отдельного planning correction commit не изменялись.

## Tests

Проверены:

- все opcode `0x0..0xF` с exact numeric mapping;
- отдельные NOP, JV, reserved `0xB..0xE` и HLT cases;
- operands `0x000`, `0x001`, `0x00F`, `0x0FF`, `0x100`, `0xABC`, `0xFFE`, `0xFFF`;
- полные instruction examples, включая `0x1ABC`, `0x6FFF`, `0xB123`, `0xEABC` и `0xFFFF`;
- repeated decode, equality и отсутствие stateful behavior;
- immutability через `FrozenInstanceError`;
- отсутствие assembler-specific operand validation: `LDI 0xABC` успешно декодируется.

Execution behavior tests не добавлялись.

## Verification

Targeted decode tests: `53 passed` до planning correction; после восстановления WIP выполнена полная regression.

Обязательные проверки после завершения implementation:

- `./scripts/verify` — PASS;
- `git diff --check` — PASS;
- formatting, lint и mypy — PASS;
- documentation checks — PASS;
- generated artifacts — отсутствуют.

## Architectural compliance

Implementation находится в `emulator/` и использует только существующие validators из `cpu/`. `cpu/` не получил instruction decoder. Нет зависимостей от simulator, microcode, assembler, loader или hardware. Decode не выполняет instruction, не читает execution policy, не создаёт diagnostics и не моделирует fetch, DATA BUS, MAR, MICROSTEP или clock.

Reserved opcode не отвергаются decode layer; illegal-opcode halt остаётся задачей execution layer.

Hardware status: `NOT_TESTED`.

## Result

`COMPLETED`

## Commit

Expected atomic commit:

```text
emulator: add ISA instruction decoding values
```

Planning correction находится в отдельном commit `f55ea0e` с message `docs: align Milestone 2 task numbering`.

## Follow-up

Следующая задача — M2-004: добавить architectural emulator state. Exact executable image loading остаётся отдельной задачей M2-006. Push не выполняется в рамках этой задачи.
