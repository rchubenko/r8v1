# ADR-0005: FLAGS Update on Accumulator Write

## Status

Accepted

## Контекст

Исходный R8 hardware обновлял FLAGS при каждой записи Register A. Отдельный `FLAGS_LOAD` control bit дал бы более гибкую ISA semantics, но добавил бы control-word и gating complexity, не нужную v1 ISA.

## Решение

Сохранить исходную R8 scheme. Decoded A-load action одновременно является FLAGS load-enable event.

```text
FLAGS_LOAD_INTERNAL = A_LOAD
```

В v1 control word нет independent `FLAGS_LOAD` bit. Control-word bit 13 reserved.

Validity flags:

- ADD/SUB определяют Z, C, S и O;
- LDI/LDA определяют Z и S;
- C и O после LDI/LDA unspecified;
- instructions без записи A сохраняют FLAGS.

## Последствия

Положительные:

- воспроизводит проверенную original R8 hardware model;
- убирает dedicated control signal и его gating logic;
- упрощает microcode и hardware bring-up;
- освобождает один control-word bit для будущих versions.

Отрицательные:

- flags нельзя обновить без записи A;
- нельзя записать A с сохранением FLAGS;
- compare-like instructions потребовали бы architecture revision;
- programs не должны использовать JC/JV после LDI/LDA, поскольку C/O unspecified.
