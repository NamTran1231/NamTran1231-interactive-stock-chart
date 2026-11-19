"""LeetCode Judge for P01 (Candle), P02 (CSV Loader), P03 (RingBuffer), P04 (Simulator)."""

from __future__ import annotations

import ast
import math
from pathlib import Path
import random
from typing import Any

import pytest

from src.core.candle import Candle
from src.core.csv_loader import load_candles, parse_candle_row
from src.core.data_simulator import ReplayDataSource, generate_synthetic_candles
from src.core.ring_buffer import RingBuffer

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _make_candle(ts: int, base: float = 100.0, bullish: bool = True) -> Candle:
    o = base
    c = base + 2.0 if bullish else base - 2.0
    return Candle(timestamp=ts, open=o, high=max(o, c) + 1.5, low=min(o, c) - 1.5, close=c, volume=50.0)


# ---------------------------------------------------------------------------
# P01 — Candle
# ---------------------------------------------------------------------------


@pytest.mark.p01
def test_candle_valid_properties_and_doji() -> None:
    bull = Candle(1700000000, 100, 105.0, 98.0, 103.0, 250.0)
    assert bull.is_bullish is True
    assert bull.body_low == 100.0
    assert bull.body_high == 103.0
    assert isinstance(bull.open, float)

    bear = Candle(1700000060, 103.0, 105.0, 97.0, 99.0, 120.0)
    assert bear.is_bullish is False
    assert bear.body_low == 99.0
    assert bear.body_high == 103.0

    doji = Candle(1700000120, 100.0, 100.0, 100.0, 100.0, 0.0)
    assert doji.is_bullish is True
    assert doji.body_low == 100.0
    assert doji.body_high == 100.0

    with pytest.raises(AttributeError):
        bull.close = 999.0  # type: ignore[misc]


@pytest.mark.p01
@pytest.mark.parametrize("bad_ts", [True, False, 1700000000.5, "1700000000", None])
def test_candle_invalid_timestamp_type_raises_type_error(bad_ts: Any) -> None:
    with pytest.raises(TypeError):
        Candle(timestamp=bad_ts, open=100.0, high=105.0, low=95.0, close=102.0, volume=10.0)


@pytest.mark.p01
@pytest.mark.parametrize(
    "kwargs",
    [
        {"timestamp": -1, "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": 10.0},
        {"timestamp": 10, "open": math.nan, "high": 105.0, "low": 95.0, "close": 102.0, "volume": 10.0},
        {"timestamp": 10, "open": 100.0, "high": math.inf, "low": 95.0, "close": 102.0, "volume": 10.0},
        {"timestamp": 10, "open": 100.0, "high": 105.0, "low": -math.inf, "close": 102.0, "volume": 10.0},
        {"timestamp": 10, "open": 100.0, "high": 105.0, "low": 95.0, "close": math.nan, "volume": 10.0},
        {"timestamp": 10, "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": math.inf},
        {"timestamp": 10, "open": 100.0, "high": 105.0, "low": 95.0, "close": 102.0, "volume": -0.01},
        {"timestamp": 10, "open": 100.0, "high": 106.0, "low": 100.5, "close": 104.0, "volume": 10.0},
        {"timestamp": 10, "open": 100.0, "high": 103.5, "low": 95.0, "close": 104.0, "volume": 10.0},
    ],
)
def test_candle_invalid_values_raise_value_error(kwargs: dict[str, Any]) -> None:
    with pytest.raises(ValueError):
        Candle(**kwargs)


# ---------------------------------------------------------------------------
# P02 — CSV Loader
# ---------------------------------------------------------------------------


@pytest.mark.p02
def test_parse_candle_row_valid_and_errors() -> None:
    good = {
        "timestamp": " 1700000000 ",
        "open": "100.0",
        "high": "105.5",
        "low": "98.2",
        "close": "102.1",
        "volume": "420.5",
    }
    candle = parse_candle_row(good, line_num=2)
    assert candle == Candle(1700000000, 100.0, 105.5, 98.2, 102.1, 420.5)

    for bad_row in (
        {"timestamp": "1700000000", "open": "100"},  # missing columns
        {**good, "timestamp": "1700000000.5"},  # float timestamp
        {**good, "close": "not_a_float"},
        {**good, "high": "90.0"},  # high < open
        {**good, "volume": ""},
    ):
        with pytest.raises(ValueError, match="7"):
            parse_candle_row(bad_row, line_num=7)


