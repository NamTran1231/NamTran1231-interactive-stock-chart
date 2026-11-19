"""LeetCode Judge for P07 (SegmentTree & scan_range Oracle)."""

from __future__ import annotations

import random

import pytest

from src.algorithms.segment_tree import RangeStats, SegmentTree, scan_range
from src.core.candle import Candle


def _make_candle(ts: int, rng: random.Random) -> Candle:
    o = rng.uniform(50.0, 200.0)
    c = rng.uniform(50.0, 200.0)
    hi = max(o, c) + rng.uniform(0.0, 10.0)
    lo = min(o, c) - rng.uniform(0.0, 10.0)
    vol = rng.uniform(0.0, 1000.0)
    return Candle(ts, o, hi, lo, c, vol)


def _assert_stats_match(actual: RangeStats | None, expected: RangeStats | None) -> None:
    if expected is None:
        assert actual is None
    else:
        assert actual is not None
        assert actual.min_low == pytest.approx(expected.min_low, rel=1e-9, abs=1e-9)
        assert actual.max_high == pytest.approx(expected.max_high, rel=1e-9, abs=1e-9)
        assert actual.volume_sum == pytest.approx(expected.volume_sum, rel=1e-9, abs=1e-7)


@pytest.mark.p07
def test_segment_tree_edge_cases_and_capacity_doubling() -> None:
    empty = SegmentTree()
    assert len(empty) == 0
    assert empty.query(0, 1) is None
    assert scan_range([], 0, 1) is None
    with pytest.raises(IndexError):
        empty.get_candle(0)
    with pytest.raises(IndexError):
        empty.update(0, Candle(1, 10.0, 11.0, 9.0, 10.0, 1.0))

    # Grow through power-of-2 boundaries: 0 -> 1 -> 2 -> 4 -> 8 -> 16 -> 20
    rng = random.Random(77)
    candles: list[Candle] = []
    st = SegmentTree()
    for i in range(20):
        c = _make_candle(1000 + i * 60, rng)
        candles.append(c)
        st.append(c)
        assert len(st) == len(candles)
        assert st.get_candle(i) == c
        _assert_stats_match(st.query(0, len(candles)), scan_range(candles, 0, len(candles)))

    # Clamping & inverted/empty ranges
    _assert_stats_match(st.query(-5, 999), scan_range(candles, -5, 999))
    assert st.query(5, 5) is None
    assert st.query(8, 3) is None
    assert st.query(20, 25) is None

    # Update single element and verify
    replacement = Candle(candles[7].timestamp, 500.0, 600.0, 1.0, 550.0, 9999.0)
    candles[7] = replacement
    st.update(7, replacement)
    assert st.get_candle(7) == replacement
    _assert_stats_match(st.query(0, 20), scan_range(candles, 0, 20))
    _assert_stats_match(st.query(7, 8), scan_range(candles, 7, 8))

    with pytest.raises(IndexError):
        st.update(-1, replacement)
    with pytest.raises(IndexError):
        st.update(20, replacement)


@pytest.mark.p07
def test_segment_tree_randomized_differential_against_scan_range() -> None:
    rng = random.Random(202607)
    # Start with non-power-of-2 size (13)
    candles = [_make_candle(i * 60, rng) for i in range(13)]
    st = SegmentTree(candles)
    next_ts = 13 * 60

    for _ in range(2000):
        roll = rng.random()
        if roll < 0.70:
            lo = rng.randint(-3, len(candles) + 3)
            hi = rng.randint(-3, len(candles) + 3)
            _assert_stats_match(st.query(lo, hi), scan_range(candles, lo, hi))
        elif roll < 0.88:
            idx = rng.randrange(len(candles))
            c = _make_candle(candles[idx].timestamp, rng)
            candles[idx] = c
            st.update(idx, c)
        else:
            c = _make_candle(next_ts, rng)
            next_ts += 60
            candles.append(c)
            st.append(c)

    _assert_stats_match(st.query(0, len(candles)), scan_range(candles, 0, len(candles)))
