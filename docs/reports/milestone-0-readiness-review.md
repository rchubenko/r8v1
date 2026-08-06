# Проверка готовности репозитория к Milestone 0

## 1. Итог проверки готовности репозитория

Репозиторий **не готов к непосредственному выполнению Milestone 0**.

Архитектурный baseline готов: обязательные документы присутствуют, активные ADR согласованы, ADR-0010 принят и индексирован. Блокеры относятся к repository foundation:

- каталог `/home/roman/Desktop/r8v1` не является Git-репозиторием;
- текущая ветка, working tree и remote отсутствуют;
- software toolchain не выбран и не закреплён;
- monorepo skeleton, manifest, scripts и test harness отсутствуют;
- присутствует пустой каталог `r8-inception`, не описанный в approved structure, его судьбу нужно определить до инициализации Git.

Архитектурных блокеров для Milestone 0 не обнаружено.

## 2. Проверенная архитектурная база

| Область | Источники | Результат | Статус |
| ------- | --------- | --------- | ------ |
| Общая архитектура | `docs/architecture.md`, ADR-0001, ADR-0002, ADR-0003, ADR-0004 | 8-bit CPU, unified 4 KB SRAM, отдельный 12-bit address path, software-first, EEPROM CU согласованы | `CONSISTENT` |
| ISA и opcode reservations | `docs/isa.md`, ADR-0008 | ISA содержит NOP, LDI, LDA, ADD, SUB, STA, JMP, JC, JZ, JN, JV, HLT; `0xB..0xE` reserved | `CONSISTENT` |
| `flags_defined_mask` | `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, ADR-0010 | RESET и ADD/SUB определяют все флаги; LDI/LDA только Z/S; parity сравнивает mask и только defined values | `CONSISTENT` |
| C/O после LDI/LDA | `docs/architecture.md`, `docs/isa.md`, `docs/control-word.md`, ADR-0005, ADR-0010 | Физические значения существуют, архитектурно C/O unspecified; зависимость от JC/JV запрещена | `CONSISTENT` |
| Strict/hardware-like modes | `docs/isa.md`, `docs/microarchitecture.md`, ADR-0010 | Strict mode диагностирует undefined flag; hardware-like mode использует concrete physical value | `CONSISTENT` |
| `HIGH_Z` DATA BUS | `docs/microarchitecture.md`, `docs/control-word.md`, ADR-0010 | `OE_NONE` представляется как `HIGH_Z`/`None` | `CONSISTENT` |
| Producer/consumer invariant | `docs/microarchitecture.md`, `docs/control-word.md`, ADR-0010 | Каждый DATA BUS consumer требует ровно одного producer; producer без consumer разрешён для bring-up | `CONSISTENT` |
| Neutral HALT word | `docs/microarchitecture.md`, `docs/control-word.md`, ADR-0010 | Каноническое поле-by-field значение определено; invalid combinations запрещены | `CONSISTENT` |
| HALT edge semantics | `docs/isa.md`, `docs/microarchitecture.md`, `docs/control-word.md`, ADR-0010 | HALT latch происходит на rising edge; последующие edges не меняют состояние; RESET имеет приоритет | `CONSISTENT` |
| 12-bit PC wraparound | `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, ADR-0010 | `0xFFF + 1 = 0x000` | `CONSISTENT` |
| Boundary fetch | `docs/architecture.md`, `docs/isa.md`, `docs/microarchitecture.md`, ADR-0010 | Fetch `0xFFF -> 0x000`, после fetch PC равен `0x001` | `CONSISTENT` |
| Executable image | `docs/memory.md`, `docs/repository-structure.md`, ADR-0010 | Ровно 4096 bytes, code с `0x000`, data после code, overflow запрещён | `CONSISTENT` |
| Software SRAM initialization | `docs/memory.md`, ADR-0010 | Новая software machine получает 4096 нулевых bytes; RESET SRAM не очищает | `CONSISTENT` |
| `FLAGS_LOAD` | ADR-0005, `docs/architecture.md`, `docs/isa.md`, `docs/control-word.md` | Независимого `FLAGS_LOAD` bit/command нет; update связан с `E_A`/A write | `CONSISTENT` |
| Reset | ADR-0006, `docs/architecture.md`, `docs/microarchitecture.md` | Asynchronous assertion, synchronized deassertion, reset вне control word | `CONSISTENT` |
| SRAM ownership | ADR-0007, `docs/memory.md` | CPU/Pi ownership exclusive, switching only under reset, break-before-make | `CONSISTENT` |
| Clock | ADR-0009, `docs/architecture.md` | Common `CPU_CLK_IN`, Pi single-step during bring-up, source switch under reset | `CONSISTENT` |
| Active ADR index | `docs/adr/README.md`, ADR files | ADR-0001..0010, все Accepted и индексированы | `CONSISTENT` |
| Architecture inception status | `docs/reports/architecture-inception.md` | Документ явно заявляет отсутствие unresolved decisions blocking Milestone 0/1 | `CONSISTENT` |

