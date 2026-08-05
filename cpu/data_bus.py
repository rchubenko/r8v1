"""Stateless 8-bit DATA BUS resolution for R8 v1."""

from collections.abc import Iterable

from .values import validate_byte


class DataBusContention(RuntimeError):
    """Raised when multiple producers attempt to drive the DATA BUS."""


def resolve_data_bus(producers: Iterable[object]) -> int | None:
    """Resolve zero, one, or multiple validated DATA BUS producers."""

    values = tuple(validate_byte(producer) for producer in producers)
    if not values:
        return None
    if len(values) > 1:
        formatted_values = ", ".join(f"{value:#04x}" for value in values)
        raise DataBusContention(
            f"DATA BUS contention: {len(values)} producers drive the bus ({formatted_values})"
        )
    return values[0]
