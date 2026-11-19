"""LeetCode Judge for P10 (EventBus), P11 (CommandHistory), and Final Boss Integration."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest
from PyQt6.QtWidgets import QApplication

from src.core.candle import Candle
from src.core.coordinate_math import ViewportState
from src.core.data_simulator import generate_synthetic_candles
from src.main import build_parser, run_benchmark, run_cli
from src.patterns.command_history import Command, CommandHistory, ViewportChangeCommand
from src.patterns.observer import EventBus
from src.ui.chart_canvas import ChartCanvasWidget, VisibleFrame
from src.ui.main_window import MainWindow

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    assert isinstance(app, QApplication)
    return app


# ---------------------------------------------------------------------------
# P10 — EventBus (Observer Pattern)
# ---------------------------------------------------------------------------


@pytest.mark.p10
def test_event_bus_subscribe_publish_unsubscribe_and_self_removal() -> None:
    bus = EventBus()
    received: list[tuple[Any, ...]] = []

    with pytest.raises(ValueError):
        bus.subscribe("", lambda: None)
    with pytest.raises(TypeError):
        bus.subscribe("tick", "not_callable")  # type: ignore[arg-type]

    def listener_a(symbol: str, price: float) -> None:
        received.append(("a", symbol, price))

    unsub_a = bus.subscribe("tick", listener_a)
    bus.subscribe("tick", listener_a)  # duplicate ignored
    assert bus.listener_count("tick") == 1

    # Self-unsubscribing listener during publish must not break iteration
    def once(symbol: str, price: float) -> None:
        received.append(("once", symbol, price))
        bus.unsubscribe("tick", once)

    bus.subscribe("tick", once)
    assert bus.publish("tick", "BTC", price=65000.0) == 2
    assert received == [("a", "BTC", 65000.0), ("once", "BTC", 65000.0)]
    assert bus.listener_count("tick") == 1

    unsub_a()
    assert bus.listener_count("tick") == 0
    assert bus.unsubscribe("tick", listener_a) is False
    assert bus.publish("tick", "BTC", price=66000.0) == 0

    bus.subscribe("e1", lambda: None)
    bus.subscribe("e2", lambda: None)
    assert bus.listener_count() == 2
    bus.clear("e1")
    assert bus.listener_count() == 1
    bus.clear()
    assert bus.listener_count() == 0


# ---------------------------------------------------------------------------
# P11 — Command & CommandHistory
# ---------------------------------------------------------------------------


class _AddCommand(Command):
    def __init__(self, box: list[int], delta: int) -> None:
        self._box = box
        self._delta = delta

    @property
    def description(self) -> str:
        return f"Add {self._delta}"

    def execute(self) -> None:
        self._box[0] += self._delta

    def undo(self) -> None:
        self._box[0] -= self._delta


@pytest.mark.p11
def test_command_history_undo_redo_max_size_and_redo_reset() -> None:
    with pytest.raises(ValueError):
        CommandHistory(0)
    with pytest.raises(TypeError):
        CommandHistory(True)  # type: ignore[arg-type]

    box = [0]
    history = CommandHistory(max_size=3)
    assert history.max_size == 3
    assert len(history) == 0 and not history.can_undo() and not history.can_redo()
    assert history.undo() is None and history.redo() is None

    for d in (1, 2, 3, 4):
        history.execute(_AddCommand(box, d))
    assert box == [10]
    assert len(history) == 3  # oldest (1) dropped due to max_size=3

    cmd = history.undo()
    assert cmd is not None and cmd.description == "Add 4"
    assert box == [6] and history.can_redo()

    # Executing a new command clears redo branch
    history.execute(_AddCommand(box, 100))
    assert box == [106] and not history.can_redo()

    history.undo()
    assert box == [6]
    history.redo()
    assert box == [106]

    history.clear()
    assert len(history) == 0 and not history.can_undo() and not history.can_redo()


@pytest.mark.p11
def test_viewport_change_command() -> None:
    vp0 = ViewportState(0.0, 50.0, 90.0, 110.0, 800, 500)
    vp1 = ViewportState(10.0, 60.0, 95.0, 115.0, 800, 500)
    current = [vp0]

    with pytest.raises(TypeError):
        ViewportChangeCommand("bad", vp0, vp1)  # type: ignore[arg-type]

    cmd = ViewportChangeCommand(lambda vp: current.__setitem__(0, vp), vp0, vp1, "Pan")
    assert cmd.description == "Pan"
    assert cmd.old_viewport == vp0 and cmd.new_viewport == vp1

    history = CommandHistory()
    history.execute(cmd)
    assert current[0] == vp1
    history.undo()
    assert current[0] == vp0
    history.redo()
    assert current[0] == vp1


# ---------------------------------------------------------------------------
# Final Boss — Integration (unlocks when P01–P11 all pass!)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_chart_canvas_widget_headless_render_and_updates(qapp: QApplication) -> None:
    candles = generate_synthetic_candles(450, seed=42)
    canvas = ChartCanvasWidget()
    canvas.resize(900, 500)

    # Empty state safe
    empty_frame = canvas.compute_visible_frame(900, 500)
    assert empty_frame.total_candles == 0 and empty_frame.range_stats is None

    canvas.set_candles(candles, fit=True)
    frame = canvas.compute_visible_frame(900, 500, max_render_candles=200)
    assert isinstance(frame, VisibleFrame)
    assert frame.total_candles == 450
    assert frame.range_stats is not None
    assert len(frame.render_candles) <= 200
    assert len(frame.decimated_close_points) <= 200

    # Forming-candle update & new-candle append
    last = candles[-1]
    forming = Candle(last.timestamp, last.open, last.high + 2.0, last.low, last.close + 0.5, last.volume + 5.0)
    assert canvas.append_or_update_candle(forming) == "updated"
    next_c = Candle(last.timestamp + 60, last.close, last.close + 3.0, last.close - 1.0, last.close + 1.0, 25.0)
    assert canvas.append_or_update_candle(next_c) == "appended"
    assert len(canvas.candles) == 451

    # Offscreen QPainter render smoke check
    pixmap = canvas.grab()
    assert not pixmap.isNull()


@pytest.mark.integration
def test_main_window_load_csv_replay_ring_buffer_and_render(qapp: QApplication) -> None:
    sample_csv = PROJECT_ROOT / "data" / "sample_ohlcv.csv"
    win = MainWindow(csv_path=sample_csv, ring_capacity=64)
    assert len(win.ring_buffer) == 64
    assert win.replay_source is not None

    before_cur, total = win.replay_source.progress
    assert total == 500 and before_cur < total

    stepped = win.step_replay()
    assert stepped is not None
    assert win.ring_buffer.latest() == stepped
    assert win.replay_source.progress[0] == before_cur + 1

    # Undo/Redo via Fit All
    win.canvas.fit_all(record_history=True)
    assert win.command_history.can_undo()
    win._on_undo()
    assert win.command_history.can_redo()

    pixmap = win.canvas.grab()
    assert not pixmap.isNull()
    win.close()


@pytest.mark.integration
def test_cli_and_benchmark_smoke() -> None:
    parser = build_parser()
    parsed = parser.parse_args(["--cli", "--csv", "data/sample_ohlcv.csv"])
    assert parsed.cli is True and parsed.benchmark is False

    cli_out = run_cli(PROJECT_ROOT / "data" / "sample_ohlcv.csv", capacity=128, window=20)
    assert cli_out["total_candles"] == 500
    assert cli_out["buffered_candles"] == 128
    assert cli_out["range_stats"] is not None
    assert 1 <= cli_out["lttb_count"] <= 100

    bench_out = run_benchmark(count=1500, capacity=128, window=20)
    assert bench_out["count"] == 1500
    assert bench_out["lttb_output_len"] == 300
    assert bench_out["peak_memory_kb"] > 0.0
