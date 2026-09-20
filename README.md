# 📈 Interactive Real-Time Stock Chart Engine (DSA Project)

> An interactive, high-performance financial candlestick charting engine built from scratch in Python and PyQt6, demonstrating core Data Structures and Algorithms (DSA) without external plotting libraries.

---

## 📌 Project Overview
The **Interactive Real-Time Stock Chart Engine** is an academic software project developed for the Data Structures and Algorithms curriculum. Rather than relying on black-box charting libraries (such as Matplotlib or Plotly), this application implements a custom 2D rendering pipeline using Qt's `QPainter`, combining continuous affine transformations, spatial indexing, range query trees, and geometric decimation to handle massive financial time-series datasets.

The system supports both historical exploration (loading multi-year daily/hourly CSV datasets) and live streaming simulation (real-time tick and candle updates).

---

## 🚀 Key Features

* **High-Performance Custom Canvas:** Subclassed `QWidget` with native `paintEvent()` and double-buffered `QPainter` rendering.
* **Continuous Viewport Dynamics:**
  * **Focal Zooming:** Mouse wheel zoom anchored directly at the cursor's world coordinates.
  * **Interactive Pan:** Smooth drag-and-drop navigation across time and price axes.
  * **Dynamic Axis Ticks:** Logarithmic ($\log_{10}$) scaling for gridlines and price/time labels.
* **Dual-Mode Operation:**
  * **Historical Data Analysis:** Ingests CSV files containing 100,000+ candlesticks without UI stutter.
  * **Real-Time Streaming:** Live candlestick updates via a background worker thread (`QThread`) and Ring Buffer.
* **Spatial Hover Tooltips:** Real-time crosshair and tooltip showing OHLCV (Open, High, Low, Close, Volume) metrics for the nearest candle.
* **Viewport Navigation History:** Full Undo/Redo (`Ctrl + Z` / `Ctrl + Y`) for zoom and pan states.

---

## 🧠 Data Structures & Algorithms (Core Technical Rubric)

| Component | Applied Data Structure / Algorithm | Time Complexity | Purpose |
| :--- | :--- | :--- | :--- |
| **Auto-Scaling Y-Axis** | **Segment Tree (RMQ)** | Build: $O(N)$<br>Query: $O(\log N)$ | Rapidly finds $\min(Low)$ and $\max(High)$ in the visible time window to rescale the price axis. |
| **Point Decimation** | **Largest-Triangle-Three-Buckets (LTTB)** | Run: $O(N)$ | Downsamples massive datasets (e.g., 300k points to 1,200 points) while preserving price peaks and troughs. |
| **Hover Hit-Testing** | **2D Point Quadtree** | Query: $O(\log N)$ avg | Prunes 2D Cartesian space to instantly find the nearest candle under the mouse cursor for tooltips. |
| **Live Stream Queue** | **Ring Buffer (Circular Queue)** | Push/Pop: $O(1)$ | Manages incoming streaming market ticks with fixed memory allocation and zero reallocation overhead. |
| **Navigation History** | **Dual-Stack Command Architecture** | Undo/Redo: $O(1)$ | Manages `UndoStack` and `RedoStack` to store snapshots of viewport coordinates. |

---

## 🏗️ Software Architecture & Design Patterns

* **Observer Pattern:** Decouples the underlying data store (`StockDataModel`) from the visual canvas (`ChartCanvasWidget`). Model updates trigger asynchronous canvas repaints.
* **Strategy Pattern:** Decouples downsampling via a `DecimationStrategy` interface (`LTTBStrategy`, `MinMaxStrategy`, `PassThroughStrategy`), switchable at runtime.
* **Command Pattern:** Encapsulates viewport transformations into `PanZoomCommand` objects for clean undo/redo history management.
* **Factory Method Pattern:** Encapsulates the ingestion of different time-series formats via a polymorphic `SeriesFactory`.

---

## 🛠️ Tech Stack & Requirements

* **Language:** Python 3.10+
* **GUI Framework:** PyQt6 (`PyQt6>=6.5.0`)
* **Testing:** `pytest>=7.0.0`
* **Standard Libraries:** `math`, `csv`, `dataclasses`, `typing`

---

## 📂 Project Structure

```text
interactive-stock-chart/
├── .github/workflows/
│   └── python-tests.yml        # Automated CI workflow
├── data/
│   ├── BTC-USD.csv             # Bitcoin historical dataset
│   └── AAPL.csv                # Apple historical dataset
├── docs/
│   ├── class_diagram_uml.png   # Full UML Class Diagram
│   └── complexity_analysis.md  # Asymptotic Big-O proofs
├── src/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── ui/
│   │   ├── main_window.py      # Main application window & toolbar
│   │   └── chart_canvas.py     # Custom QWidget canvas with QPainter
│   ├── core/
│   │   ├── coordinate_math.py  # World-to-Screen coordinate transformation
│   │   ├── ring_buffer.py      # Real-time circular buffer
│   │   └── data_simulator.py   # Background streaming thread (QThread)
│   ├── algorithms/
│   │   ├── segment_tree.py     # Segment Tree for Range Min/Max Queries
│   │   ├── quad_tree.py        # 2D Point Quadtree for nearest-neighbor hover
│   │   └── lttb_decimator.py   # Largest-Triangle-Three-Buckets algorithm
│   └── patterns/
│       ├── observer.py         # Observer pattern interfaces
│       └── command_history.py  # Undo/Redo navigation history
├── tests/
│   ├── test_segment_tree.py
│   ├── test_lttb.py
│   └── test_ring_buffer.py
├── .gitignore
├── requirements.txt
└── README.md
