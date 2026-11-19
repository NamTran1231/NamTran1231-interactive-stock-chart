"""Application shell owned by Nam; chart drawing belongs in chart_canvas.py."""

from PyQt6.QtWidgets import QMainWindow, QWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Stock Chart — M2")
        self.resize(960, 600)

        # Dũng's ChartCanvasWidget will replace this blank central widget later.
        self.setCentralWidget(QWidget())
