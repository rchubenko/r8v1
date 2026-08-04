# ADR-0007: Exclusive SRAM Ownership

## Status

Accepted

## Контекст

Raspberry Pi должен загружать и inspect memory, а autonomous CPU — владеть той же SRAM во время execution. Прямое соединение masters создаёт риск contention и unintended writes.

## Решение

Реализовать explicit exclusive ownership между CPU и Pi.

Ownership switching управляет address, data и write-related signals. Переключение выполняется только при active reset и использует break-before-make.

## Последствия

Положительные:

- безопасная загрузка program;
- deterministic CPU execution;
- возможна read-back verification;
- при корректной реализации нет shared-output contention.

Отрицательные:

- требуются multiplexers или tri-state arbitration;
- loader workflow должен соблюдать strict sequencing;
- ownership switching не должен вызывать glitch SRAM write controls.
