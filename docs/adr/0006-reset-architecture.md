# ADR-0006: Архитектура RESET

## Статус

Принято

## Контекст

Reset должен работать даже когда clock, microcode или HALT state не продвигаются. Control-word reset bit зависел бы от работающего CU.

## Решение

Reset — отдельный system signal, не часть control word.

Источники:

- power-on circuit;
- manual button;
- Raspberry Pi.

Поведение:

- asynchronous assertion;
- synchronized release;
- priority над HALT и normal execution.

## Последствия

Положительные:

- deterministic startup;
- надёжное восстановление после bad microcode или HALT;
- automated hardware tests могут перезапустить CPU.

Отрицательные:

- требуется reset-conditioning hardware;
- все stateful devices должны поддерживать reset или external initialization logic.

## Связанные решения и документы

- [Архитектура R8 v1](../architecture.md) задаёт reset values и priority.
- [Микроархитектура](../microarchitecture.md) описывает reset относительно clock и HALT.
