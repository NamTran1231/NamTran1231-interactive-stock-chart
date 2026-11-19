"""Pre-built PyQt6 MainWindow workbench (DO NOT EDIT for P01-P11).

Wires `ChartCanvasWidget`, `RingBuffer`, `ReplayDataSource` (via Factory Methods
`from_csv` / `from_synthetic`), `EventBus` (Observer), `CommandHistory` (Command),
and `QTimer` replay controls.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QLabel,
    QMainWindow,
    QToolBar,
    QWidget,
)

from src.algorithms.segment_tree import RangeStats
from src.core.candle import Candle
from src.core.data_simulator import ReplayDataSource
from src.core.ring_buffer import RingBuffer
from src.patterns.command_history import CommandHistory
from src.patterns.observer import EventBus
from src.ui.chart_canvas import ChartCanvasWidget

BASE_REPLAY_INTERVAL_MS = 400
_SPEED_OPTIONS: tuple[tuple[str, float], ...] = (
    ("1x", 1.0),
    ("2x", 2.0),
    ("5x", 5.0),
    ("10x", 10.0),
)


class MainWindow(QMainWindow):
    """Interactive TradingView-style desktop shell backed by student DSA modules."""

    def __init__(
        self,
        csv_path: str | Path | None = None,
        ring_capacity: int = 256,
        sma_window: int = 20,
        donchian_window: int = 20,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Interactive TradingView Chart Engine (DSA Python)")
        self.resize(1280, 780)

        self._event_bus = EventBus()
        self._command_history = CommandHistory()
        self._ring_buffer: RingBuffer[Candle] = RingBuffer(ring_capacity)
        self._canvas = ChartCanvasWidget(
            event_bus=self._event_bus,
            command_history=self._command_history,
            sma_window=sma_window,
            donchian_window=donchian_window,
            parent=self,
        )
        self.setCentralWidget(self._canvas)

        self._replay_source: ReplayDataSource | None = None
        self._timer = QTimer(self)
        self._timer.setInterval(BASE_REPLAY_INTERVAL_MS)

        self._apply_dark_stylesheet()
        self._build_toolbar()
        self._build_status_bar()
        self._bind_events()

        if csv_path is not None:
            self.load_csv_file(csv_path)
        else:
            self._load_source(ReplayDataSource.from_synthetic(200, seed=42))

    @property
    def canvas(self) -> ChartCanvasWidget:
        return self._canvas

    @property
    def ring_buffer(self) -> RingBuffer[Candle]:
        return self._ring_buffer

    @property
    def event_bus(self) -> EventBus:
        return self._event_bus

    @property
    def command_history(self) -> CommandHistory:
        return self._command_history

    @property
    def replay_source(self) -> ReplayDataSource | None:
        return self._replay_source

    def _apply_dark_stylesheet(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow { background-color: #131722; color: #d1d4dc; }
            QToolBar { background-color: #1e222d; border-bottom: 1px solid #2a2e39; spacing: 6px; padding: 4px; }
            QToolButton, QComboBox { color: #d1d4dc; background-color: #2a2e39; border: 1px solid #363a45; border-radius: 3px; padding: 4px 8px; }
            QToolButton:checked { background-color: #2962ff; border-color: #2962ff; }
            QStatusBar { background-color: #1e222d; color: #d1d4dc; border-top: 1px solid #2a2e39; }
            """
        )

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Controls", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        open_action = QAction("Open CSV", self)
        open_action.triggered.connect(self._on_open_csv_dialog)
        toolbar.addAction(open_action)

        toolbar.addSeparator()
        self._play_action = QAction("Play", self)
        self._play_action.triggered.connect(self._on_toggle_play_pause)
        toolbar.addAction(self._play_action)

        step_action = QAction("Step", self)
        step_action.triggered.connect(self.step_replay)
        toolbar.addAction(step_action)

        reset_action = QAction("Reset", self)
        reset_action.triggered.connect(self.reset_replay)
        toolbar.addAction(reset_action)

        self._speed_combo = QComboBox(self)
        for label, mult in _SPEED_OPTIONS:
            self._speed_combo.addItem(label, mult)
        self._speed_combo.currentIndexChanged.connect(self._on_speed_combo_changed)
        toolbar.addWidget(self._speed_combo)

        toolbar.addSeparator()
        fit_action = QAction("Fit All", self)
        fit_action.triggered.connect(lambda: self._canvas.fit_all(record_history=True))
        toolbar.addAction(fit_action)

        self._sma_action = QAction("SMA", self)
        self._sma_action.setCheckable(True)
        self._sma_action.setChecked(True)
        self._sma_action.toggled.connect(lambda checked: self._canvas.set_overlays(sma=checked))
        toolbar.addAction(self._sma_action)

        self._donchian_action = QAction("Donchian", self)
        self._donchian_action.setCheckable(True)
        self._donchian_action.setChecked(True)
        self._donchian_action.toggled.connect(lambda checked: self._canvas.set_overlays(donchian=checked))
        toolbar.addAction(self._donchian_action)

        self._volume_action = QAction("Volume", self)
        self._volume_action.setCheckable(True)
        self._volume_action.setChecked(True)
        self._volume_action.toggled.connect(lambda checked: self._canvas.set_overlays(volume=checked))
        toolbar.addAction(self._volume_action)

        toolbar.addSeparator()
        self._undo_action = QAction("Undo", self)
        self._undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self._undo_action.triggered.connect(self._on_undo)
        toolbar.addAction(self._undo_action)

        self._redo_action = QAction("Redo", self)
        self._redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self._redo_action.triggered.connect(self._on_redo)
        toolbar.addAction(self._redo_action)
        self._sync_history_actions()

    def _build_status_bar(self) -> None:
        bar = self.statusBar()
        self._hover_label = QLabel("Hover: -", self)
        self._stats_label = QLabel("Range: -", self)
        self._replay_label = QLabel("Replay: 0/0 | Ring: 0", self)
        bar.addWidget(self._hover_label, 2)
        bar.addPermanentWidget(self._stats_label)
        bar.addPermanentWidget(self._replay_label)

    def _bind_events(self) -> None:
        self._timer.timeout.connect(self.step_replay)
        self._event_bus.subscribe("viewport_changed", lambda _vp, stats: self._refresh_status_bar(stats))
        self._event_bus.subscribe("hover_candle_changed", self._on_hover_candle_changed)
        self._event_bus.subscribe("history_changed", self._sync_history_actions)

    def _sync_history_actions(self) -> None:
        self._undo_action.setEnabled(self._command_history.can_undo())
        self._redo_action.setEnabled(self._command_history.can_redo())

    def _on_undo(self) -> None:
        self._command_history.undo()
        self._sync_history_actions()

    def _on_redo(self) -> None:
        self._command_history.redo()
        self._sync_history_actions()

    def _on_open_csv_dialog(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Open OHLCV CSV", "", "CSV Files (*.csv)")
        if file_path:
            self.load_csv_file(file_path)

    def _on_toggle_play_pause(self) -> None:
        if self._timer.isActive():
            self.pause_replay()
        else:
            self.play_replay()

    def _on_speed_combo_changed(self, index: int) -> None:
        mult = self._speed_combo.itemData(index)
        if mult is not None:
            self.set_replay_speed(float(mult))

    def _on_hover_candle_changed(self, candle: Candle | None, index: float | None) -> None:
        if candle is None:
            self._hover_label.setText("Hover: -")
        else:
            idx_str = f"#{int(index)}" if index is not None else ""
            self._hover_label.setText(
                f"{idx_str} O:{candle.open:.2f} H:{candle.high:.2f} L:{candle.low:.2f} C:{candle.close:.2f} V:{candle.volume:.1f}"
            )

    def _refresh_status_bar(self, stats: RangeStats | None) -> None:
        if stats is None:
            self._stats_label.setText("Range: -")
        else:
            self._stats_label.setText(
                f"Low:{stats.min_low:.2f} High:{stats.max_high:.2f} Vol:{stats.volume_sum:,.1f}"
            )
        cur, total = self._replay_source.progress if self._replay_source is not None else (0, 0)
        self._replay_label.setText(
            f"Replay: {cur}/{total} | Ring: {len(self._ring_buffer)}/{self._ring_buffer.capacity}"
        )
        self._sync_history_actions()

    def play_replay(self) -> None:
        if self._replay_source is not None and self._replay_source.has_next() and not self._timer.isActive():
            self._timer.start()
            self._play_action.setText("Pause")

    def pause_replay(self) -> None:
        if self._timer.isActive():
            self._timer.stop()
        self._play_action.setText("Play")

    def step_replay(self) -> Candle | None:
        if self._replay_source is None:
            return None
        candle = self._replay_source.step()
        if candle is None:
            self.pause_replay()
            return None
        self._ring_buffer.push(candle)
        self._canvas.append_or_update_candle(candle, auto_follow=True)
        self._refresh_status_bar(self._canvas.get_visible_range_stats())
        return candle

    def reset_replay(self) -> None:
        self.pause_replay()
        if self._replay_source is None:
            return
        self._replay_source.reset()
        self._ring_buffer.clear()
        self._command_history.clear()
        self._canvas.set_candles([], fit=True)
        self._refresh_status_bar(None)

    def set_replay_speed(self, multiplier: float) -> None:
        if multiplier <= 0:
            raise ValueError("Replay speed multiplier must be > 0")
        self._timer.setInterval(max(10, int(BASE_REPLAY_INTERVAL_MS / multiplier)))

    def _load_source(self, source: ReplayDataSource) -> list[Candle]:
        self.pause_replay()
        self._replay_source = source
        candles = source.candles
        self._ring_buffer.clear()
        self._command_history.clear()

        # Seed initial half so the chart displays immediately while leaving candles to replay.
        seed_count = len(candles) if len(candles) <= 1 else min(len(candles) // 2, self._ring_buffer.capacity)
        seeded: list[Candle] = []
        for _ in range(seed_count):
            c = source.step()
            if c is None:
                break
            self._ring_buffer.push(c)
            seeded.append(c)

        self._canvas.set_candles(seeded, fit=True)
        self._refresh_status_bar(self._canvas.get_visible_range_stats())
        return candles

    def load_csv_file(self, path: str | Path) -> list[Candle]:
        return self._load_source(ReplayDataSource.from_csv(path))