## 3. Результаты проверки репозитория

### Git

- `git status --short --branch` завершился ошибкой: `not a git repository`.
- Текущая ветка не определена.
- Working tree в Git-смысле отсутствует.
- Remote не настроен.
- История commits отсутствует, поскольку Git repository отсутствует.

### Обязательные документы

Все требуемые файлы присутствуют:

- `AGENTS.md`;
- `docs/architecture.md`;
- `docs/isa.md`;
- `docs/microarchitecture.md`;
- `docs/control-word.md`;
- `docs/memory.md`;
- `docs/adr/README.md`;
- ADR-0001..ADR-0010;
- `docs/repository-structure.md`;
- `docs/plans/milestone-0-repository-foundation.md`;
- `docs/reports/architecture-inception.md`.

### ADR

- Активных ADR: 10.
- Все 10 перечислены в `docs/adr/README.md`.
- Номера активных ADR уникальны.
- ADR-0005 ровно один: `docs/adr/0005-flags-update-on-a-write.md`.
- ADR-0010 существует, имеет статус `Accepted` и присутствует в индексе.
- Дубликатов ADR-0005 не обнаружено.

### `FLAGS_LOAD`

Независимое устаревшее решение не найдено.

Оставшиеся упоминания относятся к разрешённой внутренней связи:

- `FLAGS_LOAD_INTERNAL = A_LOAD`;
- `FLAGS_LOAD_INTERNAL = E_A`;
- явные утверждения, что независимого control-word bit нет.

Consistency check должен различать эти внутренние обозначения и запрещённую независимую команду или поле `FLAGS_LOAD`.

### Markdown links

Проверенные внутренние ссылки:

- ссылки из `README.md` на core documents;
- ссылки из `docs/adr/README.md` на все ADR;
- ссылки из `docs/architecture.md` на `memory.md`, `isa.md`, `microarchitecture.md`, `control-word.md`.

Broken Markdown links не обнаружены.

### Фактическая структура

Присутствуют:

- `AGENTS.md`;
- `README.md`;
- `docs/`;
- `docs/adr/`;
- `docs/plans/`;
- `docs/reports/`.

Отсутствуют, что ожидаемо до Milestone 0:

- `specs/`;
- `cpu/`;
- `emulator/`;
- `simulator/`;
- `assembler/`;
- `microcode/`;
- `loader/`;
- `hardware/`;
- `programs/`;
- `tests/`;
- `scripts/`;
- `pyproject.toml`;
- `.gitignore`;
- `docs/testing/`;
- `docs/milestones/`.

Пустые будущие директории не следует создавать без содержимого. Для них можно использовать минимальные README только там, где это необходимо для package discovery или документирования границы. Production placeholder classes создавать нельзя.

Пустой `r8-inception/` не описан в approved tree. Перед Git bootstrap нужно решить, является ли он внешним workspace artifact или должен быть исключён из будущего repository root. Удалять его сейчас не следует.

### Toolchain

В repository отсутствуют:

- language/runtime manifest;
- dependency lockfile;
- build scripts;
- test configuration;
- formatter/linter configuration;
- CI configuration;
- declared test framework.

