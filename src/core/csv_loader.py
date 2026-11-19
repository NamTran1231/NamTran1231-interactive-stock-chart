"""[P02] CSV Loader — Strict OHLCV Parser & File Reader (Easy).

Run tests:
    pytest -m p02

Problem:
    Parse CSV rows and files into validated, strictly time-ordered `Candle` lists.

Constraints:
    - Required header columns: `REQUIRED_COLUMNS` (`timestamp`, `open`, `high`,
      `low`, `close`, `volume`). Leading/trailing whitespace around headers or
      values must be stripped safely.
    - `parse_candle_row(row, line_num)`:
      - Raises `ValueError` mentioning `line_num` if any column is missing/empty,
        `timestamp` is not a valid base-10 integer (e.g. reject `"1700.5"`),
        OHLCV values are not valid floats, or `Candle` invariants fail.
    - `load_candles(path)`:
      - Raises `FileNotFoundError` if `path` does not exist.
      - Returns `[]` for an empty (0-byte) or header-only file.
      - Raises `ValueError` if required columns are missing from the header,
        if any row is malformed, or if timestamps are not strictly increasing
        (`candle.timestamp <= prev_timestamp`) — including `line_num` in errors.
      - Skips completely blank lines.
    - Complexity: O(1) per row, O(N) time and space for N rows.

Example:
    >>> row = {"timestamp": "1700000000", "open": "100", "high": "105",
    ...        "low": "98", "close": "102", "volume": "50"}
    >>> parse_candle_row(row, line_num=2).close
    102.0
"""

from __future__ import annotations

from pathlib import Path

from src.core.candle import Candle

REQUIRED_COLUMNS: tuple[str, ...] = (
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
)


def parse_candle_row(row: dict[str, str], line_num: int) -> Candle:
    """Parse one CSV dict row into a validated `Candle`, tagging errors with `line_num`."""
    raise NotImplementedError("TODO(P02): implement parse_candle_row")


def load_candles(path: str | Path) -> list[Candle]:
    """Load strictly increasing OHLCV `Candle` records from a CSV file (O(N))."""
    raise NotImplementedError("TODO(P02): implement load_candles")
