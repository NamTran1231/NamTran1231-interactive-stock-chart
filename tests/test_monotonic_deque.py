"""LeetCode Judge for P05 (CircularDeque, MonotonicDeque, Indicators) and P06 (Coordinate Math)."""

from __future__ import annotations

import ast
import math
from pathlib import Path
import random
import statistics
from typing import Any

import pytest

from src.algorithms.monotonic_deque import (
    CircularDeque,
    MonotonicDeque,
    SlidingWindowIndicators,
)
from src.core.candle import Candle
from src.core.coordinate_math import CoordinateTransformer, ViewportState

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# P05 — CircularDeque, MonotonicDeque & SlidingWindowIndicators
# ---------------------------------------------------------------------------


@pytest.mark.p05
def test_monotonic_deque_ast_forbids_collections_deque() -> None:
    source = (PROJECT_ROOT / "src" / "algorithms" / "monotonic_deque.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith("collections"), "collections import is forbidden"
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert not module.startswith("collections"), "collections import is forbidden"
        elif isinstance(node, ast.Name):
            assert node.id != "deque", "deque usage is forbidden"
        elif isinstance(node, ast.Attribute):
            assert node.attr != "deque", "deque usage is forbidden"


@pytest.mark.p05
def test_circular_deque_empty_errors_and_auto_resize() -> None:
    with pytest.raises(ValueError):
        CircularDeque(0)
    with pytest.raises(TypeError):
        CircularDeque(True)  # type: ignore[arg-type]

    dq = CircularDeque[int](capacity=2)
    assert dq.is_empty() and len(dq) == 0
    for fn in (dq.pop_front, dq.pop_back, dq.peek_front, dq.peek_back):
        with pytest.raises(IndexError):
            fn()

    # Force multiple 2x resizes across wrap-around boundaries
    for i in range(1, 33):
        if i % 2 == 0:
            dq.push_back(i)
        else:
            dq.push_front(i)
    assert len(dq) == 32
    items = dq.to_list()
    assert len(items) == 32
    assert dq.peek_front() == items[0]
    assert dq.peek_back() == items[-1]

    dq.clear()
    assert dq.is_empty() and dq.to_list() == []


@pytest.mark.p05
def test_circular_deque_differential_against_python_list() -> None:
    rng = random.Random(2026)
    dq = CircularDeque[int](capacity=4)
    oracle: list[int] = []

    for _ in range(2000):
        op = rng.randrange(6)
        if op == 0:
            v = rng.randint(-1000, 1000)
            dq.push_front(v)
            oracle.insert(0, v)
        elif op == 1:
            v = rng.randint(-1000, 1000)
            dq.push_back(v)
            oracle.append(v)
        elif op == 2 and oracle:
            assert dq.pop_front() == oracle.pop(0)
        elif op == 3 and oracle:
            assert dq.pop_back() == oracle.pop()
        elif op == 4 and oracle:
            assert dq.peek_front() == oracle[0]
            assert dq.peek_back() == oracle[-1]
        elif op == 5 and rng.random() < 0.05:
            dq.clear()
            oracle.clear()

        assert len(dq) == len(oracle)
        assert dq.is_empty() == (len(oracle) == 0)
        if len(oracle) <= 30:
            assert dq.to_list() == oracle


@pytest.mark.p05
def test_monotonic_deque_min_max_and_eviction() -> None:
    with pytest.raises(ValueError):
        MonotonicDeque("median")

    min_dq = MonotonicDeque("min")
    max_dq = MonotonicDeque("max")
    assert min_dq.extrema() is None and max_dq.extrema() is None

    with pytest.raises(ValueError):
        min_dq.push(0, math.nan)
    with pytest.raises(TypeError):
        min_dq.push(True, 1.0)  # type: ignore[arg-type]

    for idx, val in enumerate([5.0, 2.0, 2.0, 4.0, 1.0]):
        min_dq.push(idx, val)
        max_dq.push(idx, val)

    assert min_dq.extrema() == (4, 1.0)
    assert max_dq.extrema() == (0, 5.0)

    max_dq.evict_before(1)
    assert max_dq.extrema() == (3, 4.0)
    max_dq.evict_before(4)
    assert max_dq.extrema() == (4, 1.0)
    max_dq.evict_before(5)
    assert max_dq.extrema() is None


@pytest.mark.p05
@pytest.mark.parametrize("window", [1, 3, 5, 12])
def test_rolling_min_max_differential_against_bruteforce(window: int) -> None:
    rng = random.Random(500 + window)
    values = [rng.uniform(-50.0, 150.0) for _ in range(120)]
    actual = SlidingWindowIndicators.rolling_min_max(values, window)
    expected = [
        (min(values[max(0, i - window + 1) : i + 1]), max(values[max(0, i - window + 1) : i + 1]))
        for i in range(len(values))
    ]
    assert actual == expected
    assert SlidingWindowIndicators.rolling_min_max([], window) == []


@pytest.mark.p05
def test_sma_and_ema_seeded_formulas() -> None:
    vals = [10.0, 20.0, 30.0, 40.0, 50.0]
    assert SlidingWindowIndicators.sma(vals, 3) == [None, None, pytest.approx(20.0), pytest.approx(30.0), pytest.approx(40.0)]
    assert SlidingWindowIndicators.sma([1.0, 2.0], 5) == [None, None]
    assert SlidingWindowIndicators.sma([], 3) == []

    ema = SlidingWindowIndicators.ema(vals, 3)
    alpha = 2.0 / (3 + 1)
    e2 = 20.0
    e3 = alpha * 40.0 + (1.0 - alpha) * e2
    e4 = alpha * 50.0 + (1.0 - alpha) * e3
    assert ema[0] is None and ema[1] is None
    assert ema[2] == pytest.approx(e2, rel=1e-9)
    assert ema[3] == pytest.approx(e3, rel=1e-9)
    assert ema[4] == pytest.approx(e4, rel=1e-9)

    with pytest.raises(ValueError):
        SlidingWindowIndicators.sma(vals, 0)
    with pytest.raises(ValueError):
        SlidingWindowIndicators.ema(vals, 0)


@pytest.mark.p05
def test_donchian_channels_and_bollinger_bands() -> None:
    candles = [
        Candle(1, 10.0, 12.0, 8.0, 11.0, 1.0),
        Candle(2, 11.0, 15.0, 9.0, 14.0, 1.0),
        Candle(3, 14.0, 14.0, 7.0, 10.0, 1.0),
        Candle(4, 10.0, 13.0, 9.5, 12.0, 1.0),
    ]
    don = SlidingWindowIndicators.donchian_channels(candles, window=2)
    assert don == [
        (12.0, 10.0, 8.0),
        (15.0, 11.5, 8.0),
        (15.0, 11.0, 7.0),
        (14.0, 10.5, 7.0),
    ]

    # Large constant offset tests numerical stability (avoids catastrophic cancellation)
    values = [1_000_000.0 + x for x in (1.0, 2.0, 3.0, 5.0, 2.0, 8.0, 4.0)]
    bb = SlidingWindowIndicators.bollinger_bands(values, window=3, num_std=2.0)
    assert bb[0] == (None, None, None) and bb[1] == (None, None, None)
    for i in range(2, len(values)):
        seg = values[i - 2 : i + 1]
        mean = statistics.fmean(seg)
        std = statistics.pstdev(seg)
        u, m, lo = bb[i]
        assert m == pytest.approx(mean, abs=1e-6)
        assert u == pytest.approx(mean + 2.0 * std, abs=1e-6)
        assert lo == pytest.approx(mean - 2.0 * std, abs=1e-6)

    with pytest.raises(ValueError):
        SlidingWindowIndicators.bollinger_bands(values, window=3, num_std=-1.0)


# ---------------------------------------------------------------------------
# P06 — CoordinateTransformer & ViewportState (Prototype)
# ---------------------------------------------------------------------------


@pytest.mark.p06
def test_coordinate_transformer_round_trip_zoom_and_pan() -> None:
    vp = ViewportState(
        start_idx=10.0,
        end_idx=110.0,
        min_price=50.0,
        max_price=150.0,
        width_px=884,
        height_px=444,
    )
    assert vp.plot_left == 12.0
    assert vp.plot_right == 812.0
    assert vp.plot_width == 800.0
    assert vp.plot_top == 16.0
    assert vp.plot_bottom == 416.0
    assert vp.plot_height == 400.0

    ct = CoordinateTransformer(vp)
    assert ct.viewport is vp
    assert ct.index_to_x(10.0) == pytest.approx(vp.plot_left)
    assert ct.index_to_x(110.0) == pytest.approx(vp.plot_right)
    assert ct.price_to_y(150.0) == pytest.approx(vp.plot_top)
    assert ct.price_to_y(50.0) == pytest.approx(vp.plot_bottom)

    for idx, price in ((10.0, 50.0), (35.5, 112.75), (110.0, 150.0)):
        sx, sy = ct.world_to_screen(idx, price)
        w_idx, w_price = ct.screen_to_world(sx, sy)
        assert w_idx == pytest.approx(idx, abs=1e-9)
        assert w_price == pytest.approx(price, abs=1e-9)

    # Cursor-anchored zoom invariant + Prototype immutability
    anchor_x = vp.plot_left + 0.3 * vp.plot_width
    anchor_before = ct.x_to_index(anchor_x)
    zoomed = ct.zoom_at_pixel(anchor_x, zoom_factor=2.0)
    assert zoomed is not vp
    assert vp.start_idx == 10.0 and vp.end_idx == 110.0  # original unchanged
    assert (zoomed.end_idx - zoomed.start_idx) == pytest.approx(50.0, abs=1e-9)
    assert CoordinateTransformer(zoomed).x_to_index(anchor_x) == pytest.approx(anchor_before, abs=1e-9)

    # Pan right shifts visible window left (earlier in time)
    panned = ct.pan_by_pixels(dx_px=80.0)
    assert panned.start_idx == pytest.approx(0.0, abs=1e-9)
    assert panned.end_idx == pytest.approx(100.0, abs=1e-9)

    with pytest.raises(ValueError):
        ct.zoom_at_pixel(anchor_x, zoom_factor=0.0)
    with pytest.raises(ValueError):
        ct.zoom_at_pixel(anchor_x, zoom_factor=-1.5)


@pytest.mark.p06
@pytest.mark.parametrize(
    ("min_p", "max_p", "width", "height"),
    [
        (100.0, 100.0, 800, 400),
        (90.0, 110.0, 0, 400),
        (90.0, 110.0, 800, 0),
        (90.0, 110.0, -50, -20),
        (100.0, 100.0, 0, 0),
    ],
)
def test_coordinate_transformer_degenerate_inputs_do_not_divide_by_zero(
    min_p: float,
    max_p: float,
    width: int,
    height: int,
) -> None:
    vp = ViewportState(5.0, 5.0, min_p, max_p, width, height)
    ct = CoordinateTransformer(vp)
    sx, sy = ct.world_to_screen(5.0, min_p)
    wx, wy = ct.screen_to_world(sx, sy)
    assert all(math.isfinite(v) for v in (sx, sy, wx, wy))
