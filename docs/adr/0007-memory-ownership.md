# ADR-0007: Исключительное владение SRAM

## Статус

Принято

## Контекст

Raspberry Pi должен загружать и проверять memory, а autonomous CPU — владеть той же SRAM во время execution. Прямое соединение masters создаёт риск contention и unintended writes.

## Решение

Реализовать явное исключительное владение между CPU и Pi.

Ownership switching управляет address, data и write-related signals. Переключение выполняется только при active reset и использует break-before-make.

## Последствия

Положительные:

- безопасная загрузка program;
- deterministic CPU execution;
- возможна read-back verification;
- при корректной реализации нет shared-output contention.

Отрицательные:

- требуются multiplexers или tri-state arbitration;
- loader workflow должен соблюдать строгую последовательность;
- ownership switching не должен вызывать glitch SRAM write controls.
