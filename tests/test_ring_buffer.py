"""Verify fixed-capacity candle retention and chronological snapshots."""

import unittest
from weakref import ref

from src.core.candle import Candle
from src.core.ring_buffer import RingBuffer


def candle_at(timestamp: int) -> Candle:
    return Candle(timestamp, 100, 100, 100, 100, 0)


class RingBufferTests(unittest.TestCase):
    def test_capacity_must_be_a_positive_integer(self) -> None:
        for capacity in (0, -1, True, 3.0, "3", None):
            with self.subTest(capacity=capacity), self.assertRaises(ValueError):
                RingBuffer(capacity)

    def test_multiple_wraparounds_match_recent_history(self) -> None:
        for capacity in (1, 3, 7):
            with self.subTest(capacity=capacity):
                buffer = RingBuffer(capacity)
                history = []
                self.assertEqual(buffer.get_all(), [])
                self.assertFalse(buffer.is_full())
                for timestamp in range(1, 29):
                    candle = candle_at(timestamp)
                    history.append(candle)
                    buffer.push(candle)
                    self.assertEqual(buffer.get_all(), history[-capacity:])
                    self.assertEqual(buffer.is_full(), len(history) >= capacity)

    def test_snapshot_is_independent_and_clear_allows_reuse(self) -> None:
        buffer = RingBuffer(3)
        for timestamp in range(1, 9):
            buffer.push(candle_at(timestamp))
        snapshot = buffer.get_all()
        self.assertEqual([candle.timestamp for candle in snapshot], [6, 7, 8])
        snapshot.clear()
        self.assertEqual([candle.timestamp for candle in buffer.get_all()], [6, 7, 8])
        buffer.clear()
        self.assertFalse(buffer.is_full())
        self.assertEqual(buffer.get_all(), [])
        buffer.push(candle_at(9))
        self.assertEqual(buffer.get_all(), [candle_at(9)])

    def test_clear_releases_retained_candles(self) -> None:
        buffer = RingBuffer(2)
        candle = candle_at(1)
        reference = ref(candle)
        buffer.push(candle)
        del candle
        self.assertIsNotNone(reference())
        buffer.clear()
        self.assertIsNone(reference())
