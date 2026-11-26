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

    def test_canvas_renders_demo_and_csv_after_resize(self):
        result = self.run_offscreen("""
from PyQt6.QtWidgets import QApplication
from src.core.csv_loader import load_candles
from src.ui.main_window import MainWindow

app = QApplication([])

def painted_columns(window, *, plot_only=False):
    canvas = window.centralWidget()
    image = canvas.grab().toImage()
    if plot_only:
        image = image.copy(canvas._plot().toRect())
    background = image.pixel(0, 0)
    return {x for x in range(image.width())
            if any(image.pixel(x, y) != background for y in range(image.height()))}

for candles, expected in ((None, 1), (load_candles('tests/fixtures/candles_valid.csv'), 12)):
    window = MainWindow(candles=candles)
    window.resize(480, 300)
    window.show()
    app.processEvents()
    before = painted_columns(window, plot_only=True)
    window.resize(640, 400)
    app.processEvents()
    after = painted_columns(window, plot_only=True)
    # Each candle occupies a separate run of columns inside the plot.
    for columns in (before, after):
        actual = sum(x - 1 not in columns for x in columns)
        assert actual == expected, (actual, expected)
    assert max(after) > max(before), 'Candle positions did not respond to resizing'
    window.close()

window = MainWindow(candles=[])
assert window.statusBar().currentMessage() == 'Loaded 0 candles.'
window.show()
app.processEvents()
assert painted_columns(window), 'Expected a visible empty-state message'
window.close()
""")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_100_candle_csv_navigation_and_edges(self):
        result = self.run_offscreen("""
from unittest.mock import patch
from PyQt6.QtCore import QPoint, QPointF, Qt
from PyQt6.QtGui import QMouseEvent, QPainter, QWheelEvent
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication
from src.algorithms.range_scan import scan_range
from src.algorithms.segment_tree import SegmentTree
from src.core.csv_loader import load_candles
from src.ui.main_window import MainWindow

app = QApplication([])
candles = load_candles('tests/fixtures/candles_m2_100.csv')
window = MainWindow(candles=candles)
window.show()
app.processEvents()
canvas = window.centralWidget()
assert window.statusBar().currentMessage() == 'Loaded 100 candles.'
image = canvas.grab().toImage().copy(canvas._plot().toRect())
background = image.pixel(0, 0)
painted = {x for x in range(image.width())
           if any(image.pixel(x, y) != background for y in range(image.height()))}
assert sum(x - 1 not in painted for x in painted) == 100

def point(fraction):
    plot = canvas._plot()
    return QPoint(round(plot.left() + fraction * plot.width()), round(plot.center().y()))

def hover(position):
    QTest.mouseMove(canvas, position + QPoint(0, -1))
    QTest.mouseMove(canvas, position)
    app.processEvents()
    return canvas.toolTip()

def wheel(position, steps):
    event = QWheelEvent(QPointF(position), QPointF(canvas.mapToGlobal(position)),
                        QPoint(), QPoint(0, 120 * steps), Qt.MouseButton.NoButton,
                        Qt.KeyboardModifier.NoModifier, Qt.ScrollPhase.NoScrollPhase, False)
    app.sendEvent(canvas, event)

def drag(start, end):
    QTest.mousePress(canvas, Qt.MouseButton.LeftButton, pos=start)
    move = QMouseEvent(QMouseEvent.Type.MouseMove, QPointF(end),
                       QPointF(canvas.mapToGlobal(end)), Qt.MouseButton.NoButton,
                       Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    app.sendEvent(canvas, move)
    QTest.mouseRelease(canvas, Qt.MouseButton.LeftButton, pos=end)

def assert_edges():
    assert '00:00:00 UTC' in hover(point(0.002))
    assert '01:39:00 UTC' in hover(point(0.998))
    assert hover(point(-0.01)) == ''
    assert hover(point(1.0)) == ''

assert_edges()
anchor = point(0.52)
details = hover(anchor)
assert all(field in details for field in ('Open ', 'High ', 'Low ', 'Close ', 'Volume '))
wheel(anchor, 5)
assert hover(anchor) == details, 'Zoom should preserve the candle under the cursor'
assert '00:00:00 UTC' not in hover(point(0.002))
assert '01:39:00 UTC' not in hover(point(0.998))
queried = []
labels = []
original_query = SegmentTree.query

class RecordingPainter(QPainter):
    def drawText(self, *args):
        labels.append(args[-1])
        return super().drawText(*args)

def checked_query(tree, left, right):
    stats = original_query(tree, left, right)
    expected = scan_range(candles, left, right)
    assert (stats.min_low, stats.max_high) == (expected.min_low, expected.max_high)
    queried.append((left, right, expected))
    return stats

def assert_visible_labels():
    labels.clear()
    canvas.grab()
    expected = queried[-1][2]
    assert f'{expected.min_low:.2f}' in labels
    assert f'{expected.max_high:.2f}' in labels

with patch.object(SegmentTree, 'query', checked_query), patch('src.ui.chart_canvas.QPainter', RecordingPainter):
    assert_visible_labels()
    assert queried and 0 < queried[-1][0] < queried[-1][1] < len(candles)
    zoomed = queried[-1]
    drag(point(0.02), point(3.2))
    assert_visible_labels()
    assert queried[-1][0] == 0 and queried[-1][1] < zoomed[1]
    assert queried[-1][2].min_low != zoomed[2].min_low
assert '00:00:00 UTC' in hover(point(0.002)), 'Pan must stop at the first candle'
drag(point(0.98), point(-2.2))
assert '01:39:00 UTC' in hover(point(0.998)), 'Pan must stop at the last candle'
wheel(point(1.0), -10)
assert '00:00:00 UTC' not in hover(point(0.002)), 'Zoom outside the plot must be ignored'
wheel(anchor, -10)
assert_edges()
window.resize(600, 360)
app.processEvents()
assert_edges()
window.close()
""")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_flat_price_and_tiny_viewport(self):
        result = self.run_offscreen("""
from PyQt6.QtCore import QPoint
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication
from src.core.candle import Candle
from src.ui.chart_canvas import ChartCanvasWidget

app = QApplication([])
canvas = ChartCanvasWidget([Candle(1704067200, 0, 0, 0, 0, 0)])
canvas.resize(480, 300)
canvas.show()
app.processEvents()
plot = canvas._plot()
center = plot.center().toPoint()
image = canvas.grab().toImage()
assert image.pixel(center) != image.pixel(0, 0), 'A flat candle must remain visible'
QTest.mouseMove(canvas, center)
assert 'Close 0' in canvas.toolTip()
canvas.resize(80, 40)
app.processEvents()
QTest.mouseMove(canvas, QPoint(20, 20))
assert canvas.toolTip() == ''
assert not canvas.grab().isNull()
canvas.close()
""")
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
