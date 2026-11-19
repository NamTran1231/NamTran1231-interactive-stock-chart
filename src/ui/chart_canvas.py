"""Pre-built PyQt6 candlestick chart canvas (DO NOT EDIT for P01-P11).

Integrates student DSA & Pattern modules (`SegmentTree`, `CoordinateTransformer`,
`SlidingWindowIndicators`, `LTTBDecimator`, `aggregate_ohlcv_buckets`, `QuadTree`,
`EventBus`, `CommandHistory`) into a 60 FPS dark-theme `QPainter` widget with a
100% headless `compute_visible_frame()` pipeline for pytest verification.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import math
from typing import Any, Sequence

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPen,
    QPolygonF,
    QResizeEvent,
    QWheelEvent,
)
from PyQt6.QtWidgets import QSizePolicy, QWidget

from src.algorithms.lttb_decimator import LTTBDecimator, aggregate_ohlcv_buckets
from src.algorithms.monotonic_deque import SlidingWindowIndicators
from src.algorithms.quad_tree import Bounds, QuadTree, SpatialPoint
from src.algorithms.segment_tree import RangeStats, SegmentTree
from src.core.candle import Candle
from src.core.coordinate_math import CoordinateTransformer, ViewportState
from src.patterns.command_history import CommandHistory, ViewportChangeCommand
from src.patterns.observer import EventBus

BG_COLOR = QColor("#131722")
PANEL_BG_COLOR = QColor("#1e222d")
GRID_COLOR = QColor("#1f2430")
AXIS_BORDER_COLOR = QColor("#2a2e39")
TEXT_MUTED_COLOR = QColor("#787b86")
TEXT_PRIMARY_COLOR = QColor("#d1d4dc")
BULL_COLOR = QColor("#26a69a")
BEAR_COLOR = QColor("#ef5350")
BULL_VOL_COLOR = QColor(38, 166, 154, 75)
BEAR_VOL_COLOR = QColor(239, 83, 80, 75)
SMA_COLOR = QColor("#f7931a")
DONCHIAN_BAND_COLOR = QColor(41, 98, 255, 190)
DONCHIAN_MID_COLOR = QColor(255, 152, 0, 170)
DONCHIAN_FILL_COLOR = QColor(41, 98, 255, 22)
CROSSHAIR_COLOR = QColor("#787b86")


@dataclass(frozen=True)
class VisibleFrame:
    """Headless snapshot of geometry and indicators computed for one paint frame."""

    viewport: ViewportState
    range_stats: RangeStats | None
    render_candles: list[Candle]
    candle_indices: list[float]
    sma_points: list[tuple[float, float]]
    donchian_upper: list[tuple[float, float]]
    donchian_middle: list[tuple[float, float]]
    donchian_lower: list[tuple[float, float]]
    decimated_close_points: list[tuple[float, float]]
    total_candles: int
    start_idx: int
    end_idx: int


def _padded_price_bounds(min_low: float, max_high: float) -> tuple[float, float]:
    span = max_high - min_low
    pad = max(abs(max_high) * 0.01, 0.5) if span < 1e-9 else span * 0.06
    return min_low - pad, max_high + pad


def _format_timestamp(ts: float | int) -> str:
    return datetime.fromtimestamp(float(ts), tz=timezone.utc).strftime("%m-%d %H:%M")


def _format_price(price: float) -> str:
    return f"{price:,.2f}"


def _format_volume(volume: float) -> str:
    if volume >= 1e9:
        return f"{volume / 1e9:.2f}B"
    if volume >= 1e6:
        return f"{volume / 1e6:.2f}M"
    if volume >= 1e3:
        return f"{volume / 1e3:.2f}K"
    return f"{volume:.1f}"


class ChartCanvasWidget(QWidget):
    """Interactive PyQt6 OHLCV candlestick canvas powered by custom DSA structures."""

    def __init__(
        self,
        event_bus: EventBus | None = None,
        command_history: CommandHistory | None = None,
        sma_window: int = 20,
        donchian_window: int = 20,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setMinimumSize(320, 200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._event_bus = event_bus if event_bus is not None else EventBus()
        self._command_history = command_history if command_history is not None else CommandHistory()
        self._sma_window = max(1, sma_window)
        self._donchian_window = max(1, donchian_window)

        self._candles: list[Candle] = []
        self._segment_tree = SegmentTree()
        self._quad_tree: QuadTree[int] | None = None
        self._last_frame: VisibleFrame | None = None

        self._viewport = ViewportState(
            start_idx=0.0,
            end_idx=50.0,
            min_price=0.0,
            max_price=100.0,
            width_px=800,
            height_px=500,
        )
        self.show_sma = True
        self.show_donchian = True
        self.show_volume = True

        self._is_panning = False
        self._pan_start_x = 0.0
        self._pan_start_viewport: ViewportState | None = None
        self._hover_pos: tuple[float, float] | None = None
        self._hover_idx: int | None = None

    @property
    def event_bus(self) -> EventBus:
        return self._event_bus

    @property
    def command_history(self) -> CommandHistory:
        return self._command_history

    @property
    def candles(self) -> list[Candle]:
        return list(self._candles)

    @property
    def last_frame(self) -> VisibleFrame | None:
        return self._last_frame

    def set_candles(self, candles: Sequence[Candle], fit: bool = True) -> None:
        self._candles = list(candles)
        self._segment_tree = SegmentTree(self._candles)
        self._quad_tree = None
        self._last_frame = None
        self._hover_pos = None
        self._hover_idx = None

        if fit:
            self.fit_all(record_history=False)
        else:
            self._apply_viewport(self._auto_scale_y(self._viewport))
        self._event_bus.publish("candles_loaded", len(self._candles))
        self.update()

    def append_or_update_candle(self, candle: Candle, auto_follow: bool = True) -> str:
        if self._candles and candle.timestamp == self._candles[-1].timestamp:
            idx = len(self._candles) - 1
            self._candles[idx] = candle
            self._segment_tree.update(idx, candle)
            mode = "updated"
        else:
            idx = len(self._candles)
            self._candles.append(candle)
            self._segment_tree.append(candle)
            mode = "appended"
            if auto_follow:
                span = max(10.0, self._viewport.end_idx - self._viewport.start_idx)
                end = max(float(idx) + 1.0, span) if len(self._candles) < span else float(idx) + 1.0
                start = max(0.0, end - span)
                self._viewport = replace(self._viewport, start_idx=start, end_idx=end)

        self._viewport = self._auto_scale_y(self._viewport)
        stats = self.get_visible_range_stats()
        self._event_bus.publish("candle_updated", mode, idx, candle)
        self._event_bus.publish("viewport_changed", self._viewport, stats)
        self.update()
        return mode

    def set_viewport(
        self,
        viewport: ViewportState,
        record_history: bool = False,
        description: str = "Viewport Change",
    ) -> None:
        if record_history:
            cmd = ViewportChangeCommand(self._apply_viewport, self._viewport, viewport, description)
            self._command_history.execute(cmd)
            self._event_bus.publish("history_changed")
        else:
            self._apply_viewport(viewport)

    def _apply_viewport(self, viewport: ViewportState) -> None:
        self._viewport = viewport
        stats = self.get_visible_range_stats()
        self._event_bus.publish("viewport_changed", self._viewport, stats)
        self.update()

    def get_viewport(self) -> ViewportState:
        return self._viewport

    def fit_all(self, record_history: bool = False) -> None:
        n = len(self._candles)
        end_idx = float(max(n - 1, 1)) + 0.5 if n > 0 else 50.0
        start_idx = -0.5 if n > 0 else 0.0
        w = max(1, self.width()) if self.width() > 0 else self._viewport.width_px
        h = max(1, self.height()) if self.height() > 0 else self._viewport.height_px
        vp = replace(self._viewport, start_idx=start_idx, end_idx=end_idx, width_px=w, height_px=h)
        vp = self._auto_scale_y(vp)
        self.set_viewport(vp, record_history=record_history, description="Fit All")

    def set_overlays(
        self,
        *,
        sma: bool | None = None,
        donchian: bool | None = None,
        volume: bool | None = None,
    ) -> None:
        if sma is not None:
            self.show_sma = bool(sma)
        if donchian is not None:
            self.show_donchian = bool(donchian)
        if volume is not None:
            self.show_volume = bool(volume)
        self.update()

    def _visible_index_bounds(self, vp: ViewportState) -> tuple[int, int]:
        n = len(self._candles)
        if n == 0:
            return 0, -1
        s_idx = max(0, min(n - 1, math.floor(vp.start_idx)))
        e_idx = max(0, min(n - 1, math.ceil(vp.end_idx)))
        return (s_idx, e_idx) if s_idx <= e_idx else (0, -1)

    def get_visible_range_stats(self) -> RangeStats | None:
        s_idx, e_idx = self._visible_index_bounds(self._viewport)
        if e_idx < s_idx:
            return None
        return self._segment_tree.query(s_idx, e_idx + 1)

    def _auto_scale_y(self, vp: ViewportState) -> ViewportState:
        s_idx, e_idx = self._visible_index_bounds(vp)
        if e_idx < s_idx:
            return vp
        stats = self._segment_tree.query(s_idx, e_idx + 1)
        if stats is None:
            return vp
        min_p, max_p = _padded_price_bounds(stats.min_low, stats.max_high)
        return replace(vp, min_price=min_p, max_price=max_p)

    def compute_visible_frame(
        self,
        width_px: int | None = None,
        height_px: int | None = None,
        max_render_candles: int = 300,
    ) -> VisibleFrame:
        if isinstance(max_render_candles, bool) or not isinstance(max_render_candles, int) or max_render_candles < 1:
            raise ValueError("max_render_candles must be a positive integer")

        w = width_px if width_px is not None else (self.width() if self.width() > 0 else self._viewport.width_px)
        h = height_px if height_px is not None else (self.height() if self.height() > 0 else self._viewport.height_px)
        vp = replace(self._viewport, width_px=max(1, w), height_px=max(1, h))

        n = len(self._candles)
        if n == 0:
            frame = VisibleFrame(vp, None, [], [], [], [], [], [], [], 0, 0, -1)
            self._quad_tree = None
            self._last_frame = frame
            return frame

        s_idx, e_idx = self._visible_index_bounds(vp)
        range_stats = self._segment_tree.query(s_idx, e_idx + 1)
        if range_stats is not None:
            min_p, max_p = _padded_price_bounds(range_stats.min_low, range_stats.max_high)
            vp = replace(vp, min_price=min_p, max_price=max_p)

        # Warm-up prefix so SMA and Donchian have values at the left viewport edge.
        warmup = max(self._sma_window, self._donchian_window) - 1
        slice_start = max(0, s_idx - warmup)
        window_candles = self._candles[slice_start : e_idx + 1]
        closes = [c.close for c in window_candles]

        sma_vals = SlidingWindowIndicators.sma(closes, self._sma_window)
        donchian_vals = SlidingWindowIndicators.donchian_channels(window_candles, self._donchian_window)

        offset = s_idx - slice_start
        sma_points: list[tuple[float, float]] = []
        don_upper: list[tuple[float, float]] = []
        don_mid: list[tuple[float, float]] = []
        don_lower: list[tuple[float, float]] = []
        for rel_i in range(offset, len(window_candles)):
            world_i = float(slice_start + rel_i)
            s_val = sma_vals[rel_i]
            if s_val is not None:
                sma_points.append((world_i, s_val))
            u, m, lo = donchian_vals[rel_i]
            don_upper.append((world_i, u))
            don_mid.append((world_i, m))
            don_lower.append((world_i, lo))

        visible_count = e_idx - s_idx + 1
        raw_close_pts = [(float(i), self._candles[i].close) for i in range(s_idx, e_idx + 1)]
        if visible_count > max_render_candles:
            render_candles = aggregate_ohlcv_buckets(self._candles, s_idx, e_idx + 1, max_render_candles)
            bucket_step = visible_count / len(render_candles)
            candle_indices = [s_idx + (k + 0.5) * bucket_step for k in range(len(render_candles))]
            decimated_close = LTTBDecimator.downsample(raw_close_pts, max_render_candles)
        else:
            render_candles = list(self._candles[s_idx : e_idx + 1])
            candle_indices = [float(i) for i in range(s_idx, e_idx + 1)]
            decimated_close = raw_close_pts

        transformer = CoordinateTransformer(vp)
        bounds = Bounds(vp.plot_left, vp.plot_top, vp.plot_right, vp.plot_bottom)
        qt: QuadTree[int] = QuadTree(bounds)
        for local_i, (c_idx, candle) in enumerate(zip(candle_indices, render_candles)):
            x_px, y_px = transformer.world_to_screen(c_idx, candle.close)
            clamped_x = max(vp.plot_left, min(vp.plot_right, x_px))
            clamped_y = max(vp.plot_top, min(vp.plot_bottom, y_px))
            qt.insert(SpatialPoint(clamped_x, clamped_y, local_i))
        self._quad_tree = qt

        frame = VisibleFrame(
            viewport=vp,
            range_stats=range_stats,
            render_candles=render_candles,
            candle_indices=candle_indices,
            sma_points=sma_points,
            donchian_upper=don_upper,
            donchian_middle=don_mid,
            donchian_lower=don_lower,
            decimated_close_points=decimated_close,
            total_candles=n,
            start_idx=s_idx,
            end_idx=e_idx,
        )
        self._last_frame = frame
        return frame

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._viewport = replace(
            self._viewport,
            width_px=max(1, event.size().width()),
            height_px=max(1, event.size().height()),
        )
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_panning = True
            self._pan_start_x = event.position().x()
            self._pan_start_viewport = self._viewport
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = event.position()
        if self._is_panning and self._pan_start_viewport is not None:
            dx = pos.x() - self._pan_start_x
            panned = CoordinateTransformer(self._pan_start_viewport).pan_by_pixels(dx)
            self._apply_viewport(self._auto_scale_y(panned))
        else:
            self._hover_pos = (pos.x(), pos.y())
            snapped_candle: Candle | None = None
            snapped_idx: float | None = None
            if self._quad_tree is not None and self._last_frame is not None:
                nearest = self._quad_tree.nearest(pos.x(), pos.y(), max_dist=60.0)
                if nearest is not None and 0 <= nearest.payload < len(self._last_frame.render_candles):
                    self._hover_idx = nearest.payload
                    snapped_candle = self._last_frame.render_candles[nearest.payload]
                    snapped_idx = self._last_frame.candle_indices[nearest.payload]
                else:
                    self._hover_idx = None
            self._event_bus.publish("hover_candle_changed", snapped_candle, snapped_idx)
            self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._is_panning:
            self._is_panning = False
            self.unsetCursor()
            old_vp = self._pan_start_viewport
            self._pan_start_viewport = None
            if old_vp is not None and old_vp != self._viewport:
                new_vp = self._viewport
                self._viewport = old_vp
                self.set_viewport(new_vp, record_history=True, description="Pan Chart")
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        delta = event.angleDelta().y()
        if delta == 0:
            return
        factor = 1.15 if delta > 0 else (1.0 / 1.15)
        zoomed = CoordinateTransformer(self._viewport).zoom_at_pixel(event.position().x(), factor)
        self.set_viewport(self._auto_scale_y(zoomed), record_history=True, description="Zoom Chart")
        event.accept()

    def leaveEvent(self, event: Any) -> None:
        self._hover_pos = None
        self._hover_idx = None
        self._event_bus.publish("hover_candle_changed", None, None)
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.fillRect(self.rect(), BG_COLOR)

        frame = self.compute_visible_frame(self.width(), self.height())
        if frame.total_candles == 0 or not frame.render_candles:
            painter.setPen(TEXT_MUTED_COLOR)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No candle data loaded")
            painter.end()
            return

        vp = frame.viewport
        transformer = CoordinateTransformer(vp)
        self._draw_grid_and_axes(painter, frame, transformer)
        if self.show_volume:
            self._draw_volume_bars(painter, frame, transformer)
        if self.show_donchian:
            self._draw_donchian(painter, frame, transformer)
        self._draw_candles(painter, frame, transformer)
        if self.show_sma:
            self._draw_polyline(painter, frame.sma_points, transformer, SMA_COLOR, 1.6)
        self._draw_crosshair(painter, frame, transformer)
        painter.end()

    def _candle_pixel_width(self, frame: VisibleFrame) -> float:
        vp = frame.viewport
        span = max(1.0, vp.end_idx - vp.start_idx)
        return max(1.5, min(18.0, (vp.plot_width / span) * 0.72))

    def _draw_grid_and_axes(
        self, painter: QPainter, frame: VisibleFrame, transformer: CoordinateTransformer
    ) -> None:
        vp = frame.viewport
        painter.setFont(QFont("Sans Serif", 8))
        grid_pen = QPen(GRID_COLOR, 1)

        # Horizontal price grid lines + Y-axis labels
        steps = 5
        for i in range(steps + 1):
            frac = i / steps
            price = vp.min_price + frac * (vp.max_price - vp.min_price)
            y = transformer.price_to_y(price)
            painter.setPen(grid_pen)
            painter.drawLine(QPointF(vp.plot_left, y), QPointF(vp.plot_right, y))
            painter.setPen(TEXT_MUTED_COLOR)
            painter.drawText(
                QRectF(vp.plot_right + 4, y - 8, vp.padding_right - 6, 16),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                _format_price(price),
            )

        # Vertical time grid lines + X-axis labels
        count = len(frame.render_candles)
        x_ticks = min(6, count)
        for k in range(x_ticks):
            pos = int(k * (count - 1) / max(1, x_ticks - 1))
            x = transformer.index_to_x(frame.candle_indices[pos])
            painter.setPen(grid_pen)
            painter.drawLine(QPointF(x, vp.plot_top), QPointF(x, vp.plot_bottom))
            painter.setPen(TEXT_MUTED_COLOR)
            label = _format_timestamp(frame.render_candles[pos].timestamp)
            painter.drawText(
                QRectF(x - 36, vp.plot_bottom + 4, 72, vp.padding_bottom - 4),
                Qt.AlignmentFlag.AlignCenter,
                label,
            )

        painter.setPen(QPen(AXIS_BORDER_COLOR, 1))
        painter.drawRect(QRectF(vp.plot_left, vp.plot_top, vp.plot_width, vp.plot_height))

    def _draw_volume_bars(
        self, painter: QPainter, frame: VisibleFrame, transformer: CoordinateTransformer
    ) -> None:
        vp = frame.viewport
        max_vol = max((c.volume for c in frame.render_candles), default=0.0)
        if max_vol <= 0.0:
            return
        max_bar_h = vp.plot_height * 0.20
        bar_w = self._candle_pixel_width(frame)
        painter.setPen(Qt.PenStyle.NoPen)
        for idx, candle in zip(frame.candle_indices, frame.render_candles):
            x = transformer.index_to_x(idx)
            bar_h = (candle.volume / max_vol) * max_bar_h
            painter.setBrush(BULL_VOL_COLOR if candle.is_bullish else BEAR_VOL_COLOR)
            painter.drawRect(QRectF(x - bar_w / 2.0, vp.plot_bottom - bar_h, bar_w, bar_h))

    def _draw_donchian(
        self, painter: QPainter, frame: VisibleFrame, transformer: CoordinateTransformer
    ) -> None:
        if len(frame.donchian_upper) < 2:
            return
        poly = QPolygonF()
        for idx, price in frame.donchian_upper:
            x, y = transformer.world_to_screen(idx, price)
            poly.append(QPointF(x, y))
        for idx, price in reversed(frame.donchian_lower):
            x, y = transformer.world_to_screen(idx, price)
            poly.append(QPointF(x, y))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(DONCHIAN_FILL_COLOR))
        painter.drawPolygon(poly)

        self._draw_polyline(painter, frame.donchian_upper, transformer, DONCHIAN_BAND_COLOR, 1.1)
        self._draw_polyline(painter, frame.donchian_middle, transformer, DONCHIAN_MID_COLOR, 1.0, dashed=True)
        self._draw_polyline(painter, frame.donchian_lower, transformer, DONCHIAN_BAND_COLOR, 1.1)

    def _draw_polyline(
        self,
        painter: QPainter,
        points: Sequence[tuple[float, float]],
        transformer: CoordinateTransformer,
        color: QColor,
        width: float,
        dashed: bool = False,
    ) -> None:
        if len(points) < 2:
            return
        pen = QPen(color, width)
        if dashed:
            pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        path = QPainterPath()
        x0, y0 = transformer.world_to_screen(*points[0])
        path.moveTo(x0, y0)
        for idx, price in points[1:]:
            x, y = transformer.world_to_screen(idx, price)
            path.lineTo(x, y)
        painter.drawPath(path)

    def _draw_candles(
        self, painter: QPainter, frame: VisibleFrame, transformer: CoordinateTransformer
    ) -> None:
        body_w = self._candle_pixel_width(frame)
        for idx, candle in zip(frame.candle_indices, frame.render_candles):
            color = BULL_COLOR if candle.is_bullish else BEAR_COLOR
            x = transformer.index_to_x(idx)
            y_high = transformer.price_to_y(candle.high)
            y_low = transformer.price_to_y(candle.low)
            y_top = transformer.price_to_y(candle.body_high)
            y_bot = transformer.price_to_y(candle.body_low)

            painter.setPen(QPen(color, 1.2))
            painter.drawLine(QPointF(x, y_high), QPointF(x, y_low))
            painter.setBrush(QBrush(color))
            painter.drawRect(QRectF(x - body_w / 2.0, y_top, body_w, max(1.0, y_bot - y_top)))

    def _draw_crosshair(
        self, painter: QPainter, frame: VisibleFrame, transformer: CoordinateTransformer
    ) -> None:
        if self._hover_pos is None:
            return
        vp = frame.viewport
        hx, hy = self._hover_pos
        if not (vp.plot_left <= hx <= vp.plot_right and vp.plot_top <= hy <= vp.plot_bottom):
            return

        pen = QPen(CROSSHAIR_COLOR, 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawLine(QPointF(hx, vp.plot_top), QPointF(hx, vp.plot_bottom))
        painter.drawLine(QPointF(vp.plot_left, hy), QPointF(vp.plot_right, hy))

        if self._hover_idx is not None and 0 <= self._hover_idx < len(frame.render_candles):
            c = frame.render_candles[self._hover_idx]
            text = (
                f"{_format_timestamp(c.timestamp)}  "
                f"O:{c.open:.2f} H:{c.high:.2f} L:{c.low:.2f} C:{c.close:.2f} V:{_format_volume(c.volume)}"
            )
            box = QRectF(vp.plot_left + 8, vp.plot_top + 6, min(460.0, vp.plot_width - 16), 22)
            painter.fillRect(box, PANEL_BG_COLOR)
            painter.setPen(TEXT_PRIMARY_COLOR)
            painter.drawText(box.adjusted(6, 0, -6, 0), Qt.AlignmentFlag.AlignVCenter, text)
