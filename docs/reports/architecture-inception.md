# Отчёт об архитектурном inception

## Статус

Завершён после устранения конфликта дублирующего ADR-0005 и утверждения детерминированной семантики программных моделей.

## Результат

Активный архитектурный пакет R8 v1 внутренне согласован для Repository Foundation и последующей программной roadmap CPU.

Следующие ранее открытые вопросы утверждены как нормативные через ADR-0010 и соответствующие основные документы:

- физические значения flags и `flags_defined_mask`;
- строгая и hardware-like обработка undefined conditional flags;
- представление `HIGH_Z` и проверка DATA BUS producer/consumer;
- canonical neutral HALT control word и поведение rising edge;
- modulo-4096 PC и fetch через границу address space;
- zero-initialized software SRAM и executable images ровно 4096 bytes.

## Оставшиеся решения

Ни одно неразрешённое решение не блокирует Milestone 0 или component models Milestone 1.

Синтаксис исходных файлов assembler, выбранный язык и toolchain реализации, timing physical SRAM, reset circuitry и Raspberry Pi loader wiring остаются решениями будущих milestones. Они должны быть определены до начала затронутой реализации.

## Hardware status

`NOT_TESTED` — на этом этапе есть только спецификации и планирование репозитория.
