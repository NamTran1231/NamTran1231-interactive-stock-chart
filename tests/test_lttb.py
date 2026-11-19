"""LeetCode Judge for P08 (LTTB & OHLCV Buckets) and P09 (QuadTree)."""

from __future__ import annotations

import math
import random

import pytest

from src.algorithms.lttb_decimator import LTTBDecimator, aggregate_ohlcv_buckets
from src.algorithms.quad_tree import Bounds, QuadTree, SpatialPoint
from src.core.candle import Candle


# ---------------------------------------------------------------------------
# P08 — LTTBDecimator & aggregate_ohlcv_buckets
# ---------------------------------------------------------------------------


@pytest.mark.p08
def test_lttb_downsample_thresholds_and_endpoints() -> None:
    pts = [(float(i), math.sin(i * 0.2) * 10.0) for i in range(50)]

    with pytest.raises(ValueError):
        LTTBDecimator.downsample(pts, -1)
    assert LTTBDecimator.downsample([], 10) == []
    assert LTTBDecimator.downsample(pts, 0) == []
    assert LTTBDecimator.downsample(pts, 1) == [pts[0]]
    assert LTTBDecimator.downsample(pts, 2) == [pts[0], pts[-1]]
    assert LTTBDecimator.downsample(pts, 50) == pts
    assert LTTBDecimator.downsample(pts, 100) == pts

    out = LTTBDecimator.downsample(pts, 12)
    assert len(out) == 12
    assert out[0] == pts[0]
    assert out[-1] == pts[-1]
    assert all(out[i][0] < out[i + 1][0] for i in range(len(out) - 1))


@pytest.mark.p08
def test_lttb_preserves_sharp_visual_spike() -> None:
    pts = [(float(i), 100.0) for i in range(100)]
    pts[47] = (47.0, 500.0)
    out = LTTBDecimator.downsample(pts, 10)
    assert len(out) == 10
    assert (47.0, 500.0) in out


@pytest.mark.p08
def test_aggregate_ohlcv_buckets_preserves_ohlcv_invariants() -> None:
    rng = random.Random(88)
    candles = []
    price = 100.0
    for i in range(100):
        o = price
        c = max(1.0, o + rng.uniform(-3.0, 3.0))
        hi = max(o, c) + rng.uniform(0.0, 2.0)
        lo = max(0.1, min(o, c) - rng.uniform(0.0, 2.0))
        candles.append(Candle(1000 + i * 60, o, hi, lo, c, rng.uniform(10.0, 500.0)))
        price = c

    with pytest.raises(ValueError):
        aggregate_ohlcv_buckets(candles, 0, 50, 0)

    assert aggregate_ohlcv_buckets([], 0, 10, 5) == []
    assert aggregate_ohlcv_buckets(candles, 20, 20, 5) == []
    assert aggregate_ohlcv_buckets(candles, 10, 15, 20) == candles[10:15]

    agg = aggregate_ohlcv_buckets(candles, 10, 90, max_candles=15)
    src = candles[10:90]
    assert 1 <= len(agg) <= 15
    assert agg[0].timestamp == src[0].timestamp
    assert agg[0].open == src[0].open
    assert agg[-1].close == src[-1].close
    assert max(c.high for c in agg) == pytest.approx(max(c.high for c in src))
    assert min(c.low for c in agg) == pytest.approx(min(c.low for c in src))
    assert sum(c.volume for c in agg) == pytest.approx(sum(c.volume for c in src), rel=1e-9)


# ---------------------------------------------------------------------------
# P09 — QuadTree
# ---------------------------------------------------------------------------


@pytest.mark.p09
def test_quad_tree_bounds_subdivision_duplicates_and_range_query() -> None:
    with pytest.raises(ValueError):
        Bounds(10.0, 0.0, 5.0, 10.0)
    with pytest.raises(ValueError):
        Bounds(0.0, 0.0, math.inf, 10.0)

    root = Bounds(0.0, 0.0, 100.0, 100.0)
    assert root.contains(0.0, 0.0) and root.contains(100.0, 100.0)
    assert not root.contains(100.1, 50.0)
    assert root.distance_sq_to_point(50.0, 50.0) == 0.0
    assert root.distance_sq_to_point(103.0, 104.0) == pytest.approx(25.0)
    assert root.intersects(Bounds(100.0, 100.0, 120.0, 120.0))
    assert not root.intersects(Bounds(101.0, 0.0, 120.0, 10.0))

    with pytest.raises(ValueError):
        QuadTree(root, capacity=0)

    qt = QuadTree[int](root, capacity=4, max_depth=8)
    assert qt.insert(SpatialPoint(-1.0, 5.0, -1)) is False
    assert len(qt) == 0

    # Identical coordinates beyond capacity must not hit RecursionError
    for i in range(12):
        assert qt.insert(SpatialPoint(25.0, 25.0, i)) is True
    assert len(qt) == 12

    rng = random.Random(909)
    points: list[SpatialPoint[int]] = [SpatialPoint(25.0, 25.0, i) for i in range(12)]
    for i in range(12, 212):
        p = SpatialPoint(rng.uniform(0.0, 100.0), rng.uniform(0.0, 100.0), i)
        assert qt.insert(p) is True
        points.append(p)
    assert len(qt) == len(points)

    rect = Bounds(20.0, 20.0, 65.0, 75.0)
    found = {p.payload for p in qt.query_range(rect)}
    expected = {p.payload for p in points if rect.contains(p.x, p.y)}
    assert found == expected


@pytest.mark.p09
def test_quad_tree_nearest_differential_against_bruteforce() -> None:
    root = Bounds(0.0, 0.0, 500.0, 500.0)
    qt = QuadTree[int](root, capacity=4)
    assert qt.nearest(10.0, 10.0) is None
    with pytest.raises(ValueError):
        qt.nearest(10.0, 10.0, max_dist=-1.0)

    rng = random.Random(999)
    points = [SpatialPoint(rng.uniform(0.0, 500.0), rng.uniform(0.0, 500.0), i) for i in range(250)]
    for p in points:
        qt.insert(p)

    for _ in range(100):
        qx, qy = rng.uniform(-20.0, 520.0), rng.uniform(-20.0, 520.0)
        max_d = rng.choice([float("inf"), 15.0, 40.0])

        best_dist_sq = min((p.x - qx) ** 2 + (p.y - qy) ** 2 for p in points)
        got = qt.nearest(qx, qy, max_dist=max_d)
        if best_dist_sq > max_d * max_d:
            assert got is None
        else:
            assert got is not None
            got_dist_sq = (got.x - qx) ** 2 + (got.y - qy) ** 2
            assert got_dist_sq == pytest.approx(best_dist_sq, rel=1e-9, abs=1e-9)
