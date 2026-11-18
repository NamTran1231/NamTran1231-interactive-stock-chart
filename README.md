# Interactive Stock Chart Engine — DSA Project

A university project for four students: build an OHLCV candlestick application with **Python + PyQt6/QPainter**, custom data structures, correctness tests, complexity arguments, and reproducible measurements.

## Current status

**Updated November 18, 2026:** PRs #3/#4 introduced the Candle model, CSV loader, and CLI. PR #5 completed model validation, CLI statistics, and M1 verification. This follow-up translates the M1 interface and documentation into English.

- Implemented: immutable validated candles, CSV loading with row-specific errors, a synthetic fixture, terminal tables, and full-dataset statistics.
- Verified: 19 unittest tests covering the model, CSV loader, and CLI subprocesses. See the [M1 completion report](docs/m1_completion.md).
- Planned: GUI, integrated custom DSA, replay, and benchmarking. Placeholder files do not represent working features.
- The older Ring Buffer prototype uses deque/PyQt5 and needs revision for M3.
- The CI workflow is still empty. An independent run on Hưng's or Nam's machine has not been confirmed.

## First-release scope

- One instrument and one intraday input timeframe; timestamps are UTC Unix seconds.
- A Qt-independent Candle model, validated CSV input, and a CLI summary.
- Custom candlesticks, axes, pan/zoom/hover, and visible-range clipping.
- A **custom Segment Tree** for minimum low, maximum high, and total volume over `[left, right)`.
- A **custom circular-array Ring Buffer** for bounded recent retention, separate from full history.
- Offline replay with play/pause, restart, and speed control. Simulation is not a live market feed.
- Correctness tests and reproducible comparisons against baselines.

Dense candle views will use OHLCV aggregation: first open, maximum high, minimum low, last close, and summed volume. LTTB is not a substitute for candle aggregation.

## M0–M6 roadmap

| Milestone | Main deliverable |
| --- | --- |
| M0 | Consistent documentation and contracts |
| M1 | Candle model, CSV loader, and CLI summary |
| M2 | A small interactive chart with approximately 100 candles |
| M3 | Custom Ring Buffer/Segment Tree integrated into working features |
| M4 | Replay and incremental updates |
| M5 | OHLCV grouping, benchmarks, and analysis |
| M6 | Optional extensions |

Test throughout development. A small GUI belongs to the first release rather than being a final bonus. See [ROADMAP.md](ROADMAP.md) for dependencies, owners, and acceptance criteria.

## Optional work

Real trade feeds, trade-to-candle construction, multiple instruments/timeframes, Quadtree, LTTB for a close-price line, undo/redo, rolling-window analytics, and advanced caching. **Restore any feature the course rubric explicitly requires.** The rubric and submission deadline have not been provided.

## Setup and usage

M1 requires Python 3.10+ and the standard library. **No pip installation, Qt, or pandas is needed for these CLI commands and tests.** Open a terminal at the repository root containing README.md and src/. Use `python3` instead of `python` if required by your system.

An optional virtual environment:

```bash
python -m venv .venv
```

Activate with `source .venv/bin/activate` on Linux/macOS or `.venv\Scripts\Activate.ps1` in Windows PowerShell. Alternatively, run the commands with your installed Python directly.

```bash
python -m src.main_cli
python -m src.main_cli tests/fixtures/candles_valid.csv
python -m src.main_cli tests/fixtures/candles_valid.csv --limit 0
python -m unittest discover -s tests -v
```

Without a path, the CLI uses three demo candles. The CSV fixture contains 12 synthetic candles; the default preview shows 10 rows. Use `--limit 0` to show all rows or `--limit 2` to show two. **Statistics always use the entire dataset**, regardless of the preview limit:

```text
Candle count: 12
First timestamp (UTC Unix seconds): 1704067200
Last timestamp (UTC Unix seconds): 1704067860
Min low: 98.00
Max high: 113.00
Total volume: 13600.00
```

CSV input must be UTF-8 with the header `timestamp,open,high,low,close,volume`; see the [contracts](docs/interfaces.md). Empty/header-only files display `No candle data.` A single candle still has a summary. Invalid data, missing files, and encoding errors report to stderr with exit status 1. Invalid arguments return status 2; success returns 0. Imports do not execute demos.

The model rejects non-integer timestamps, boolean/non-finite numeric fields, invalid OHLC bounds, and negative volume. Negative prices, flat candles, and zero volume are allowed. The loader adds header/order validation and CSV row numbers. Tests use unittest and can also run under pytest if installed. `.github/workflows/python-tests.yml` remains empty; CI is not active. The planned GUI stack remains PyQt6.

Other scaffold files remain placeholders. The AAPL/BTC datasets are on the prototype branch; M1 uses the shared synthetic fixture in `tests/fixtures/`.

## Team documentation

- [M1 completion report and verification](docs/m1_completion.md)
- [Roadmap and responsibilities](ROADMAP.md)
- [Team plan revision report](docs/team_plan_report.md)
- [Research comparison](docs/research_comparison.md)
- [Module contracts](docs/interfaces.md)
- [Complexity and benchmarks](docs/complexity_analysis.md)
- [Git workflow](CONTRIBUTING.md)