Следовательно, toolchain пока не утверждён.

## 4. Варианты toolchain

| Вариант | ISA emulator | Microarchitecture simulator | Fixed-width state | Deterministic tests | CLI assembler/loader | Raspberry Pi | Setup | Анализ и сопровождение |
| ------- | ------------ | --------------------------- | ----------------- | ------------------ | ------------------- | ------------ | ------ | ----------------------- |
| Python 3.12 + `pyproject.toml`, `pytest`, `ruff`, `mypy`, `uv` | Очень хорошо | Очень хорошо | Хорошо через typed wrappers/dataclasses; контроль ширины runtime-проверками | Очень хорошо | Очень хорошо | Отлично | Очень просто | Большая ecosystem, но fixed-width discipline нужно поддерживать явно |
| Rust stable + Cargo, `clippy`, `rustfmt`, встроенный test runner | Очень хорошо | Отлично | Отлично, сильная типизация и явные `u8/u12`-подобные wrappers | Отлично | Отлично | Хорошо | Средне | Сильные guarantees, выше initial complexity и стоимость сопровождения |
| TypeScript + Node.js, `vitest`, `eslint`, `prettier` | Хорошо | Хорошо | Средне: number semantics требуют wrappers и дисциплины | Очень хорошо | Очень хорошо | Хорошо | Хорошо | Сильная CLI ecosystem, но numeric model менее естественен для CPU state |

**Рекомендация:** Python 3.12 с `pyproject.toml`, `pytest`, `ruff`, `mypy` и lockfile через `uv`.

Причины:

- естественно подходит для reference emulator и deterministic simulator;
- хорошо поддерживает CLI tooling;
- доступен на Raspberry Pi;
- минимален по setup cost;
- имеет зрелые formatter, linter, static-analysis и test ecosystems;
- позволяет явно определить fixed-width value types без premature framework structure.

Это engineering decision, а не архитектурное решение CPU. Его следует зафиксировать в:

- `docs/testing/software.md`;
- root `README.md`;
- `pyproject.toml`;
- lockfile;
- при необходимости отдельном engineering decision section, но не в ADR.

Настройку toolchain до отдельного утверждения выполнять не следует.

## 5. Предлагаемый план выполнения Milestone 0

### Task 0.0 — Initialize repository boundary and Git governance

- **Цель:** превратить текущий documentation package в контролируемый Git repository.
- **Source documents:** `AGENTS.md`, `docs/repository-structure.md`, Milestone 0 plan.
- **Scope:** определить repository root, проверить `r8-inception`, создать feature branch после Git initialization, настроить remote только по подтверждённому адресу.
- **Non-goals:** не изменять архитектуру, не удалять неизвестные пользовательские файлы, не создавать production code.
- **Файлы и каталоги:** `.git/` как repository metadata, будущий `.gitignore`, root files.
- **Зависимости:** решение по статусу `r8-inception`.
- **Acceptance criteria:** repository root подтверждён; branch создана; remote явно настроен или зафиксирован как отсутствующий; исходные документы отслеживаются Git.
- **Проверки и тесты:** `git status`, `git branch --show-current`, `git remote -v`, initial clean-tree review.
- **Документация:** README должен описать repository root и branch policy.
- **Риски:** случайное включение внешнего `r8-inception` или пользовательских файлов.
- **Commit:** обычно без отдельного application commit; bootstrap должен быть проверен до первого feature commit.

### Task 0.1 — Confirm architecture baseline

