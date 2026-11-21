"""Application shell owned by Nam; chart drawing belongs in chart_canvas.py."""

from PyQt6.QtWidgets import QMainWindow, QWidget

from src.core.candle import Candle


class MainWindow(QMainWindow):
    def __init__(self, *, candles: list[Candle] | None = None) -> None:
        super().__init__()
        self.setWindowTitle("Stock Chart — M2")
        self.resize(960, 600)
        self.candles = tuple(candles) if candles is not None else ()
        if candles is not None:
            self.statusBar().showMessage(f"Loaded {len(self.candles)} candles.")

        # Dũng's ChartCanvasWidget will replace this blank central widget later.
        self.setCentralWidget(QWidget())
