"""Start the M2 desktop application: python -m src.main."""

import sys

from PyQt6.QtWidgets import QApplication

from src.ui.main_window import MainWindow


def main(argv: list[str] | None = None) -> int:
    """Create the application, show its window, and run the GUI event loop."""
    app = QApplication(sys.argv if argv is None else argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
