# ADR-0002: Software-First Co-Design

## Status

Accepted

## Контекст

Создание hardware первым делает архитектурные ошибки дорогими. Независимое создание software и hardware создаёт риск divergence.

## Решение

Разработать complete software CPU до hardware integration, используя две models:

1. ISA reference emulator;
2. microarchitecture simulator, управляемый real control words и microsteps.

После установления software parity последовательно заменять coherent software subsystems hardware backends.

## Последствия

Положительные:

- executable architectural reference существует до wiring;
- microcode тестируется до EEPROM programming;
- hybrid integration повторно использует те же control definitions;
- hardware failures можно сравнивать с deterministic expected state.

Отрицательные:

- до первого hardware milestone требуется больше software work;
- interfaces нужно тщательно сопоставлять с physical boundaries;
- simulator не должен скрывать timing и contention rules.