- **Цель:** подтвердить, что нормативный baseline можно использовать без архитектурного решения.
- **Source documents:** все обязательные документы и активные ADR.
- **Scope:** review перечисленных решений, ADR index, document presence, internal links, `FLAGS_LOAD` search.
- **Non-goals:** не выбирать новые ISA semantics, не менять control word, reset, HALT, clock или SRAM ownership.
- **Файлы и каталоги:** только проверяемые документы; изменения только при наличии конкретной approved correction.
- **Зависимости:** Task 0.1 не требует Git для review, но Git необходим для commit.
- **Acceptance criteria:** baseline consistent; ровно один ADR-0005; ADR-0010 accepted/indexed; links resolve.
- **Проверки и тесты:** duplicate ADR scan, indexed-file scan, link check, contradictory wording review.
- **Документация:** только необходимые синхронные corrections.
- **Риски:** механический запрет всех строк `FLAGS_LOAD` ошибочно сочтёт coupled internal signal конфликтом.
- **Commit:** `spec: define deterministic software model semantics` и `spec: align normative documents with ADR-0010` только если будут реальные approved documentation changes; при текущем состоянии вероятен no-op review без этих commits.

### Task 0.2 — Add repository governance

- **Цель:** закрепить правила работы до появления implementation code.
- **Source documents:** `AGENTS.md`, Milestone 0 plan, architecture baseline.
- **Scope:** sources-of-truth order, no-guessing policy, development sequence, hardware statuses, test layers, generated artifacts, clean-main rules.
- **Non-goals:** OpenCode commands, subagents, CI, automated merge management.
- **Файлы и каталоги:** `AGENTS.md`, возможно root `README.md`.
- **Зависимости:** Task 0.1.
- **Acceptance criteria:** используются только `NOT_TESTED`, `PASS`, `FAIL`, `BLOCKED`; inferred hardware PASS запрещён; software-first sequence закреплена.
- **Проверки и тесты:** policy checklist и keyword checks.
- **Документация:** `AGENTS.md`.
- **Риски:** случайное добавление workflow policy, не одобренной проектом.
- **Commit:** `docs: add repository agent policy`, если policy ещё не отслеживается Git.

### Task 0.3 — Create monorepo skeleton

- **Цель:** создать approved package boundaries без production behavior.
- **Source documents:** `docs/repository-structure.md`, Milestone 0 plan.
- **Scope:** top-level directories и только необходимые package markers; `.gitignore`; root manifest после выбора toolchain.
- **Non-goals:** CPU classes, emulator, simulator, assembler, loader, hardware code, compiler directory.
- **Файлы и каталоги:** `specs/`, `cpu/`, `emulator/`, `simulator/`, `assembler/`, `microcode/`, `loader/`, `hardware/`, `programs/`, `tests/`, `scripts/`; без пустых binary directories.
- **Зависимости:** Task 0.0 и утверждение toolchain.
- **Acceptance criteria:** структура соответствует документу; нет speculative APIs; compiler не создаётся.
- **Проверки и тесты:** layout check, package discovery smoke test, `git diff --check`.
- **Документация:** root README map и repository structure при необходимости.
- **Риски:** пустые каталоги могут исчезнуть из Git; добавлять только осмысленные README/package markers.
- **Commits:** `build: create monorepo skeleton`, затем отдельно `docs: document repository structure`.

### Task 0.4 — Select and configure software toolchain

- **Цель:** закрепить воспроизводимый runtime и developer tooling.
- **Source documents:** Milestone 0 plan, `docs/repository-structure.md`, engineering decision review.
- **Scope:** выбранный runtime, dependency management, formatter, linter, static analysis, test runner, lock data.
- **Non-goals:** production CPU types, framework-heavy application structure, hardware libraries.
- **Файлы и каталоги:** `pyproject.toml`, lockfile, tool configuration, `docs/testing/software.md`.
- **Зависимости:** approval Python recommendation or another selected option.
- **Acceptance criteria:** clean environment installable; declared commands pass; undeclared global dependency не требуется.
- **Проверки и тесты:** version report, install, formatter check, static check, intentional failure propagation.
- **Документация:** prerequisites и exact local commands.
- **Риски:** изменение toolchain после Milestone 1 увеличит стоимость; решение нужно закрепить сейчас.
- **Commit:** `build: configure software development toolchain`.

### Task 0.5 — Add minimal deterministic test harness

