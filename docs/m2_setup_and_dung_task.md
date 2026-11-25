# M2 Start Guide — Nam's Setup and Dũng's First Task

The interactive M2 follow-up adds price and UTC time labels, wheel zoom, drag-to-pan, and OHLCV hover. See the [current run commands and controls](../README.md#m2-desktop-setup-english). The static-preview notes below document the earlier checkpoint.

The agent-assisted static preview draws one demo candle or the loaded CSV candles. Dũng's next checkpoint is to run it and explain the price-to-screen mapping. The original fixed-coordinate exercise is preserved below as optional practice.

## 1. What is ready?

The PyQt6 preview accepts validated candles from Nam's CSV startup path. The chart draws a static view, with no axes or navigation yet. M1's CLI remains independent of Qt.

| File | Owner | Purpose |
| --- | --- | --- |
| `requirements-gui.txt` | Nam | Optional PyQt6 dependency for M2 |
| `src/main.py` | Nam | Load optional CSV, show MainWindow, run the event loop |
| `src/ui/main_window.py` | Nam | Pass the loaded candles, or one demo candle, to the canvas |
| `src/ui/chart_canvas.py` | Dũng | Paint candle wicks and bodies using the current widget size |
| `tests/test_gui_setup.py` | Nam | Optional offscreen startup, lifecycle, and rendering checks |

## 2. Install and run

Use the branch containing the static preview (`feature/m2-first-csv-chart` until merged). Preserve any uncommitted work before switching branches. Open a terminal at the repository root.

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
python -m src.main --csv tests/fixtures/candles_valid.csv
```

The first launch shows one demo candle. The CSV launch shows 12 candles and `Loaded 12 candles.` in the status bar. Resize the window, minimize and restore it, then close it. Expect candles to redraw at the new size and the process to exit cleanly. Use `python3` instead of `python` where needed.

If installation or startup fails, send Nam the OS, Python version, exact command, and complete error. Do not substitute PyQt5 or change the dependency range without discussing it.

## 3. Dũng — preview review

- [ ] Run both preview modes on your desktop and send Nam a screenshot and your resize/restore/close results.
- [ ] Read `src/ui/chart_canvas.py`. Explain why a higher price has a smaller screen y-coordinate and how `high`/`low` differ from `open`/`close` when drawing a candle.

## 4. Archived M2-D01 — optional fixed-coordinate practice

This is the original fixed-coordinate exercise. The commands, starter assumptions, and PR checklist in this section are historical. Practice on scratch code if useful; do not replace the working preview or open the original implementation PR.

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

## 5. Nam's handoff check

Use the two launch commands above for desktop review. Run the offscreen tests for regression coverage:

Run the existing tests in the GUI environment:

```bash
python -m unittest discover -s tests -v
```

Without PyQt6, GUI checks skip and the standard-library M1 suite still runs. With PyQt6 installed, GUI checks use subprocesses and the offscreen platform.

## 6. Preview verification record

Verified on the agent's Linux environment using Python 3.14.4, PyQt6 6.12.1, and Qt 6.12.0 in an isolated virtual environment:

- `python -m unittest discover -s tests -v`: **25 tests passed**, including offscreen rendering and repaint after resize.
- A desktop `xcb` smoke check opened the shared CSV preview, confirmed the status and visible chart, and closed cleanly. A teammate-machine check is still pending.
- The test versions document this verification environment; the dependency range is not an exact lock for every team machine.

## 7. Interactive chart verification

Run `python -m src.main --csv tests/fixtures/candles_m2_100.csv` on a graphical desktop. Expect 100 candles and `Loaded 100 candles.` Zoom around a candle, drag in both directions, and hover inside and outside the plot. Close after resizing the window.

The automated suite verified all 100 painted candles, cursor-centered zoom, pan limits at both ends, off-plot hover and wheel handling, resize, and flat and tiny views. All 27 tests passed. An agent-run Linux desktop smoke test also verified the 100-candle startup, hover, zoom, pan, resize, and normal shutdown. The next teammate check is to run these steps on their own desktop.
