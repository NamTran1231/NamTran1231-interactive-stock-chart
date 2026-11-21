"""Optional, offscreen lifecycle checks; skipped when PyQt6 is not installed."""

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(importlib.util.find_spec("PyQt6"), "Install requirements-gui.txt for GUI tests")
class GuiSetupTests(unittest.TestCase):
    def run_offscreen(self, script):
        environment = os.environ.copy()
        environment["QT_QPA_PLATFORM"] = "offscreen"
        return subprocess.run(
            [sys.executable, "-c", script], cwd=ROOT, env=environment,
            capture_output=True, text=True, timeout=15,
        )

    def test_import_does_not_create_application(self):
        result = self.run_offscreen("""
from PyQt6.QtWidgets import QApplication
import src.main
import src.ui.main_window
assert QApplication.instance() is None
print('Imports are passive')
""")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Imports are passive", result.stdout)

    def test_window_shows_and_closes(self):
        result = self.run_offscreen("""
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

app = QApplication([])
window = MainWindow()
assert window.windowTitle() == 'Stock Chart — M2'
assert window.width() == 960 and window.height() == 600
assert window.centralWidget() is not None
window.show()
app.processEvents()
assert window.isVisible()
QTimer.singleShot(20, window.close)
QTimer.singleShot(2000, app.quit)
assert app.exec() == 0
assert not window.isVisible()
print('Window lifecycle passed')
""")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Window lifecycle passed", result.stdout)

    def test_entry_point_runs_event_loop_and_exits(self):
        result = self.run_offscreen("""
from PyQt6.QtCore import QTimer
from unittest.mock import patch
from src import main as entry
from src.ui.main_window import MainWindow

class AutoClosingWindow(MainWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        QTimer.singleShot(20, self.close)

with patch.object(entry, 'MainWindow', AutoClosingWindow):
    assert entry.main(['stock-chart']) == 0
print('Entry point passed')
""")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Entry point passed", result.stdout)

    def test_csv_startup_passes_candles_to_window(self):
        result = self.run_offscreen("""
from PyQt6.QtCore import QTimer
from unittest.mock import patch
from src import main as entry
from src.ui.main_window import MainWindow

class CheckingWindow(MainWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assert len(self.candles) == 12
        assert self.candles[0].timestamp == 1704067200
        assert self.statusBar().currentMessage() == 'Loaded 12 candles.'
        QTimer.singleShot(20, self.close)

with patch.object(entry, 'MainWindow', CheckingWindow):
    assert entry.main(['stock-chart', '--csv', 'tests/fixtures/candles_valid.csv']) == 0
""")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_invalid_csv_is_reported_before_gui_creation(self):
        result = self.run_offscreen("""
from PyQt6.QtWidgets import QApplication
from unittest.mock import patch
from src import main as entry

with patch.object(entry, 'load_candles', side_effect=ValueError('CSV row 2: invalid OHLC bounds')):
    assert entry.main(['stock-chart', '--csv', 'invalid.csv']) == 1
assert QApplication.instance() is None
""")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Error: CSV row 2: invalid OHLC bounds", result.stderr)


if __name__ == "__main__":
    unittest.main()
