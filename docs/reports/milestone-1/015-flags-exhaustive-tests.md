# Task M1-015: Exhaustive FLAGS tests

## Summary

Расширено coverage FLAGS policy независимыми exhaustive и parameterized tests. Production behavior не изменялся.

## Sources

Решение основано на `AGENTS.md`, `README.md`, `docs/plans/milestone-1-component-models.md`, `docs/reports/milestone-1/README.md`, reports Tasks 8–10, 13 и 14, `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, `docs/adr/README.md` и всеми активными ADR, особенно ADR-0005 и ADR-0010. Реализация tests сверена с `cpu/alu.py`, `cpu/alu_add.py`, `cpu/alu_sub.py`, `cpu/flags.py`, `cpu/flags_policy.py`, `cpu/values.py`, существующими ALU и FLAGS tests, `docs/testing/software.md`, `pyproject.toml` и `scripts/verify`.

## Test strategy

Выбран вариант A: отдельный test file `tests/test_cpu_flags_exhaustive.py` с end-to-end loops ALU API -> FLAGS latch policy. Существующие exhaustive ADD/SUB tests Tasks 8–9 не изменялись и продолжают проверять low-level ALU results.

Новые loops независимо вычисляют `wide`, modulo result, Z, C, S и O и сравнивают их с ALU result и новым `FlagsSnapshot`. Production fields не используются для вычисления expected values.

Отдельно добавлена полная non-ALU matrix. Focused tests покрывают mask transitions, preserve, reset и validation regression. Production code не изменён.

## ADD coverage

Проверены все `256 x 256 = 65536` пар через `evaluate(ALUMode.ADD, a, b)` и `latch_flags_for_alu_write()`.

Expected formulas:

```text
wide = a + b
result = wide & 0xFF
Z = result == 0x00
C = wide > 0xFF
S = bool(result & 0x80)
O = same-sign operands and result sign differs from operand sign
```

Проверяются ALU result, все concrete FLAGS и all-defined mask.

## SUB coverage

Проверены все `256 x 256 = 65536` пар через `evaluate(ALUMode.SUB, a, b)` и `latch_flags_for_alu_write()`.

Expected formulas:

```text
wide = a - b
result = wide & 0xFF
Z = result == 0x00
C = a >= b
S = bool(result & 0x80)
O = differing-sign operands and result sign differs from A sign
```

Boundary cases, equal operands, underflow и no-borrow C входят в exhaustive coverage.

## Non-ALU write coverage

Проверены все `256` incoming A bytes и все четыре concrete C/O combinations:

```text
256 x 4 = 1024 cases
```

Для каждого case independently проверяются:

- `Z = value == 0x00`;
- `S = bool(value & 0x80)`;
- C/O сохраняют переданные concrete values;
- defined mask содержит только Z/S;
- C/O остаются доступными в values, несмотря на undefined mask.

## Defined mask transitions

Проверены логические immutable sequences без mutable FLAGS register:

- reset -> full-defined ALU result;
- reset -> partial-defined non-ALU value;
- partial-defined -> full-defined;
- full-defined -> partial-defined.

Каждая policy function создаёт новый resulting snapshot и не читает history.

## Preserve and reset

Проверены preserve для reset, all-defined, Z/S-only, Z/S-only с concrete `C=True/O=True` и none-defined snapshots. `preserve_flags()` сохраняет values/mask и возвращает тот же immutable object.

Reset проверен после simulated full/partial sequence: values равны `0000`, mask all-defined, snapshot immutable и deterministic.

## Performance

Baseline до Task 15:

```text
time ./scripts/verify: real 2.194s
pytest: 464 passed in 1.09s
```

После добавления tests:

```text
time ./scripts/verify: real 4.132s
pytest: 478 passed in 2.88s
```

Runtime остаётся практичным для полного regression run. Timing не закрепляется жёстким assertion, так как зависит от среды.

## Changes

- Добавлен `tests/test_cpu_flags_exhaustive.py`.
- Production code не изменялся.
- Добавлен этот report.
- Обновлён milestone index; hash commit оставлен `—`.

## Verification

Перед commit выполняются `time ./scripts/verify`, `git diff --check`, status/stat checks и targeted/full pytest. Hardware verification не выполняется; hardware status — `NOT_TESTED`.

## Architectural compliance

Не добавлены mutable FLAGS register, A orchestration, instruction execution, instruction mnemonics, control-word decode, `E_A`, clock/rising-edge semantics, branch diagnostics, strict/hardware-like modes, emulator, simulator или hardware work.

## Result

`COMPLETED`

## Commit

Atomic commit:

```text
test: add exhaustive flags coverage
```

Hash текущего commit будет указан в Git metadata; push и tag не выполняются.

## Follow-up

Следующая задача — Task 16: SRAM storage model. FLAGS policy и её test coverage остаются без изменений.
