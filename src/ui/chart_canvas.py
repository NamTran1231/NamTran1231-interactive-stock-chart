"""Draw a static candlestick preview from validated OHLCV data."""

from collections.abc import Sequence

from PyQt6.QtCore import QLineF, QRectF, Qt
from PyQt6.QtGui import QColor, QPaintEvent, QPainter
from PyQt6.QtWidgets import QWidget

from src.core.candle import Candle


class ChartCanvasWidget(QWidget):
    def __init__(self, candles: Sequence[Candle]) -> None:
        super().__init__()
        self._candles = tuple(candles)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        try:
            painter.fillRect(self.rect(), QColor("white"))
            painter.setPen(QColor("#374151"))
            if not self._candles:
                painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No candle data.")
                return

            plot = QRectF(self.rect()).adjusted(16, 16, -16, -16)
            if plot.width() <= 0 or plot.height() <= 0:
                return

            low = min(candle.low for candle in self._candles)
            high = max(candle.high for candle in self._candles)
            span = high - low
            # Scaling before subtraction avoids overflow for extreme signed prices.
            scale = max(abs(low), abs(high)) if span == float("inf") else 1.0
            scaled_high = high / scale
            scaled_span = scaled_high - low / scale

            def price_y(price: float) -> float:
                if not scaled_span:
                    return plot.center().y()
                return plot.top() + (scaled_high - price / scale) / scaled_span * plot.height()

            spacing = plot.width() / len(self._candles)
            body_width = min(30.0, spacing * 0.65)
            rising = QColor("#16834b")
            falling = QColor("#c23737")
            painter.setClipRect(plot.adjusted(-1, -1, 1, 1))
            for index, candle in enumerate(self._candles):
                x = plot.left() + (index + 0.5) * spacing
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