- **Цель:** доказать работоспособность test layer без реализации CPU.
- **Source documents:** `AGENTS.md`, Milestone 0 plan.
- **Scope:** минимальный smoke test, package discovery test, deterministic test configuration.
- **Non-goals:** ISA tests, component behavior, emulator, simulator, hardware tests.
- **Файлы и каталоги:** `tests/`, test configuration, возможно `tests/fixtures/` только с foundation fixtures.
- **Зависимости:** Task 0.3 и Task 0.4.
- **Acceptance criteria:** test runner проходит из clean checkout; результат deterministic; failure имеет non-zero exit code.
- **Проверки и тесты:** repeated local runs, clean-environment run, package discovery.
- **Документация:** `docs/testing/software.md`.
- **Риски:** smoke test не должен выглядеть как CPU implementation или architecture conformance.
- **Commit:** `test: add foundation smoke tests`.

### Task 0.6 — Add reproducible repository scripts

- **Цель:** предоставить стабильные локальные entry points.
- **Source documents:** Milestone 0 plan, `AGENTS.md`, `docs/repository-structure.md`.
- **Scope:** `scripts/verify`, `scripts/check-docs`, `scripts/generate`.
- **Non-goals:** OpenCode commands, CI, subagents, auto-commit/push, hardware mutation.
- **Файлы и каталоги:** `scripts/`, `docs/testing/software.md`, root README.
- **Зависимости:** Task 0.4 и Task 0.5.
- **Acceptance criteria:** `verify` запускает formatter, static analysis, tests, docs checks, generated-artifact check when applicable, whitespace check; scripts не изменяют source files.
- **Проверки и тесты:** shell syntax, success path, failure propagation for each check, execution from repository root.
- **Риски:** `generate` должен быть безопасным no-op или явно сообщать, что generated sources ещё отсутствуют.
- **Commit:** `scripts: add reproducible repository checks`, затем `docs: document local verification`.

### Task 0.7 — Add lightweight architecture consistency checks

- **Цель:** автоматически ловить раннюю divergence нормативных решений.
- **Source documents:** `AGENTS.md`, `docs/architecture.md`, `docs/isa.md`, `docs/control-word.md`, `docs/memory.md`, ADR index.
- **Scope:** required files, unique ADR numbers, index completeness, reserved opcodes, control-word width/reserved bit, memory/image sizes, forbidden independent `FLAGS_LOAD`.
- **Non-goals:** natural-language theorem proving, generation of architecture from code, replacement of human review.
- **Файлы и каталоги:** checker implementation в foundation tooling, fixtures, tests.
- **Зависимости:** Tasks 0.4–0.6.
- **Acceptance criteria:** duplicate ADR, missing index entry, contradictory machine-checkable constants и invalid independent `FLAGS_LOAD` fail with file locations; approved baseline passes.
- **Проверки и тесты:** positive/negative fixtures, deterministic output and exit status.
- **Риски:** false positives на legitimate explanatory text, especially `FLAGS_LOAD_INTERNAL`; checks должны быть syntax/statement-aware enough.
- **Commit:** `test: add architecture consistency gates`.

### Task 0.8 — Documentation and clean-checkout verification

- **Цель:** проверить, что repository instructions воспроизводимы новым checkout.
- **Source documents:** весь approved documentation package, Milestone 0 plan.
- **Scope:** README command map, prerequisites, testing docs, generated artifact policy, clean-checkout instructions.
- **Non-goals:** implementation documentation, hardware claims, physical verification.
- **Файлы и каталоги:** `README.md`, `docs/testing/software.md`, возможно `docs/milestones/`.
- **Зависимости:** Tasks 0.3–0.7.
- **Acceptance criteria:** documented commands work from clean checkout; links resolve; hardware status remains `NOT_TESTED`.
- **Проверки и тесты:** fresh checkout or archive test, full docs link check, `git diff --check`, clean-tree check.
- **Документация:** local development and verification instructions.
- **Риски:** docs могут описать будущую функциональность как уже реализованную.
- **Commit:** `docs: document local verification`.

### Task 0.9 — Final Milestone 0 regression

