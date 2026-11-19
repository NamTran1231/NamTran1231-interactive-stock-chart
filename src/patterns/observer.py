"""[P10] EventBus — Thread-Safe Observer / Pub-Sub Pattern (Easy).

Run tests:
    pytest -m p10

Design Pattern — Observer (Behavioral) + Dependency Injection (NO Singleton):
    `EventBus` decouples `ChartCanvasWidget` from `MainWindow`. Do NOT make
    `EventBus` a global Singleton — each window/test instantiates and injects
    its own bus so unit tests stay isolated.

Constraints:
    - `subscribe(event_name, callback)`:
      - Empty `event_name` (or non-`str`) -> `ValueError`; non-callable -> `TypeError`.
      - Deduplicates identical `(event_name, callback)` subscriptions.
      - Returns a zero-arg `unsubscribe()` closure.
    - `unsubscribe(event_name, callback)`:
      - Removes `callback` if registered and returns `True`; returns `False`
        quietly (no error) if missing.
    - `publish(event_name, *args, **kwargs)`:
      - Dispatches to a snapshot of current subscribers (safe if a callback
        subscribes or unsubscribes during dispatch) and returns the number of
        callbacks invoked.
    - Thread-safe via `threading.RLock` (re-entrant so callbacks may mutate
      subscriptions without deadlocking).

Example:
    >>> bus = EventBus()
    >>> seen = []
    >>> unsub = bus.subscribe("tick", lambda p: seen.append(p))
    >>> bus.publish("tick", 101.5)
    1
    >>> unsub()
    >>> bus.listener_count("tick")
    0
"""

from __future__ import annotations

from typing import Any, Callable


class EventBus:
    """Thread-safe Publish/Subscribe event dispatcher."""

    def __init__(self) -> None:
        """Initialize subscriber registry and re-entrant lock."""
        raise NotImplementedError("TODO(P10): implement EventBus.__init__")

    def subscribe(self, event_name: str, callback: Callable[..., Any]) -> Callable[[], None]:
        """Register `callback` for `event_name` (deduplicated) and return an unsubscribe fn."""
        raise NotImplementedError("TODO(P10): implement EventBus.subscribe")

    def unsubscribe(self, event_name: str, callback: Callable[..., Any]) -> bool:
        """Remove `callback` from `event_name`; return True if removed, else False."""
        raise NotImplementedError("TODO(P10): implement EventBus.unsubscribe")

    def publish(self, event_name: str, *args: Any, **kwargs: Any) -> int:
        """Invoke all current listeners for `event_name` and return count invoked."""
        raise NotImplementedError("TODO(P10): implement EventBus.publish")

    def clear(self, event_name: str | None = None) -> None:
        """Clear subscribers for `event_name`, or for all events if `event_name is None`."""
        raise NotImplementedError("TODO(P10): implement EventBus.clear")

    def listener_count(self, event_name: str | None = None) -> int:
        """Return listener count for `event_name`, or total across all events if None."""
        raise NotImplementedError("TODO(P10): implement EventBus.listener_count")
