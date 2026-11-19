"""Pre-built CLI / Benchmark / PyQt6 GUI entrypoint (DO NOT EDIT for P01-P11).

Usage:
    python3 -m src.main --cli --csv data/sample_ohlcv.csv
    python3 -m src.main --benchmark --count 10000
    python3 -m src.main [--gui]
"""

from __future__ import annotations

import argparse
from pathlib import Path
import random
import sys
import time
import tracemalloc
from typing import Any, Sequence

from src.algorithms.lttb_decimator import LTTBDecimator
from src.algorithms.monotonic_deque import SlidingWindowIndicators
from src.algorithms.segment_tree import SegmentTree, scan_range
from src.core.csv_loader import load_candles
from src.core.data_simulator import generate_synthetic_candles
from src.core.ring_buffer import RingBuffer


def _validate_positive_int(name: str, value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer, got {value!r}")
    return value


def _latest_scalar(series: Sequence[float | None]) -> float | None:
    for val in reversed(series):
        if val is not None:
            return val
    return None


def _naive_rolling_min_max(values: Sequence[float], window: int) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    for i in range(len(values)):
        seg = values[max(0, i - window + 1) : i + 1]
        out.append((min(seg), max(seg)))
    return out


def run_cli(
    csv_path: str | Path = "data/sample_ohlcv.csv",
    capacity: int = 256,
    window: int = 20,
) -> dict[str, Any]:
    """Run headless OHLCV DSA pipeline and print summary metrics."""
    _validate_positive_int("capacity", capacity)
    _validate_positive_int("window", window)

    candles = load_candles(csv_path)
    ring: RingBuffer[Any] = RingBuffer(capacity)
    for candle in candles:
        ring.push(candle)
    recent = ring.get_all()

    if not recent:
        summary: dict[str, Any] = {
            "total_candles": 0,
            "buffered_candles": 0,
            "range_stats": None,
            "latest_sma": None,
            "latest_ema": None,
            "latest_donchian": None,
            "latest_bollinger": None,
            "lttb_count": 0,
        }
        print("CLI Summary: 0 candles loaded.")
        return summary

    st = SegmentTree(recent)
    stats = st.query(0, len(recent))
    closes = [c.close for c in recent]
    sma = SlidingWindowIndicators.sma(closes, window)
    ema = SlidingWindowIndicators.ema(closes, window)
    donchian = SlidingWindowIndicators.donchian_channels(recent, window)
    bollinger = SlidingWindowIndicators.bollinger_bands(closes, window)
    lttb = LTTBDecimator.downsample([(float(i), c.close) for i, c in enumerate(recent)], min(100, len(recent)))

    summary = {
        "total_candles": len(candles),
        "buffered_candles": len(recent),
        "range_stats": stats,
        "latest_sma": _latest_scalar(sma),
        "latest_ema": _latest_scalar(ema),
        "latest_donchian": donchian[-1] if donchian else None,
        "latest_bollinger": bollinger[-1] if bollinger else None,
        "lttb_count": len(lttb),
    }
    print(
        f"CLI Summary | loaded={len(candles)} buffered={len(recent)} "
        f"min={stats.min_low:.2f} max={stats.max_high:.2f} vol={stats.volume_sum:,.1f} "
        f"lttb={len(lttb)}"
    )
    return summary


def run_benchmark(
    count: int = 10000,
    capacity: int = 256,
    window: int = 20,
) -> dict[str, Any]:
    """Benchmark custom O(1)/O(log N)/O(N) DSA structures against brute-force baselines."""
    _validate_positive_int("count", count)
    _validate_positive_int("capacity", capacity)
    _validate_positive_int("window", window)

    candles = generate_synthetic_candles(count, seed=42)
    closes = [c.close for c in candles]
    points = [(float(i), v) for i, v in enumerate(closes)]
    rng = random.Random(42)
    queries = [
        (lo, hi)
        for lo, hi in (
            sorted((rng.randint(0, count - 1), rng.randint(1, count)))
            for _ in range(500)
        )
    ]

    tracemalloc.start()

    t0 = time.perf_counter()
    ring: RingBuffer[Any] = RingBuffer(capacity)
    for c in candles:
        ring.push(c)
    ring_ms = (time.perf_counter() - t0) * 1000.0

    t0 = time.perf_counter()
    st = SegmentTree(candles)
    st_build_ms = (time.perf_counter() - t0) * 1000.0

    t0 = time.perf_counter()
    for lo, hi in queries:
        st.query(lo, hi)
    st_query_ms = (time.perf_counter() - t0) * 1000.0

    t0 = time.perf_counter()
    for lo, hi in queries:
        scan_range(candles, lo, hi)
    scan_ms = (time.perf_counter() - t0) * 1000.0

    t0 = time.perf_counter()
    SlidingWindowIndicators.rolling_min_max(closes, window)
    mono_ms = (time.perf_counter() - t0) * 1000.0

    t0 = time.perf_counter()
    _naive_rolling_min_max(closes, window)
    naive_mm_ms = (time.perf_counter() - t0) * 1000.0

    t0 = time.perf_counter()
    lttb_out = LTTBDecimator.downsample(points, min(300, count))
    lttb_ms = (time.perf_counter() - t0) * 1000.0

    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    results: dict[str, Any] = {
        "count": count,
        "ring_push_ms": ring_ms,
        "segment_tree_build_ms": st_build_ms,
        "segment_tree_query_ms": st_query_ms,
        "scan_range_ms": scan_ms,
        "monotonic_rolling_ms": mono_ms,
        "naive_rolling_ms": naive_mm_ms,
        "lttb_ms": lttb_ms,
        "lttb_output_len": len(lttb_out),
        "peak_memory_kb": peak_bytes / 1024.0,
    }
    print(
        f"Benchmark (N={count}, W={window}) | "
        f"Ring:{ring_ms:.2f}ms | SegTree 500q:{st_query_ms:.2f}ms vs Scan:{scan_ms:.2f}ms | "
        f"MonoDeque:{mono_ms:.2f}ms vs Naive:{naive_mm_ms:.2f}ms | "
        f"LTTB:{lttb_ms:.2f}ms | PeakRAM:{results['peak_memory_kb']:.1f}KB"
    )
    return results


def run_gui(
    csv_path: str | Path | None = "data/sample_ohlcv.csv",
    capacity: int = 256,
    window: int = 20,
) -> int:
    """Launch the PyQt6 desktop chart window."""
    _validate_positive_int("capacity", capacity)
    _validate_positive_int("window", window)

    from PyQt6.QtWidgets import QApplication
    from src.ui.main_window import MainWindow

    app = QApplication.instance() or QApplication(sys.argv)
    resolved = csv_path if csv_path is None or Path(csv_path).is_file() else None
    win = MainWindow(csv_path=resolved, ring_capacity=capacity, sma_window=window, donchian_window=window)
    win.show()
    return int(app.exec())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interactive TradingView Stock Chart Engine (DSA Python)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--cli", action="store_true", help="Run headless DSA pipeline check")
    mode.add_argument("--benchmark", action="store_true", help="Run performance & memory benchmark")
    mode.add_argument("--gui", action="store_true", help="Launch PyQt6 desktop chart UI (default)")
    parser.add_argument("--csv", default="data/sample_ohlcv.csv", help="Path to OHLCV CSV file")
    parser.add_argument("--count", type=int, default=10000, help="Synthetic candle count for --benchmark")
    parser.add_argument("--capacity", type=int, default=256, help="RingBuffer capacity")
    parser.add_argument("--window", type=int, default=20, help="Sliding-window indicator period")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.cli:
            run_cli(csv_path=args.csv, capacity=args.capacity, window=args.window)
            return 0
        if args.benchmark:
            run_benchmark(count=args.count, capacity=args.capacity, window=args.window)
            return 0
        return run_gui(csv_path=args.csv, capacity=args.capacity, window=args.window)
    except NotImplementedError as exc:
        print(f"[Unsolved TODO] {exc}", file=sys.stderr)
        print("Solve P01-P11 first (`pytest -m p01` .. `pytest -m p11`) before running the app.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
