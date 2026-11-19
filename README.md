# Interactive TradingView Stock Chart Engine (DSA Python — LeetCode Edition)

Tackle a real 60 FPS PyQt6 TradingView-style candlestick chart engine **like a LeetCode problem sheet**.

- **Pre-built harness (DO NOT EDIT for P01–P11):** PyQt6 `QPainter` chart canvas ([src/ui/chart_canvas.py](src/ui/chart_canvas.py)), `MainWindow` workbench ([src/ui/main_window.py](src/ui/main_window.py)), CLI/benchmark runner ([src/main.py](src/main.py)), and the real `pytest` judge ([tests/](tests/)).
- **Your job:** Solve **11 self-contained problems (`P01`–`P11`)** by replacing `NotImplementedError` stubs until each problem's `pytest -m pXX` suite turns green. Once `P01`–`P11` pass, the **Final Boss** (`pytest -m integration` and the live PyQt6 chart app) unlocks automatically.

---

## 1. Quick Start (3-Step LeetCode Loop)

```bash
pip install -r requirements.txt
```

1. **Pick a problem** from the sheet below (start with `P01` or any problem with no dependency).
2. **Run its judge (Red):** e.g. `pytest -m p03` — every unsolved stub fails loudly with `NotImplementedError`.
3. **Implement & iterate until Green:** read the concise Problem / Constraints / Examples header at the top of the file, write your solution, and re-run `pytest -m p03` (or narrow down with `-k`, e.g. `pytest -m p05 -k circular_deque`).

---

## 2. Problem Sheet (`P01`–`P11` + Final Boss)

| ID | Problem | Diff | File | Depends On | Target Complexity / Rules | Judge Command | Team Owner |
|---|---|---|---|---|---|---|---|
| **P01** | `Candle` OHLCV Model | Easy | [src/core/candle.py](src/core/candle.py) | — | $O(1)$ validation & properties | `pytest -m p01` | TV1 |
| **P02** | `csv_loader` Parser | Easy | [src/core/csv_loader.py](src/core/csv_loader.py) | P01 | $O(N)$ strict monotonic CSV load | `pytest -m p02` | TV1 |
| **P03** | `RingBuffer` | Medium | [src/core/ring_buffer.py](src/core/ring_buffer.py) | — | $O(1)$ push; **no `collections.deque`** (AST-checked) | `pytest -m p03` | TV1 |
| **P04** | `data_simulator` & `ReplayDataSource` | Easy | [src/core/data_simulator.py](src/core/data_simulator.py) | P01, P02 | $O(1)$ step/upsert + **Factory Method** (`from_csv`, `from_synthetic`) | `pytest -m p04` | TV1 |
| **P05** | `CircularDeque`, `MonotonicDeque` & Indicators | Med-Hard | [src/algorithms/monotonic_deque.py](src/algorithms/monotonic_deque.py) | P01 *(Donchian)* | $O(1)$ amort. deque, $O(N)$ indicators; **no `collections.deque`** | `pytest -m p05` | TV2 |
| **P06** | `CoordinateTransformer` & `ViewportState` | Medium | [src/core/coordinate_math.py](src/core/coordinate_math.py) | — | $O(1)$ affine math, cursor zoom, **Prototype** (`dataclasses.replace`) | `pytest -m p06` | TV2 |
| **P07** | `SegmentTree` & `scan_range` | Hard | [src/algorithms/segment_tree.py](src/algorithms/segment_tree.py) | P01 | $O(\log N)$ `[left, right)` query/update, amort. $O(\log N)$ append | `pytest -m p07` | TV3 |
| **P08** | `LTTBDecimator` & OHLCV Buckets | Medium | [src/algorithms/lttb_decimator.py](src/algorithms/lttb_decimator.py) | P01 *(buckets)* | $O(N)$ visual downsampling & bucket merge | `pytest -m p08` | TV3 |
| **P09** | `QuadTree` 2D Spatial Index | Hard | [src/algorithms/quad_tree.py](src/algorithms/quad_tree.py) | — | $O(\log N)$ avg range & branch-and-bound nearest | `pytest -m p09` | TV3 |
| **P10** | `EventBus` (Observer) | Easy | [src/patterns/observer.py](src/patterns/observer.py) | — | Thread-safe Pub-Sub (`RLock`, snapshot dispatch) | `pytest -m p10` | TV4 |
| **P11** | `CommandHistory` (Command) | Easy | [src/patterns/command_history.py](src/patterns/command_history.py) | — | Bounded Undo/Redo stacks | `pytest -m p11` | TV4 |
| **Boss** | Full Integration (PyQt6 + CLI + Bench) | — | Pre-built harness | P01–P11 | Headless `QT_QPA_PLATFORM=offscreen` + CLI + Bench | `QT_QPA_PLATFORM=offscreen pytest -m integration` | All |

