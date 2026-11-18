# M2: Minimal PyQt6 desktop setup research

Sources accessed: **November 18, 2026**. Scope: a small desktop window using PyQt6 and Qt Widgets. Official behavior is separated from implementation recommendations below.

## Installation and Python compatibility

**Official behavior:** Riverbank documents `pip install PyQt6`. Supported wheels install the bindings plus the `PyQt6-Qt6` Qt libraries and `PyQt6-sip` dependency automatically; a separate Qt SDK is normally unnecessary for this route. Wheel availability depends on Python, operating system, and architecture. If pip falls back to a source build, additional build configuration and Qt tools are needed. [1]

**Metadata checked:** The current PyPI release is **6.12.1**, with `Requires-Python >=3.10`. The historical **6.5.0** metadata says `>=3.6.1`, but its published wheels use `cp37-abi3` tags. An old metadata minimum alone therefore does not establish usable wheels or dependency compatibility for an old interpreter. [2][3]

**Recommendation:** Use a virtual environment and a supported Python version, preferably Python 3.10 or newer for the current release. For this basic Widgets setup, `PyQt6>=6.5,<7` is a reasonable dependency baseline, not an exact pin or an official Riverbank requirement:

```sh
python -m pip install "PyQt6>=6.5,<7"
```

Let pip resolve compatible packages, then verify installation and launch on each target platform. The range does not guarantee wheels on every OS or interpreter. The APIs below do not require newer Qt features. Riverbank notes that PyQt and Qt patch versions need not match. [1–3]

## Application lifecycle and a minimal window

**Official Qt behavior:**

- A Widgets application has **one `QApplication`**, even with multiple windows. Construct it before widgets and other UI resources. It initializes GUI resources and handles application-wide events and settings. [4]
- A `QWidget` without a parent is a top-level window. Call `show()` to make it visible; constructing it alone does not display it. `setWindowTitle()` and `resize()` configure its title and size. [5]
- `app.exec()` enters the main event loop, which dispatches events and keeps the interface responsive. It returns an exit code when the loop exits normally. By default, closing the last visible primary window attempts to quit the application. [4][6]
- Create and use widgets and run the main event loop on the **main thread**. Qt recommends workers for time-consuming operations, with results delivered back to the main thread. [7]

**Recommended Python entry-point pattern:**

```python
import sys

from PyQt6.QtWidgets import QApplication, QWidget


def main() -> int:
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Interactive Stock Chart")
    window.resize(1000, 600)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
```

The title and dimensions are design choices. Keeping the window in a local variable retains a reference while `exec()` runs. The main guard prevents importing the module from automatically creating a window or starting an event loop; this follows Python's documented entry-point idiom, not a Qt-specific requirement. [8] Keep later stock-data fetching and expensive calculations out of blocking GUI callbacks. [7]

## Headless smoke testing

**Official mechanism:** Qt lists `offscreen` as a platform plugin and supports selecting the platform through `QT_QPA_PLATFORM` or `-platform`. Select it before constructing the application. Qt's offscreen implementation uses a separate platform integration; its source restricts native styles to avoid requiring native window handles. [6][9]

**Recommended smoke check:** On a headless Linux runner, use `QT_QPA_PLATFORM=offscreen` for a small check that creates the application and window, calls `show()`, processes events, checks basic properties, and closes cleanly. Reuse one application instance across checks in the same process. For a check of `exec()` itself, schedule a `QTimer.singleShot` to close the window and add an external timeout so failures cannot hang indefinitely.

**Limitations (testing recommendation):** Passing offscreen checks demonstrates startup and basic widget behavior under that plugin. It does **not** demonstrate that a real desktop window appears, looks correct, receives native input/focus correctly, or loads the target desktop's platform plugin and system libraries. Native styling and graphics behavior can differ. Complete M2 with a normal desktop launch: confirm the title, visible window, resizing, and exit on close. Do not force offscreen mode for ordinary users. [6][9]

## Primary sources

1. [Riverbank — Installing PyQt6](https://www.riverbankcomputing.com/static/Docs/PyQt6/installation.html)
2. [PyPI — PyQt6 project, current metadata and wheels](https://pypi.org/project/PyQt6/)
3. [PyPI — PyQt6 6.5.0 JSON metadata and wheel tags](https://pypi.org/pypi/PyQt6/6.5.0/json)
4. [Qt 6 — QApplication, lifecycle and exec()](https://doc.qt.io/qt-6/qapplication.html)
5. [Qt 6 — QWidget, top-level widgets and show()](https://doc.qt.io/qt-6/qwidget.html)
6. [Qt 6 — QGuiApplication, platform selection and quit-on-close](https://doc.qt.io/qt-6/qguiapplication.html)
7. [Qt 6 — Threads and QObjects](https://doc.qt.io/qt-6/threads-qobject.html)
8. [Python — __main__ and idiomatic main guards](https://docs.python.org/3/library/__main__.html)
9. [Qt source — Offscreen platform integration (6.5 branch)](https://code.qt.io/cgit/qt/qtbase.git/plain/src/plugins/platforms/offscreen/qoffscreenintegration.cpp?h=6.5)
