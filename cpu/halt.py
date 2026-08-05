"""HALT latch model for R8 v1."""


class HaltLatch:
    """A standalone boolean latch that remains set until reset."""

    def __init__(self) -> None:
        self._is_halted = False

    @property
    def is_halted(self) -> bool:
        """Return whether the HALT state is latched."""

        return self._is_halted

    def latch(self) -> None:
        """Set the HALT state and leave it set until reset."""

        self._is_halted = True

    def reset(self) -> None:
        """Clear only this HALT latch."""

        self._is_halted = False
