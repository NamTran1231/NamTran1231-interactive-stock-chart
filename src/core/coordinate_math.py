"""[P06] Coordinate Math — Affine World <-> Screen Transform, Zoom & Pan (Medium).

Run tests:
    pytest -m p06

Design Pattern — Prototype (Creational, idiomatic Python):
    `ViewportState` is an immutable frozen dataclass. `zoom_at_pixel` and
    `pan_by_pixels` clone it with `dataclasses.replace(self._viewport, ...)`
    instead of mutating in place, so `CommandHistory` can store Undo/Redo
    viewport snapshots safely without a separate `clone()` interface.

Problem:
    Implement `ViewportState` plot-area bounds and `CoordinateTransformer` to
    map between financial world coordinates `(candle_index, price)` and PyQt
    screen pixels `(x_px, y_px)` (where screen Y increases downward), plus
    cursor-anchored zoom and horizontal pixel pan.

Constraints:
    - Plot rectangle:
      `plot_left = float(padding_left)`
      `plot_right = max(plot_left + 1.0, float(width_px - padding_right))`
      `plot_top = float(padding_top)`
      `plot_bottom = max(plot_top + 1.0, float(height_px - padding_bottom))`
      `plot_width = max(1.0, plot_right - plot_left)`
      `plot_height = max(1.0, plot_bottom - plot_top)`
    - Axis mapping:
      - `start_idx -> plot_left`, `end_idx -> plot_right`.
      - `max_price -> plot_top`, `min_price -> plot_bottom` (inverted Y).
      - Invertibility: `screen_to_world(*world_to_screen(i, p)) == (i, p)`
        within `1e-9` for non-degenerate viewports.
    - Degenerate inputs (`start_idx == end_idx`, `min_price == max_price`,
      `width_px <= 0`, `height_px <= 0`) must NEVER raise `ZeroDivisionError`;
      degenerate world spans map to the plot center.
    - `zoom_at_pixel(anchor_x, zoom_factor, min_span=5.0, max_span=100000.0)`:
      - `zoom_factor <= 0` (or non-finite), `min_span <= 0`, or
        `min_span > max_span` raises `ValueError`.
      - `zoom_factor > 1.0` zooms IN (`new_span = clamp(old_span / zoom_factor)`).
      - Invariant: `x_to_index(anchor_x)` is unchanged before and after zoom
        (when unclamped).
    - `pan_by_pixels(dx_px)`: dragging right (`dx_px > 0`) shifts the visible
      window earlier in time (decreases `start_idx` and `end_idx`).
    - All methods run in O(1).

Example:
    >>> vp = ViewportState(0.0, 100.0, 50.0, 150.0, 884, 444)
    >>> ct = CoordinateTransformer(vp)
    >>> ct.screen_to_world(*ct.world_to_screen(25.0, 125.0))
    (25.0, 125.0)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ViewportState:
    """Immutable chart viewport rectangle and visible world bounds."""

    start_idx: float
    end_idx: float
    min_price: float
    max_price: float
    width_px: int
    height_px: int
    padding_left: int = 12
    padding_right: int = 72
    padding_top: int = 16
    padding_bottom: int = 28

    @property
    def plot_left(self) -> float:
        """Left pixel edge of the candle plot area (O(1))."""
        raise NotImplementedError("TODO(P06): implement ViewportState.plot_left")

    @property
    def plot_right(self) -> float:
        """Right pixel edge of the plot area, guaranteed >= plot_left + 1.0 (O(1))."""
        raise NotImplementedError("TODO(P06): implement ViewportState.plot_right")

    @property
    def plot_top(self) -> float:
        """Top pixel edge of the candle plot area (O(1))."""
        raise NotImplementedError("TODO(P06): implement ViewportState.plot_top")

    @property
    def plot_bottom(self) -> float:
        """Bottom pixel edge of the plot area, guaranteed >= plot_top + 1.0 (O(1))."""
        raise NotImplementedError("TODO(P06): implement ViewportState.plot_bottom")

    @property
    def plot_width(self) -> float:
        """Effective plot width in pixels, guaranteed >= 1.0 (O(1))."""
        raise NotImplementedError("TODO(P06): implement ViewportState.plot_width")

    @property
    def plot_height(self) -> float:
        """Effective plot height in pixels, guaranteed >= 1.0 (O(1))."""
        raise NotImplementedError("TODO(P06): implement ViewportState.plot_height")


class CoordinateTransformer:
    """Affine converter between world `(index, price)` and screen `(x_px, y_px)`."""

    def __init__(self, viewport: ViewportState) -> None:
        """Store `viewport`."""
        raise NotImplementedError("TODO(P06): implement CoordinateTransformer.__init__")

    @property
    def viewport(self) -> ViewportState:
        """Return the underlying `ViewportState`."""
        raise NotImplementedError("TODO(P06): implement CoordinateTransformer.viewport")

    def index_to_x(self, index: float) -> float:
        """Map world `index` to screen `x_px` without dividing by zero (O(1))."""
        raise NotImplementedError("TODO(P06): implement CoordinateTransformer.index_to_x")

    def x_to_index(self, x_px: float) -> float:
        """Map screen `x_px` back to world `index` (O(1))."""
        raise NotImplementedError("TODO(P06): implement CoordinateTransformer.x_to_index")

    def price_to_y(self, price: float) -> float:
        """Map world `price` to inverted screen `y_px` without dividing by zero (O(1))."""
        raise NotImplementedError("TODO(P06): implement CoordinateTransformer.price_to_y")

    def y_to_price(self, y_px: float) -> float:
        """Map screen `y_px` back to world `price` (O(1))."""
        raise NotImplementedError("TODO(P06): implement CoordinateTransformer.y_to_price")

    def world_to_screen(self, index: float, price: float) -> tuple[float, float]:
        """Map `(index, price)` -> `(x_px, y_px)` (O(1))."""
        raise NotImplementedError("TODO(P06): implement CoordinateTransformer.world_to_screen")

    def screen_to_world(self, x_px: float, y_px: float) -> tuple[float, float]:
        """Map `(x_px, y_px)` -> `(index, price)` (O(1))."""
        raise NotImplementedError("TODO(P06): implement CoordinateTransformer.screen_to_world")

    def zoom_at_pixel(
        self,
        anchor_x: float,
        zoom_factor: float,
        min_span: float = 5.0,
        max_span: float = 100000.0,
    ) -> ViewportState:
        """Return a new `ViewportState` zoomed around `anchor_x` (`zoom_factor > 1` zooms in)."""
        raise NotImplementedError("TODO(P06): implement CoordinateTransformer.zoom_at_pixel")

    def pan_by_pixels(self, dx_px: float) -> ViewportState:
        """Return a new `ViewportState` panned horizontally by `dx_px` pixels."""
        raise NotImplementedError("TODO(P06): implement CoordinateTransformer.pan_by_pixels")


__all__ = [
    "ViewportState",
    "CoordinateTransformer",
]
