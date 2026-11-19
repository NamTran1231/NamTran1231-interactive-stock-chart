"""Algorithmic modules for range aggregation, time-series decimation, and spatial indexing."""

from src.algorithms.lttb_decimator import LTTBDecimator, aggregate_ohlcv_buckets
from src.algorithms.quad_tree import Bounds, QuadTree, SpatialPoint
from src.algorithms.segment_tree import RangeStats, SegmentTree, scan_range

__all__ = [
    "Bounds",
    "LTTBDecimator",
    "QuadTree",
    "RangeStats",
    "SegmentTree",
    "SpatialPoint",
    "aggregate_ohlcv_buckets",
    "scan_range",
]
