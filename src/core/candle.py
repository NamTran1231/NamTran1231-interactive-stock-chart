"""[P01] Candle — Immutable OHLCV Domain Model (Easy).

Run tests:
    pytest -m p01

Problem:
    Implement validation and derived properties for an immutable OHLCV
    candlestick (`Candle`). Every downstream algorithm and chart widget assumes
    `Candle` objects satisfy financial invariants.

Constraints:
    - `timestamp`: must be a real `int` (reject `bool`, `float`, `str`, `None`
      with `TypeError`) and `>= 0` (else `ValueError`).
    - `open`, `high`, `low`, `close`, `volume`: must be real finite numbers
      (reject `bool` / non-numeric with `TypeError`; reject `NaN` / `±Inf` with
      `ValueError`). Normalize stored values to `float`.
    - `volume >= 0.0` (else `ValueError`).
    - `low <= min(open, close)` and `high >= max(open, close)` and
      `low <= high` (else `ValueError`). Doji candles (`O == H == L == C`,
      `volume == 0.0`) are valid.
    - All operations must run in O(1) time and O(1) space.

Example:
    >>> c = Candle(1700000000, 100.0, 105.0, 98.0, 103.0, 250.0)
    >>> (c.is_bullish, c.body_low, c.body_high)
    (True, 100.0, 103.0)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Candle:
    """Immutable OHLCV candlestick."""

    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self) -> None:
        """Validate OHLCV invariants and normalize numeric fields to float (O(1))."""
        raise NotImplementedError("TODO(P01): validate Candle invariants in __post_init__")

    @property
    def is_bullish(self) -> bool:
        """Return True if close >= open, else False (O(1))."""
        raise NotImplementedError("TODO(P01): implement Candle.is_bullish")

    @property
    def body_low(self) -> float:
        """Return min(open, close) (O(1))."""
        raise NotImplementedError("TODO(P01): implement Candle.body_low")

    @property
    def body_high(self) -> float:
        """Return max(open, close) (O(1))."""
        raise NotImplementedError("TODO(P01): implement Candle.body_high")
