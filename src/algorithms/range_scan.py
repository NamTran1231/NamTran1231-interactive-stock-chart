"""Linear reference implementation for candle range queries."""

from src.algorithms.range_stats import RangeStats
from src.core.candle import Candle


def scan_range(candles: list[Candle], left: int, right: int) -> RangeStats | None:
    """Summarize [left, right), returning None for a valid empty range.

    Invalid bounds raise IndexError. Scanning W selected candles takes
    O(W) time and O(1) auxiliary space. Empty queries and invalid bounds
    are handled in constant time.
    """
    count = len(candles)
    if not 0 <= left <= right <= count:
        raise IndexError(f"Invalid candle range [{left}, {right}) for {count} candles")
    if left == right:
        return None

    min_low = candles[left].low
    max_high = candles[left].high
    volume_sum = 0.0
    for index in range(left, right):
        candle = candles[index]
        min_low = min(min_low, candle.low)
        max_high = max(max_high, candle.high)
        volume_sum += candle.volume

    return RangeStats(min_low, max_high, volume_sum)