> **Team parallelization tip:** Once **P01** is merged (takes ~5 min), TV1 (`P02`–`P04`), TV2 (`P05`–`P06`), TV3 (`P07`–`P09`), and TV4 (`P10`–`P11`) can work 100% in parallel without blocking each other.

---

## 3. Design Patterns & Anti-Overengineering Guide

Based on [Refactoring.Guru — Creational & Behavioral Patterns](https://refactoring.guru/design-patterns/creational-patterns), adapted idiomatically for Python:

| Pattern | Category | Status in this Repo | Where / Why |
|---|---|---|---|
| **Factory Method** | Creational | **Use (`@classmethod`)** | `ReplayDataSource.from_csv(path)` and `ReplayDataSource.from_synthetic(...)` in [data_simulator.py](src/core/data_simulator.py) — lets `MainWindow` construct sources cleanly with zero extra factory classes. |
| **Prototype** | Creational | **Use (`dataclasses.replace`)** | `CoordinateTransformer.zoom_at_pixel` / `pan_by_pixels` clone immutable `ViewportState` snapshots via `dataclasses.replace(...)` so Undo/Redo never shares mutated state. |
| **Observer** | Behavioral | **Use (`EventBus`)** | [observer.py](src/patterns/observer.py) decouples `ChartCanvasWidget` from `MainWindow`. |
| **Command** | Behavioral | **Use (`CommandHistory`)** | [command_history.py](src/patterns/command_history.py) encapsulates pan/zoom/fit-all Undo/Redo. |
| **Builder** | Creational | **Skip** | Python `@dataclass` keyword defaults (`ViewportState`, `Candle`) already replace GoF Builder. |
| **Abstract Factory** | Creational | **Skip** | Only 1 UI backend (`PyQt6`) and 1 theme exist; abstracting 1 implementation is YAGNI bloat. |
| **Singleton** | Creational | **Skip (Anti-pattern here)** | Global `EventBus` / `CommandHistory` leaks state across `pytest` tests; use constructor Dependency Injection instead. |

---

## 4. Running the Full App & Benchmarks (After P01–P11 Pass)

```bash
# Run the entire judge (headless PyQt6 included)
QT_QPA_PLATFORM=offscreen pytest -v

# Headless CLI pipeline smoke check
python3 -m src.main --cli --csv data/sample_ohlcv.csv

# Performance & memory benchmark (SegmentTree vs scan_range, MonotonicDeque vs naive O(N*W))
python3 -m src.main --benchmark --count 10000

# Launch the interactive PyQt6 TradingView desktop app
python3 -m src.main
```

Full CLI flags:
```text
python3 -m src.main [--cli | --benchmark | --gui] [--csv data/sample_ohlcv.csv] [--count 10000] [--capacity 256] [--window 20]
```

---

## 5. Reference Docs

- [docs/interfaces.md](docs/interfaces.md) — Single Source of Truth API contracts for all 15 components.
- [CONTRIBUTING.md](CONTRIBUTING.md) — Git Flow, zero-shortcut rules, design-pattern rules, and PR checklist.
- [docs/UML_ARCHITECTURE.md](docs/UML_ARCHITECTURE.md) — Mermaid architecture & sequence diagrams.
- [docs/DSA_LEARNING_GUIDE.md](docs/DSA_LEARNING_GUIDE.md) — Deep-dive DSA study guide.
- [docs/complexity_analysis.md](docs/complexity_analysis.md) — Time/space proofs and 60 FPS frame budget.
- [ROADMAP.md](ROADMAP.md) & [DEADLINES_AND_TASKS.md](DEADLINES_AND_TASKS.md) — 6-week M1–M6 course schedule.
