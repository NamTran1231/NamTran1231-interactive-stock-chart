"""[P08] LTTB Decimator & OHLCV Bucket Aggregator (Medium).

Run tests:
    pytest -m p08

Problem:
    1. `LTTBDecimator.downsample(points, threshold)`: reduce a 2D polyline
       `(x, y)` to at most `threshold` points in O(N) using Largest-Triangle-
       Three-Buckets (Steinarsson, 2013) so visual peaks/valleys survive zoom-out.
    2. `aggregate_ohlcv_buckets(candles, start_idx, end_idx, max_candles)`:
       compress `candles[start_idx:end_idx]` into at most `max_candles`
       aggregated candles in O(M) while preserving exact OHLCV invariants.

Constraints:
    - `LTTBDecimator.downsample`:
      - `threshold < 0` (or `bool`/non-`int`) -> raise `ValueError`.
      - `threshold == 0` or empty `points` -> `[]`.
      - `threshold == 1` -> `[(float(points[0][0]), float(points[0][1]))]`.
      - `len(points) <= threshold` -> all points cast to `(float(x), float(y))`.
      - For `len(points) > threshold >= 2`: output has exact length `threshold`,
        strictly preserves first and last points, and runs in O(N) time.
    - `aggregate_ohlcv_buckets`:
      - `max_candles <= 0` (or `bool`/non-`int`) -> raise `ValueError`.
      - Clamp `[start_idx, end_idx)` into `[0, len(candles)]`; empty -> `[]`.
      - If `end - start <= max_candles` -> `list(candles[start:end])`.
      - Otherwise merge contiguous buckets with:
        `timestamp = first.timestamp`, `open = first.open`,
        `high = max(high)`, `low = min(low)`,
        `close = last.close`, `volume = sum(volume)`.

Example:
    >>> LTTBDecimator.downsample([(0, 0), (1, 0), (2, 100), (3, 0), (4, 0)], 3)
    [(0.0, 0.0), (2.0, 100.0), (4.0, 0.0)]
"""

from __future__ import annotations

from collections.abc import Sequence

from src.core.candle import Candle


class LTTBDecimator:
    """Largest-Triangle-Three-Buckets time-series downsampler."""

    @staticmethod
    def downsample(
        points: Sequence[tuple[float, float]],
        threshold: int,
    ) -> list[tuple[float, float]]:
        """Downsample `(x, y)` points to at most `threshold` points in O(N)."""
        raise NotImplementedError("TODO(P08): implement LTTBDecimator.downsample")


def aggregate_ohlcv_buckets(
    candles: Sequence[Candle],
    start_idx: int,
    end_idx: int,
    max_candles: int,
) -> list[Candle]:
    """Aggregate `candles[start_idx:end_idx]` into at most `max_candles` candles in O(M)."""
    raise NotImplementedError("TODO(P08): implement aggregate_ohlcv_buckets")
