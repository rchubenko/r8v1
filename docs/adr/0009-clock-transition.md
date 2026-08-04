# ADR-0009: Clock Transition Strategy

## Status

Accepted

## Контекст

Hybrid operation требует deterministic control-signal setup перед каждым clock edge. Linux на Raspberry Pi не может безопасно управлять microcode при free-running clock.

## Решение

- С самого начала проектировать common `CPU_CLK_IN` и clock distribution network.
- Использовать Raspberry Pi single-step clock во время bring-up и hybrid execution.
- Добавить autonomous clock после готовности EEPROM CU и hardware microstep counter.
- Выбирать debug или autonomous source через explicit hardware selection.
- Менять clock source только при active reset.

## Последствия

Положительные:

- deterministic hybrid testing;
- нет race между Pi control updates и free-running clock;
- autonomous clock integration не требует rewiring всех registers.

Отрицательные:

- final performance testing происходит поздно;
- всё ещё требуются clock-source selection и conditioning hardware.
