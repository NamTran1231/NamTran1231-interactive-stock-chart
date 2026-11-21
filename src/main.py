"""Start the M2 desktop application: python -m src.main."""

import argparse
import sys

from PyQt6.QtWidgets import QApplication

from src.core.csv_loader import load_candles
from src.ui.main_window import MainWindow


def main(argv: list[str] | None = None) -> int:
    """Load optional CSV data, then show the window and run the event loop."""
    arguments = sys.argv if argv is None else argv
    parser = argparse.ArgumentParser(description="Open the Stock Chart desktop window.")
    parser.add_argument("--csv", metavar="PATH", help="Load an OHLCV CSV on startup")
    args = parser.parse_args(arguments[1:])

    candles = None
    if args.csv is not None:
        try:
            candles = load_candles(args.csv)
        except (OSError, ValueError) as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

    app = QApplication(arguments[:1])
    window = MainWindow(candles=candles)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
