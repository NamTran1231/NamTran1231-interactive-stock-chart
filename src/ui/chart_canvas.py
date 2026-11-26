"""Draw and navigate a small candlestick chart from validated OHLCV data."""

from collections.abc import Sequence
from datetime import datetime, timezone
from math import ceil, floor

from PyQt6.QtCore import QEvent, QLineF, QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QMouseEvent, QPaintEvent, QPainter, QResizeEvent, QWheelEvent
from PyQt6.QtWidgets import QToolTip, QWidget

from src.algorithms.segment_tree import SegmentTree
from src.core.candle import Candle


def utc_label(timestamp: int, *, full: bool = False) -> str:
    try:
        time = datetime.fromtimestamp(timestamp, timezone.utc)
    except (OverflowError, OSError, ValueError):
        return f"{timestamp} s"
    return time.strftime("%Y-%m-%d %H:%M:%S UTC" if full else "%m-%d %H:%M")


class ChartCanvasWidget(QWidget):
    def __init__(self, candles: Sequence[Candle]) -> None:
        super().__init__()
        self._candles = tuple(candles)
        self._price_index = SegmentTree(self._candles)
        # The viewport is measured in candle slots, including fractional slots.
        self._left = 0.0
        self._span = float(len(self._candles))
        self._drag_x: float | None = None
        self.setMouseTracking(True)

    def _plot(self) -> QRectF:
        return QRectF(self.rect()).adjusted(16, 22, -104, -30)

    def _plot_fraction(self, position: QPointF) -> float | None:
        plot = self._plot()
        if (plot.isEmpty() or not plot.left() <= position.x() < plot.right()
                or not plot.top() <= position.y() < plot.bottom()):
            return None
        return (position.x() - plot.left()) / plot.width()

    def _move_view(self, left: float) -> None:
        self._left = max(0.0, min(left, len(self._candles) - self._span))
        self._clear_hover()
        self.update()

    def _clear_hover(self) -> None:
        if self.toolTip():
            self.setToolTip("")
            QToolTip.hideText()

    def wheelEvent(self, event: QWheelEvent) -> None:
        fraction = self._plot_fraction(event.position())
        delta = event.angleDelta().y() or event.pixelDelta().y()
        if not self._candles or fraction is None or not delta:
            event.ignore()
            return
        anchor = self._left + fraction * self._span
        steps = max(-10.0, min(10.0, delta / 120))
        self._span = max(1.0, min(len(self._candles), self._span * 0.8 ** steps))
        self._move_view(anchor - fraction * self._span)
        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if (event.button() == Qt.MouseButton.LeftButton and self._candles
                and self._plot_fraction(event.position()) is not None):
            self._drag_x = event.position().x()
            self._clear_hover()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_x is not None and event.buttons() & Qt.MouseButton.LeftButton:
            x = event.position().x()
            plot = self._plot()
            if not plot.isEmpty():
                self._move_view(self._left + (self._drag_x - x) * self._span / plot.width())
            self._drag_x = x
            return
        self._drag_x = None

        fraction = self._plot_fraction(event.position())
        if fraction is None or not self._candles:
            self._clear_hover()
            return
        index = floor(self._left + fraction * self._span)
        if index >= len(self._candles):
            self._clear_hover()
            return
        candle = self._candles[index]
        text = (f"{utc_label(candle.timestamp, full=True)}\n"
                f"Open {candle.open:g}  High {candle.high:g}\n"
                f"Low {candle.low:g}  Close {candle.close:g}\nVolume {candle.volume:g}")
        if self.toolTip() != text:
            self._clear_hover()
            self.setToolTip(text)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_x = None
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self._clear_hover()
        super().leaveEvent(event)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self._clear_hover()
        self._drag_x = None
        super().resizeEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        try:
            painter.fillRect(self.rect(), QColor("white"))
            painter.setPen(QColor("#374151"))
            if not self._candles:
                painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No candle data.")
                return

            plot = self._plot()
            if plot.isEmpty():
                return

            first = floor(self._left)
            end = min(len(self._candles), ceil(self._left + self._span))
            stats = self._price_index.query(first, end)
            if stats is None:
                return
            low, high = stats.min_low, stats.max_high
            span = high - low
            # Scaling before subtraction avoids overflow for extreme signed prices.
            scale = max(abs(low), abs(high)) if span == float("inf") else 1.0
            scaled_high = high / scale
            scaled_span = scaled_high - low / scale

            def price_y(price: float) -> float:
                if not scaled_span:
                    return plot.center().y()
                return plot.top() + (scaled_high - price / scale) / scaled_span * plot.height()

            spacing = plot.width() / self._span

            def candle_x(index: int) -> float:
                return plot.left() + (index + 0.5 - self._left) * spacing

            metrics = painter.fontMetrics()
            painter.setPen(QColor("#596575"))
            painter.drawText(QPointF(plot.left(), plot.top() - 5), "Time (UTC)")
            painter.drawLine(QLineF(plot.topRight(), plot.bottomRight()))
            painter.drawLine(QLineF(plot.bottomLeft(), plot.bottomRight()))
            for price in ((low,) if high == low else (high, low)):
                y = price_y(price)
                painter.drawLine(QLineF(plot.right(), y, plot.right() + 4, y))
                label = f"{price:.2f}"
                if metrics.horizontalAdvance(label) > 90:
                    label = f"{price:.6g}"
                painter.drawText(QPointF(plot.right() + 8, y + metrics.ascent() / 2), label)

            last_label_right = plot.left() - 8
            for index in sorted({first, (first + end - 1) // 2, end - 1}):
                label = utc_label(self._candles[index].timestamp)
                width = metrics.horizontalAdvance(label)
                if width > plot.width():
                    continue
                x = max(plot.left(), min(candle_x(index) - width / 2, plot.right() - width))
                if x >= last_label_right + 8:
                    painter.drawText(QPointF(x, plot.bottom() + metrics.ascent() + 6), label)
                    last_label_right = x + width

            body_width = min(30.0, spacing * 0.65)
            rising = QColor("#16834b")
            falling = QColor("#c23737")
            painter.setPen(QColor("#374151"))
            painter.setClipRect(plot)
            for index in range(first, end):
                candle = self._candles[index]
                x = candle_x(index)
                painter.drawLine(QLineF(x, price_y(candle.high), x, price_y(candle.low)))
                open_y = price_y(candle.open)
                close_y = price_y(candle.close)
                body = QRectF(
                    x - body_width / 2,
                    min(open_y, close_y),
                    body_width,
                    max(1.0, abs(open_y - close_y)),
                )
                painter.fillRect(body, rising if candle.close >= candle.open else falling)
        finally:
            painter.end()
