from collections import deque
import threading


class RingBuffer:

    def __init__(self, max_size: int):
        """Initialize a ring buffer with a fixed maximum size.

        - max_size: The maximum number of elements the buffer can hold.
        """
        self.max_size = max_size

        # Use deque with the maxlen attribute.
        # When the buffer is full, the oldest element at the head
        # is automatically evicted when a new element is appended.
        self._buffer = deque(maxlen=max_size)

        # Create a Lock for thread-safe data access.
        self._lock = threading.Lock()

    def append(self, item) -> None:
        """Append a new item to the buffer (automatically overwrites if full)."""
        with self._lock:
            self._buffer.append(item)

    def get_all(self) -> list:
        """Return all current data in the buffer as a list."""
        with self._lock:
            return list(self._buffer)

    def clear(self) -> None:
        """Clear all data in the buffer."""
        with self._lock:
            self._buffer.clear()

    @property
    def size(self) -> int:
        """Return the current number of elements in the buffer."""
        with self._lock:
            return len(self._buffer)

    @property
    def is_full(self) -> bool:
        """"Check whether the buffer is full (reached maximum size)."""
        with self._lock:
            return len(self._buffer) == self.max_size
