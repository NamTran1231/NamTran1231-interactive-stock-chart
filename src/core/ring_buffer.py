"""Fixed-capacity circular storage for recent candles."""

from src.core.candle import Candle


class RingBuffer:
    """Retain the most recent pushes in a preallocated array."""

    def __init__(self, capacity: int) -> None:
        if type(capacity) is not int or capacity <= 0:
            raise ValueError("Ring Buffer capacity must be a positive integer")
        self._capacity = capacity
        self._slots: list[Candle | None] = [None] * capacity
        self._next = 0
        self._size = 0

    def push(self, candle: Candle) -> None:
        """Store a candle in O(1), overwriting the oldest when full."""
        self._slots[self._next] = candle
        self._next = (self._next + 1) % self._capacity
        self._size = min(self._size + 1, self._capacity)

    def get_all(self) -> list[Candle]:
        """Return an independent oldest-to-newest snapshot in O(K)."""
        oldest = (self._next - self._size) % self._capacity
        result = []
        for offset in range(self._size):
            candle = self._slots[(oldest + offset) % self._capacity]
            assert candle is not None
            result.append(candle)
        return result

    def is_full(self) -> bool:
        return self._size == self._capacity

    def clear(self) -> None:
        """Release the K retained references and reset the write position in O(K)."""
        oldest = (self._next - self._size) % self._capacity
        for offset in range(self._size):
            self._slots[(oldest + offset) % self._capacity] = None
        self._next = 0
        self._size = 0
