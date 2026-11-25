"""Shared result for candle range queries."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RangeStats:
    min_low: float
    max_high: float
    volume_sum: float
