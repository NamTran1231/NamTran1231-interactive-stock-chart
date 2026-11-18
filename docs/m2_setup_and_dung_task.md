# M2 Start Guide — Nam's Setup and Dũng's First Task

## 1. What is ready?

Nam's setup introduces an empty PyQt6 window, a runnable entry point, an optional GUI dependency file, and offscreen lifecycle tests. **It does not draw candles yet.** M1's CLI remains independent of Qt.

| File | Owner | Purpose |
| --- | --- | --- |
| `requirements-gui.txt` | Nam | Optional PyQt6 dependency for M2 |
| `src/main.py` | Nam | Create QApplication, show MainWindow, run the event loop |
| `src/ui/main_window.py` | Nam | Window title, initial size, blank central widget |
| `src/ui/chart_canvas.py` | Dũng | Existing empty placeholder for the next drawing task |
| `tests/test_gui_setup.py` | Nam | Optional offscreen import/window/entry-point checks |

## 2. Install and run

After the setup PR is merged, update your local main safely before creating a task branch. Preserve any uncommitted work first. Open a terminal at the repository root.

Create an environment:

```bash
python -m venv .venv
```

Activate it:

- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- Linux/macOS: `source .venv/bin/activate`

Install and start the window:

```bash
python -m pip install -r requirements-gui.txt
python -m src.main
```

Expected: an empty window titled **Stock Chart — M2**, initially **960 × 600**. It can be moved, resized, and closed. Closing the only window should end the command normally. Use `python3` instead of `python` where needed. Run on a machine with a graphical desktop; an offscreen server cannot confirm the actual on-screen appearance.

If installation or startup fails, send Nam the OS, Python version, exact command, and complete error. Do not substitute PyQt5 or change the dependency range without discussing it.

## 3. Dũng — first task only: draw one fixed candle

**Task ID: M2-D01.** Your deliverable is a widget that paints one candlestick correctly whenever Qt asks it to repaint. Do not implement CSV loading, axes, pan/zoom, or hover in this task.

### Learn only what this task needs

Search:

1. `PyQt6 QWidget paintEvent QPainter drawLine drawRect`
2. `Qt widget coordinates top left y increases downwards`
3. `PyQt6 QColor QPen QBrush`

Understand: a widget receives `paintEvent`; QPainter draws on that widget; screen x grows right and y grows downward; the wick is a line and the body is a rectangle. Read the research notes in `docs/m2_gui_setup_research.md` and the official sources linked there.

### Step 1 — start from the agreed setup

Once Nam's setup is merged, and your working tree is clean:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c feature/m2-chart-canvas
```

If the branch already exists, use that branch with Nam's help rather than creating it again. Do not remove another task's uncommitted files.

### Step 2 — implement exactly one widget

Work in **`src/ui/chart_canvas.py`**. This is an empty placeholder; if it already contains newer work, read that work before editing.

Required class and method:

```python
class ChartCanvasWidget(QWidget):
    def paintEvent(self, event) -> None:
        ...
```

- Import QWidget from PyQt6.QtWidgets.
- Use QPainter, QColor, QPen, and QBrush from PyQt6.QtGui as needed.
- Create the painter inside paintEvent, not in `__init__`.
- Paint a white background each repaint so the result is visible and old pixels are cleared.
- Draw one dark wick: **x = 150, from y = 80 to y = 220**.
- Draw one green body: **left x = 135, top y = 120, width = 30, height = 60**.
- Draw the wick first, then the filled body, so the wick does not cross the body visually.
- End the painter with `painter.end()` or use its supported context-manager form.

These are deliberately fixed screen coordinates. They are a drawing exercise, not a price-to-screen transform. A tiny window may clip the candle; responsive coordinate scaling belongs to a later task.

### Step 3 — connect the widget with Nam

Nam owns the application shell. Send Nam your widget class/import, or coordinate one small shell change in the same PR:

```python
from src.ui.chart_canvas import ChartCanvasWidget

# Replace the blank central widget in MainWindow.__init__:
self.setCentralWidget(ChartCanvasWidget())
```

Do not create a second QApplication or a second entry point in your widget module. Do not rewrite `src/main.py` just to preview the widget. If Nam makes the integration change separately, agree on the PR order first.

### Step 4 — run and check

```bash
python -m src.main
```

- [ ] One green rectangular candle body is visible on white.
- [ ] The wick extends above and below the body at its center.
- [ ] Resizing to a normal size such as 800 × 500 redraws the candle.
- [ ] Covering/uncovering or minimizing/restoring the window redraws it without trails.
- [ ] Closing the window ends the process normally.
- [ ] The terminal has no traceback or QPainter lifecycle warnings.

### Step 5 — hand in

Open a PR into main with:

```text
Title: feat(chart): draw a single fixed candle with QPainter
Files changed:
Python/PyQt6 version and OS:
Command run:
Screenshot of the candle:
Resize / restore / close results:
Questions or remaining problems:
```

**Done means the checklist above is confirmed, not merely that the class exists.** Send Nam the PR link. Do not mark all M2 complete: the next task will connect multiple candles from the shared model, then add transforms/axes/interactions incrementally.

## 4. Nam's handoff check

Before Dũng starts, Nam or Dũng should confirm that the empty window works on their actual desktop. Agent-side offscreen tests verify lifecycle, not visual appearance or OS-specific desktop integration.

Run the existing tests in the GUI environment:

```bash
python -m unittest discover -s tests -v
```

Without PyQt6, the three GUI checks skip and the standard-library M1 suite still runs. With PyQt6 installed, the GUI checks use subprocesses and the offscreen platform; they do not leave a window running or require changing the production event loop.

## 5. Setup verification record

Verified on the agent's Linux environment using Python 3.14.4, PyQt6 6.12.1, and Qt 6.12.0 in an isolated virtual environment:

- `python -m unittest discover -s tests -v`: **22 tests passed**, including 19 M1 checks and three GUI setup checks.
- GUI checks confirm passive imports, an initially 960 × 600 visible offscreen window, normal close behavior, and entry-point event-loop exit.
- No candle has been drawn, and actual desktop appearance/move/resize interaction still needs confirmation by Nam or Dũng.
- The test versions document this verification environment; the dependency range is not an exact lock for every team machine.
