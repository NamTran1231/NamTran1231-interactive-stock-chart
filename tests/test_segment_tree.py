"""Compare static segment-tree queries with the linear range scan."""

from pathlib import Path
import random
import unittest

from src.algorithms.range_scan import scan_range
from src.algorithms.range_stats import RangeStats
from src.algorithms.segment_tree import SegmentTree
from src.core.candle import Candle
from src.core.csv_loader import load_candles


class SegmentTreeTests(unittest.TestCase):
    def test_every_range_with_negative_prices_and_fractional_volume(self) -> None:
        candles = [
            Candle(timestamp=1, open=-6, high=-4, low=-8, close=-5, volume=0.1),
            Candle(timestamp=2, open=-3, high=-2, low=-7, close=-6, volume=0.2),
            Candle(timestamp=3, open=-9, high=-8, low=-10, close=-9, volume=0.3),
        ]
        tree = SegmentTree(candles)
        for left in range(len(candles) + 1):
            for right in range(left, len(candles) + 1):
                with self.subTest(left=left, right=right):
                    self.assert_stats_match(tree.query(left, right), scan_range(candles, left, right))

    def test_seeded_ranges_from_shared_csv(self) -> None:
        path = Path(__file__).parent / "fixtures" / "candles_m2_100.csv"
        candles = load_candles(path)
        tree = SegmentTree(candles)
        self.assert_stats_match(tree.query(0, len(candles)), scan_range(candles, 0, len(candles)))
        rng = random.Random(2026)
        for _ in range(200):
            left = rng.randrange(len(candles) + 1)
            right = rng.randrange(left, len(candles) + 1)
            with self.subTest(left=left, right=right):
                self.assert_stats_match(tree.query(left, right), scan_range(candles, left, right))

    def test_empty_and_single_candle_trees(self) -> None:
        empty = SegmentTree([])
        self.assertIsNone(empty.query(0, 0))
        with self.assertRaises(IndexError):
            empty.query(0, 1)

        candle = Candle(timestamp=1, open=5, high=7, low=4, close=6, volume=1.5)
        single = SegmentTree([candle])
        self.assertEqual(single.query(0, 1), RangeStats(4, 7, 1.5))
        self.assertIsNone(single.query(1, 1))

    def test_invalid_ranges_raise_index_error(self) -> None:
        candle = Candle(timestamp=1, open=5, high=7, low=4, close=6, volume=1.5)
        tree = SegmentTree([candle])
        for left, right in ((-1, 0), (0, 2), (1, 0), (2, 2)):
            with self.subTest(left=left, right=right), self.assertRaises(IndexError):
                tree.query(left, right)

    def assert_stats_match(self, actual: RangeStats | None, expected: RangeStats | None) -> None:
        if expected is None:
            self.assertIsNone(actual)
            return
        if actual is None:
            self.fail("A nonempty range must return statistics")
        self.assertEqual(actual.min_low, expected.min_low)
        self.assertEqual(actual.max_high, expected.max_high)
        self.assertAlmostEqual(actual.volume_sum, expected.volume_sum)
