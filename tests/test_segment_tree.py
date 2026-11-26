"""Compare segment-tree queries with the linear range scan."""

from dataclasses import replace
from pathlib import Path
import random
import unittest

from src.algorithms.range_scan import scan_range
from src.algorithms.range_stats import RangeStats
from src.algorithms.segment_tree import SegmentTree
from src.core.candle import Candle
from src.core.csv_loader import load_candles


class SegmentTreeTests(unittest.TestCase):
    def test_large_integer_volumes_can_mix_with_floats(self) -> None:
        candle = Candle(1, 5, 7, 4, 6, 10**308)
        candles = [candle, replace(candle, timestamp=2), replace(candle, timestamp=3, volume=0.5)]
        self.assertEqual(SegmentTree(candles).query(0, 3), scan_range(candles, 0, 3))

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

    def test_point_updates_match_the_scan(self) -> None:
        path = Path(__file__).parent / "fixtures" / "candles_m2_100.csv"
        original = load_candles(path)[:9]
        snapshot = original.copy()
        expected = original.copy()
        tree = SegmentTree(original)
        rng = random.Random(2026)
        for index in (0, 8, 4, 4, 0):
            current = expected[index]
            updated = replace(
                current, low=current.low - 10, high=current.high + 10,
                volume=rng.randrange(100) / 10,
            )
            tree.update(index, updated)
            expected[index] = updated
            for left in range(len(expected) + 1):
                for right in range(left, len(expected) + 1):
                    with self.subTest(index=index, left=left, right=right):
                        self.assert_stats_match(tree.query(left, right), scan_range(expected, left, right))
        self.assertEqual(original, snapshot)

    def test_update_removes_old_extremes(self) -> None:
        widest = Candle(timestamp=1, open=5, high=20, low=1, close=6, volume=4)
        neighbor = Candle(timestamp=2, open=5, high=8, low=3, close=6, volume=2)
        tree = SegmentTree([widest, neighbor])

        tree.update(0, replace(widest, high=7, low=4, volume=1))

        self.assertEqual(tree.query(0, 2), RangeStats(3, 8, 3))
        self.assertEqual(tree.query(1, 2), RangeStats(3, 8, 2))

    def test_single_candle_update(self) -> None:
        candle = Candle(timestamp=1, open=5, high=7, low=4, close=6, volume=1.5)
        tree = SegmentTree([candle])
        tree.update(0, replace(candle, volume=0))
        self.assertEqual(tree.query(0, 1), RangeStats(4, 7, 0))

    def test_invalid_updates_leave_the_tree_unchanged(self) -> None:
        candle = Candle(timestamp=1, open=5, high=7, low=4, close=6, volume=1.5)
        candles = [candle, replace(candle, timestamp=2), replace(candle, timestamp=3)]
        tree = SegmentTree(candles)
        replacement = replace(candle, low=0, high=15, volume=50)
        for index, candidate, error in (
            (-1, replacement, IndexError),
            (3, replacement, IndexError),
            (0, replace(replacement, timestamp=2), ValueError),
            (0, replace(replacement, timestamp=4), ValueError),
        ):
            with self.subTest(index=index, timestamp=candidate.timestamp):
                with self.assertRaises(error):
                    tree.update(index, candidate)
                for leaf in range(len(candles)):
                    self.assertEqual(tree.query(leaf, leaf + 1), RangeStats(4, 7, 1.5))
                self.assertEqual(tree.query(0, 3), RangeStats(4, 7, 4.5))
        with self.assertRaises(IndexError):
            SegmentTree([]).update(0, candle)

    def test_append_from_empty_through_repeated_growth(self) -> None:
        tree = SegmentTree([])
        candles: list[Candle] = []
        for index in range(17):
            # The first timestamp can be negative; only later timestamps must increase.
            candle = Candle(index - 20, -8, -4 + index, -10 - index, -5, index / 10)
            tree.append(candle)
            candles.append(candle)
            self.assert_all_ranges_match(tree, candles)

    def test_append_after_update_preserves_replaced_stats_through_growth(self) -> None:
        path = Path(__file__).parent / "fixtures" / "candles_m2_100.csv"
        source = load_candles(path)[:10]
        candles = source[:3]
        tree = SegmentTree(candles)
        for candle in source[3:]:
            # Alternate which leaf is replaced before appending, including the latest.
            index = 0 if len(candles) % 2 else len(candles) - 1
            updated = replace(candles[index], low=80, high=130, volume=2.25)
            tree.update(index, updated)
            candles[index] = updated
            tree.append(candle)
            candles.append(candle)
            self.assert_all_ranges_match(tree, candles)

    def test_append_rejects_duplicate_and_older_timestamps_without_mutation(self) -> None:
        first = Candle(timestamp=10, open=5, high=7, low=4, close=6, volume=1.5)
        second = replace(first, timestamp=20, high=9)
        candles = [first, second]
        tree = SegmentTree(candles)
        for timestamp in (20, 10, 15, -1):
            with self.subTest(timestamp=timestamp):
                with self.assertRaises(ValueError):
                    tree.append(replace(second, timestamp=timestamp, low=0, volume=50))
                self.assert_all_ranges_match(tree, candles)
                with self.assertRaises(IndexError):
                    tree.query(2, 3)

        third = replace(second, timestamp=30)
        tree.append(third)
        candles.append(third)
        self.assert_all_ranges_match(tree, candles)
        for timestamp in (30, 25):
            with self.subTest(timestamp=timestamp):
                with self.assertRaises(ValueError):
                    tree.append(replace(third, timestamp=timestamp, volume=50))
                self.assert_all_ranges_match(tree, candles)
                with self.assertRaises(IndexError):
                    tree.query(3, 4)

    def assert_all_ranges_match(self, tree: SegmentTree, candles: list[Candle]) -> None:
        for left in range(len(candles) + 1):
            for right in range(left, len(candles) + 1):
                with self.subTest(count=len(candles), left=left, right=right):
                    self.assert_stats_match(tree.query(left, right), scan_range(candles, left, right))

    def assert_stats_match(self, actual: RangeStats | None, expected: RangeStats | None) -> None:
        if expected is None:
            self.assertIsNone(actual)
            return
        if actual is None:
            self.fail("A nonempty range must return statistics")
        self.assertEqual(actual.min_low, expected.min_low)
        self.assertEqual(actual.max_high, expected.max_high)
        self.assertAlmostEqual(actual.volume_sum, expected.volume_sum)
