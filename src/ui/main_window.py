"""Application shell owned by Nam; chart drawing belongs in chart_canvas.py."""

from PyQt6.QtWidgets import QMainWindow

from src.core.candle import Candle
from src.ui.chart_canvas import ChartCanvasWidget


class MainWindow(QMainWindow):
    def __init__(self, *, candles: list[Candle] | None = None) -> None:
        super().__init__()
        self.setWindowTitle("Stock Chart — M2")
        self.resize(960, 600)
        self.candles = tuple(candles) if candles is not None else ()
        if candles is not None:
            self.statusBar().showMessage(f"Loaded {len(self.candles)} candles.")

        # No CSV means demo mode; an explicitly empty CSV remains empty.
        chart_candles = self.candles if candles is not None else (
            Candle(
                timestamp=1704067200, open=100.0, high=105.0,
                low=98.0, close=103.0, volume=1000.0,
            ),
        )
        self.setCentralWidget(ChartCanvasWidget(chart_candles))
