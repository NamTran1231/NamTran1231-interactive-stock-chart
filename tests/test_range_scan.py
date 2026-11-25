"""Check the public half-open range scan against hand-calculated totals."""

import unittest

from src.algorithms.range_scan import scan_range
from src.algorithms.range_stats import RangeStats
from src.core.candle import Candle


class RangeScanTests(unittest.TestCase):
    def setUp(self) -> None:
        self.candles = [
            Candle(timestamp=1, open=100, high=105, low=98, close=103, volume=1000),
            Candle(timestamp=2, open=103, high=108, low=102, close=107, volume=1500),
            Candle(timestamp=3, open=107, high=109, low=101, close=102, volume=1200),
        ]

    def test_full_range(self) -> None:
        self.assertEqual(scan_range(self.candles, 0, 3), RangeStats(98, 109, 3700))

    def test_partial_ranges_exclude_candles_outside_bounds(self) -> None:
        self.assertEqual(scan_range(self.candles, 1, 3), RangeStats(101, 109, 2700))
        self.assertEqual(scan_range(self.candles, 0, 2), RangeStats(98, 108, 2500))

    def test_single_candle(self) -> None:
        self.assertEqual(scan_range(self.candles, 1, 2), RangeStats(102, 108, 1500))

    def test_valid_empty_ranges(self) -> None:
        for index in (0, 2, 3):
            with self.subTest(index=index):
                self.assertIsNone(scan_range(self.candles, index, index))
        self.assertIsNone(scan_range([], 0, 0))

    def test_invalid_ranges_raise_index_error(self) -> None:
        for left, right in ((-1, 2), (0, 4), (2, 1), (5, 5), (-1, -1)):
            with self.subTest(left=left, right=right):
                with self.assertRaises(IndexError):
                    scan_range(self.candles, left, right)

    def test_negative_prices_and_fractional_volumes(self) -> None:
        candles = [
            Candle(timestamp=1, open=-8, high=-4, low=-10, close=-5, volume=0.1),
            Candle(timestamp=2, open=-6, high=-3, low=-7, close=-4, volume=0.2),
        ]
        stats = scan_range(candles, 0, 2)
        if stats is None:
            self.fail("A nonempty range must return statistics")
        self.assertEqual(stats.min_low, -10)
        self.assertEqual(stats.max_high, -3)
        self.assertAlmostEqual(stats.volume_sum, 0.3)

    def test_input_order_and_contents_are_preserved(self) -> None:
        original = self.candles.copy()
        scan_range(self.candles, 0, 3)
        self.assertEqual(self.candles, original)


if __name__ == "__main__":
    unittest.main()
