"""[P03] RingBuffer — Fixed-Capacity O(1) Circular Buffer (Medium).

Run tests:
    pytest -m p03

Problem:
    Implement a generic fixed-capacity circular buffer backed by a fixed-size
    Python `list`. When full, `push(item)` overwrites the oldest element in O(1)
    without shifting elements or reallocating memory.

Rule (checked by AST test):
    DO NOT import `collections` or use `deque` anywhere in this file.

Constraints:
    - `capacity`: real `int` (reject `bool` / non-`int` with `TypeError`) and
      `> 0` (else `ValueError`).
    - `push`, `latest`, `oldest`, `__len__`, `is_full`, `is_empty`,
      `__getitem__(int)`: O(1) worst-case.
    - `get_all`, `__iter__`, `__getitem__(slice)`: O(K) in chronological order
      (oldest -> newest).
    - `__getitem__`: supports negative indices and slices; raises `IndexError`
      when out of bounds and `TypeError` for `bool` or non-`int | slice`.
    - `latest()` / `oldest()` return `None` when empty.

Example:
    >>> rb = RingBuffer[int](3)
    >>> for x in (10, 20, 30, 40): rb.push(x)
    >>> (rb.get_all(), rb.oldest(), rb.latest(), rb[-1])
    ([20, 30, 40], 20, 40, 40)
"""

from __future__ import annotations

from typing import Any, Generic, Iterator, TypeVar, overload

T = TypeVar("T")


class RingBuffer(Generic[T]):
    """Fixed-capacity circular buffer with O(1) overwrite-on-full push."""

    def __init__(self, capacity: int) -> None:
        """Allocate a fixed-capacity ring buffer (`capacity > 0`)."""
        raise NotImplementedError("TODO(P03): implement RingBuffer.__init__")

    @property
    def capacity(self) -> int:
        """Return maximum number of elements this buffer can hold (O(1))."""
        raise NotImplementedError("TODO(P03): implement RingBuffer.capacity")

    def push(self, item: T) -> None:
        """Append `item`, overwriting the oldest element if full (O(1))."""
        raise NotImplementedError("TODO(P03): implement RingBuffer.push")

    def get_all(self) -> list[T]:
        """Return a shallow list of stored items from oldest to newest (O(K))."""
        raise NotImplementedError("TODO(P03): implement RingBuffer.get_all")

    def latest(self) -> T | None:
        """Return the most recently pushed item, or None if empty (O(1))."""
        raise NotImplementedError("TODO(P03): implement RingBuffer.latest")

    def oldest(self) -> T | None:
        """Return the oldest stored item, or None if empty (O(1))."""
        raise NotImplementedError("TODO(P03): implement RingBuffer.oldest")

    def __len__(self) -> int:
        """Return current number of stored items (O(1))."""
        raise NotImplementedError("TODO(P03): implement RingBuffer.__len__")

    def is_full(self) -> bool:
        """Return True iff len(self) == capacity (O(1))."""
        raise NotImplementedError("TODO(P03): implement RingBuffer.is_full")

    def is_empty(self) -> bool:
        """Return True iff len(self) == 0 (O(1))."""
        raise NotImplementedError("TODO(P03): implement RingBuffer.is_empty")

    def clear(self) -> None:
        """Remove all stored items and reset pointers."""
        raise NotImplementedError("TODO(P03): implement RingBuffer.clear")

    def __iter__(self) -> Iterator[T]:
        """Yield items from oldest to newest."""
        raise NotImplementedError("TODO(P03): implement RingBuffer.__iter__")

    @overload
    def __getitem__(self, index: int) -> T: ...

    @overload
    def __getitem__(self, index: slice) -> list[T]: ...

    def __getitem__(self, index: int | slice) -> Any:
        """Index (including negative indices) or slice logically from oldest to newest."""
        raise NotImplementedError("TODO(P03): implement RingBuffer.__getitem__")

    def __repr__(self) -> str:
        """Return concise debug string such as `RingBuffer(capacity=..., size=...)`."""
        raise NotImplementedError("TODO(P03): implement RingBuffer.__repr__")