- **Цель:** доказать, что foundation содержит только governance и infrastructure.
- **Source documents:** Milestone 0 plan, `AGENTS.md`, all normative documents.
- **Scope:** full verification, diff review, architecture review, generated-artifact reproducibility, scope review.
- **Non-goals:** начало Milestone 1, cleanup с добавлением CPU behavior, physical testing.
- **Файлы и каталоги:** весь diff feature branch.
- **Зависимости:** все предыдущие задачи.
- **Acceptance criteria:** `scripts/verify` passes; no CPU/emulator/simulator/assembler/loader behavior; docs current; no unrelated changes.
- **Проверки и тесты:** full regression, clean checkout, `git diff --check`, clean working tree.
- **Документация:** `docs/milestones/milestone-0-report.md`.
- **Риски:** accidental placeholder production classes или stale generated output.
- **Commit:** `docs: add milestone 0 verification report`.

### Task 0.10 — Prepare stable `main`

- **Цель:** передать repository в Milestone 1 без незавершённых изменений.
- **Source documents:** `AGENTS.md`, Milestone 0 plan, repository governance.
- **Scope:** review complete commit series, merge approved branch, verify `main`, configure remote push.
- **Non-goals:** tag до полного завершения и проверки, Milestone 1 code, hardware testing.
- **Файлы и каталоги:** Git metadata и completed foundation changes.
- **Зависимости:** Task 0.9 и explicit approval.
- **Acceptance criteria:** `main` stable, clean, fully verified; push только после успешной проверки; hardware status `NOT_TESTED`.
- **Проверки и тесты:** `git status`, complete diff review, `git log`, `scripts/verify` on `main`.
- **Документация:** milestone report должен перечислить точные verification commands.
- **Риски:** merge unrelated changes или overstated hardware status.
- **Commit/tag:** tag `v1-m0-foundation` допускается только после merge и verification; до этого tag не создавать.

## 6. Предлагаемая ветка и атомарные commits

Предлагаемая ветка:

```text
milestone/0-repository-foundation
```

Ожидаемая последовательность:

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

Для текущего состояния commits 1–2 могут быть не нужны: ADR-0010 и соответствующие clarifications уже присутствуют. Их следует создавать только при обнаружении конкретной approved correction.

Каждый логический набор должен проверяться до следующего commit. Перед merge обязательны:

- полный `git diff`;
- `git diff --check`;
- `scripts/verify`;
- clean checkout verification;
- clean working tree;
- отсутствие unrelated files;
- hardware status `NOT_TESTED`.

Push выполнять только после успешной проверки завершённого логического набора. Tag создавать только после merge и полного Milestone 0 regression.

## 7. Approval gates

До изменения файлов необходимо явно утвердить:

1. repository root и статус пустого `r8-inception`;
2. инициализацию Git repository;
3. имя feature branch;
4. remote URL либо решение временно работать без remote;
5. software toolchain, предпочтительно Python 3.12 + `uv`/`pytest`/`ruff`/`mypy`;
6. engineering-decision место фиксации toolchain;
7. точную политику создания минимальных README/package markers для будущих директорий;
8. отсутствие необходимости менять текущие нормативные документы;
9. формат lightweight architecture consistency checks;
10. необходимость и формат `docs/milestones/milestone-0-report.md`.

Архитектурное решение по ISA, flags, control word, reset, HALT, clock или SRAM ownership утверждать заново не требуется: текущая проверка показала `CONSISTENT`.

## 8. Explicit confirmation

- Файлы не создавались и не изменялись.
- Файлы не удалялись и не форматировались.
- Commits и push не выполнялись.
- CPU, emulator, simulator, assembler и loader не реализовывались.
- Hardware integration не выполнялась.
- Hardware verification status остаётся `NOT_TESTED`.

## Связанные решения и документы

- [План Milestone 0](../plans/milestone-0-repository-foundation.md) использует этот readiness review.
- [Архитектура R8 v1](../architecture.md), [ISA](../isa.md), [микроархитектура](../microarchitecture.md), [Control Word](../control-word.md) и [memory](../memory.md) являются проверенными источниками.
- [Индекс ADR](../adr/README.md) содержит активные ADR, проверенные в отчёте.