@pytest.mark.p02
def test_load_candles_empty_header_only_and_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_candles(tmp_path / "missing.csv")

    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("", encoding="utf-8")
    assert load_candles(empty_file) == []

    header_only = tmp_path / "header_only.csv"
    header_only.write_text("timestamp,open,high,low,close,volume\n", encoding="utf-8")
    assert load_candles(header_only) == []

    bad_header = tmp_path / "bad_header.csv"
    bad_header.write_text("timestamp,open,high,low,close\n1,1,2,0.5,1.5\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_candles(bad_header)


@pytest.mark.p02
def test_load_candles_valid_and_line_error_reporting(tmp_path: Path) -> None:
    valid_csv = tmp_path / "valid.csv"
    valid_csv.write_text(
        "timestamp, open, high, low, close, volume\n"
        "1700000000,100,105,99,104,50\n"
        "\n"
        "1700000060,104,108,101,102,80\n",
        encoding="utf-8",
    )
    candles = load_candles(valid_csv)
    assert len(candles) == 2
    assert candles[0].timestamp == 1700000000
    assert candles[1].timestamp == 1700000060

    dup_ts = tmp_path / "dup_ts.csv"
    dup_ts.write_text(
        "timestamp,open,high,low,close,volume\n"
        "1700000000,100,105,99,104,50\n"
        "1700000000,104,108,101,102,80\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="3"):
        load_candles(dup_ts)

    bad_row = tmp_path / "bad_row.csv"
    bad_row.write_text(
        "timestamp,open,high,low,close,volume\n"
        "1700000000,100,105,99,104,50\n"
        "1700000060,104,100,101,102,80\n",  # high < open
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="3"):
        load_candles(bad_row)

    # Also verify bundled sample dataset loads cleanly.
    sample = load_candles(PROJECT_ROOT / "data" / "sample_ohlcv.csv")
    assert len(sample) == 500


# ---------------------------------------------------------------------------
# P03 — RingBuffer
# ---------------------------------------------------------------------------


@pytest.mark.p03
def test_ring_buffer_ast_forbids_collections_deque() -> None:
    source = (PROJECT_ROOT / "src" / "core" / "ring_buffer.py").read_text(encoding="utf-8")
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


@pytest.mark.p03
@pytest.mark.parametrize("bad_cap", [0, -1, -100])
def test_ring_buffer_non_positive_capacity_raises_value_error(bad_cap: int) -> None:
    with pytest.raises(ValueError):
        RingBuffer(bad_cap)


@pytest.mark.p03
@pytest.mark.parametrize("bad_cap", [True, False, 3.5, "5"])
def test_ring_buffer_bad_type_capacity_raises_type_error(bad_cap: Any) -> None:
    with pytest.raises(TypeError):
        RingBuffer(bad_cap)


@pytest.mark.p03
def test_ring_buffer_push_wraparound_indexing_slicing_iter_clear() -> None:
    rb = RingBuffer[int](3)
    assert rb.capacity == 3
    assert len(rb) == 0
    assert rb.is_empty() and not rb.is_full()
    assert rb.oldest() is None and rb.latest() is None
    assert rb.get_all() == []

    rb.push(10)
    rb.push(20)
    assert (rb.oldest(), rb.latest(), rb.get_all()) == (10, 20, [10, 20])
    assert not rb.is_full()

    rb.push(30)
    assert rb.is_full()
    rb.push(40)
    rb.push(50)
    assert rb.get_all() == [30, 40, 50]
    assert list(rb) == [30, 40, 50]
    assert rb[0] == 30 and rb[1] == 40 and rb[-1] == 50 and rb[-3] == 30
    assert rb[1:] == [40, 50]
    assert rb[::-1] == [50, 40, 30]
    assert "3" in repr(rb)

    with pytest.raises(IndexError):
        _ = rb[3]
    with pytest.raises(IndexError):
        _ = rb[-4]
    with pytest.raises(TypeError):
        _ = rb[True]  # type: ignore[index]

    rb.clear()
    assert len(rb) == 0 and rb.is_empty() and rb.latest() is None and rb.get_all() == []


@pytest.mark.p03
@pytest.mark.parametrize("capacity", [1, 5, 16])
def test_ring_buffer_differential_against_oracle_list(capacity: int) -> None:
    rng = random.Random(100 + capacity)
    rb = RingBuffer[int](capacity)
    oracle: list[int] = []

    for step in range(1000):
        if rng.random() < 0.03:
            rb.clear()
            oracle.clear()
        else:
            val = rng.randint(-10_000, 10_000)
            rb.push(val)
            oracle.append(val)
            if len(oracle) > capacity:
                oracle = oracle[-capacity:]

        assert len(rb) == len(oracle)
        assert rb.get_all() == oracle
        assert list(rb) == oracle
        assert rb.oldest() == (oracle[0] if oracle else None)
        assert rb.latest() == (oracle[-1] if oracle else None)
        assert rb.is_full() == (len(oracle) == capacity)
        if oracle and step % 17 == 0:
            idx = rng.randrange(-len(oracle), len(oracle))
            assert rb[idx] == oracle[idx]


# ---------------------------------------------------------------------------
# P04 — Data Simulator & ReplayDataSource (Factory Method)
# ---------------------------------------------------------------------------


@pytest.mark.p04
def test_generate_synthetic_candles_determinism_and_invariants() -> None:
    assert generate_synthetic_candles(0) == []
    a = generate_synthetic_candles(50, seed=123, start_ts=1700000000, interval_sec=60, start_price=100.0)
    b = generate_synthetic_candles(50, seed=123, start_ts=1700000000, interval_sec=60, start_price=100.0)
    c = generate_synthetic_candles(50, seed=999, start_ts=1700000000, interval_sec=60, start_price=100.0)
    assert a == b
    assert a != c
    assert len(a) == 50
    for i, candle in enumerate(a):
        assert candle.timestamp == 1700000000 + i * 60
        assert candle.low > 0.0

    with pytest.raises(ValueError):
        generate_synthetic_candles(-1)
    with pytest.raises(ValueError):
        generate_synthetic_candles(5, interval_sec=0)
    with pytest.raises(ValueError):
        generate_synthetic_candles(5, start_price=0.0)
    with pytest.raises(TypeError):
        generate_synthetic_candles(True)  # type: ignore[arg-type]


@pytest.mark.p04
def test_replay_data_source_step_reset_upsert_and_factory_methods(tmp_path: Path) -> None:
    # Factory Method: from_synthetic
    src = ReplayDataSource.from_synthetic(3, seed=7)
    assert src.progress == (0, 3)
    assert src.has_next() is True

    played = [src.step(), src.step(), src.step()]
    assert all(c is not None for c in played)
    assert src.has_next() is False
    assert src.step() is None
    assert src.progress == (3, 3)

    src.reset()
    assert src.progress == (0, 3)
    assert src.step() == played[0]

    # replace_or_append
    last = src.candles[-1]
    updated = Candle(last.timestamp, last.open, last.high + 5.0, last.low, last.close + 1.0, last.volume + 10.0)
    assert src.replace_or_append(updated) == ("replaced", 2)
    assert src.candles[-1] == updated

    newer = _make_candle(last.timestamp + 60, base=last.close)
    assert src.replace_or_append(newer) == ("appended", 3)
    assert len(src.candles) == 4

    older = _make_candle(last.timestamp - 60, base=100.0)
    with pytest.raises(ValueError):
        src.replace_or_append(older)

    # Factory Method: from_csv
    csv_file = tmp_path / "mini.csv"
    csv_file.write_text(
        "timestamp,open,high,low,close,volume\n"
        "100,10,12,9,11,5\n"
        "160,11,13,10,12,6\n",
        encoding="utf-8",
    )
    csv_src = ReplayDataSource.from_csv(csv_file)
    assert csv_src.progress == (0, 2)
    assert csv_src.step() == Candle(100, 10.0, 12.0, 9.0, 11.0, 5.0)
