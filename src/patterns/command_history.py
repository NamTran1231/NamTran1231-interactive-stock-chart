"""[P11] Command & CommandHistory — Undo/Redo Stack Pattern (Easy).

Run tests:
    pytest -m p11

Design Pattern — Command (Behavioral) + Dependency Injection (NO Singleton):
    Encapsulates pan/zoom viewport transitions as undoable objects paired with
    immutable `ViewportState` snapshots (Prototype pattern).

Constraints:
    - `ViewportChangeCommand(apply_fn, old_viewport, new_viewport, description=...)`:
      - Raises `TypeError` if `apply_fn` is not callable.
      - `execute()` invokes `apply_fn(new_viewport)`.
      - `undo()` invokes `apply_fn(old_viewport)`.
    - `CommandHistory(max_size=100)`:
      - `max_size` must be a real `int >= 1` (`TypeError` for `bool`/non-`int`,
        `ValueError` for `< 1`).
      - `execute(cmd)`: runs `cmd.execute()`, pushes to undo stack, drops oldest
        entries if `len > max_size`, and clears the redo stack.
      - `undo()` / `redo()`: return `None` when respective stack is empty;
        otherwise execute/undo, move command between stacks, and return it.
      - `__len__()` returns current undo stack depth.

Example:
    >>> history = CommandHistory(max_size=50)
    >>> history.can_undo(), history.can_redo()
    (False, False)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from src.core.coordinate_math import ViewportState


class Command(ABC):
    """Abstract undoable command."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable label for this command."""

    @abstractmethod
    def execute(self) -> None:
        """Apply (or re-apply on Redo) the command."""

    @abstractmethod
    def undo(self) -> None:
        """Revert the effect of `execute()`."""


class ViewportChangeCommand(Command):
    """Undoable viewport transition command."""

    def __init__(
        self,
        apply_fn: Callable[[ViewportState], None],
        old_viewport: ViewportState,
        new_viewport: ViewportState,
        description: str = "Viewport Change",
    ) -> None:
        """Store `apply_fn` (must be callable) and old/new viewport snapshots."""
        raise NotImplementedError("TODO(P11): implement ViewportChangeCommand.__init__")

    @property
    def description(self) -> str:
        """Return command description."""
        raise NotImplementedError("TODO(P11): implement ViewportChangeCommand.description")

    @property
    def old_viewport(self) -> ViewportState:
        """Return viewport snapshot before execution."""
        raise NotImplementedError("TODO(P11): implement ViewportChangeCommand.old_viewport")

    @property
    def new_viewport(self) -> ViewportState:
        """Return viewport snapshot after execution."""
        raise NotImplementedError("TODO(P11): implement ViewportChangeCommand.new_viewport")

    def execute(self) -> None:
        """Apply `new_viewport` via `apply_fn`."""
        raise NotImplementedError("TODO(P11): implement ViewportChangeCommand.execute")

    def undo(self) -> None:
        """Restore `old_viewport` via `apply_fn`."""
        raise NotImplementedError("TODO(P11): implement ViewportChangeCommand.undo")


class CommandHistory:
    """Bounded Undo/Redo stack manager."""

    def __init__(self, max_size: int = 100) -> None:
        """Initialize empty undo/redo stacks with positive `max_size`."""
        raise NotImplementedError("TODO(P11): implement CommandHistory.__init__")

    @property
    def max_size(self) -> int:
        """Return maximum undo history capacity."""
        raise NotImplementedError("TODO(P11): implement CommandHistory.max_size")

    def execute(self, cmd: Command) -> None:
        """Execute `cmd`, record on undo stack (bounded by `max_size`), and clear redo."""
        raise NotImplementedError("TODO(P11): implement CommandHistory.execute")

    def undo(self) -> Command | None:
        """Undo and return the most recent command, or None if empty."""
        raise NotImplementedError("TODO(P11): implement CommandHistory.undo")

    def redo(self) -> Command | None:
        """Redo and return the most recently undone command, or None if empty."""
        raise NotImplementedError("TODO(P11): implement CommandHistory.redo")

    def can_undo(self) -> bool:
        """Return True iff undo stack is non-empty (O(1))."""
        raise NotImplementedError("TODO(P11): implement CommandHistory.can_undo")

    def can_redo(self) -> bool:
        """Return True iff redo stack is non-empty (O(1))."""
        raise NotImplementedError("TODO(P11): implement CommandHistory.can_redo")

    def clear(self) -> None:
        """Empty both undo and redo stacks."""
        raise NotImplementedError("TODO(P11): implement CommandHistory.clear")

    def __len__(self) -> int:
        """Return number of commands currently on the undo stack (O(1))."""
        raise NotImplementedError("TODO(P11): implement CommandHistory.__len__")
