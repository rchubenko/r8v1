# ADR-0005: Обновление FLAGS при записи в A

## Статус

Принято

## Контекст

Исходный R8 hardware обновлял FLAGS при каждой записи Register A. Отдельный `FLAGS_LOAD` control bit дал бы более гибкую семантику ISA, но добавил бы control-word и gating complexity, не нужную v1 ISA.

## Решение

Сохранить исходную R8 scheme. Decoded A-load action одновременно является событием FLAGS load-enable.

```text
FLAGS_LOAD_INTERNAL = A_LOAD
```

В v1 control word нет independent `FLAGS_LOAD` bit. Control-word bit 13 reserved.

Допустимость значений flags:

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

## Связанные решения и документы

- [ISA R8 v1](../isa.md) определяет обновление FLAGS для инструкций.
- [Control Word](../control-word.md) фиксирует связь `E_A` и FLAGS latch.
- [ADR-0010](0010-deterministic-software-model-semantics.md) определяет software `flags_defined_mask`.
