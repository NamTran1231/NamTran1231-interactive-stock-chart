"""Check the Candle contract for direct construction outside the loader."""

from dataclasses import FrozenInstanceError
import unittest

from src.core.candle import Candle


class CandleTests(unittest.TestCase):
    def make_candle(self, **changes):
        values = dict(timestamp=1704067200, open=100, high=105, low=98,
                      close=103, volume=1000)
        values.update(changes)
        return Candle(**values)

    def test_valid_and_immutable(self):
        candle = self.make_candle()
        self.assertEqual(candle.close, 103)
        with self.assertRaises(FrozenInstanceError):
            candle.close = 104

    def test_timestamp_requires_integer_not_bool(self):
        for value in [True, False, 1.5, "1704067200", None]:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "timestamp"):
                    self.make_candle(timestamp=value)

    def test_every_numeric_field_rejects_nonfinite_and_nonnumeric(self):
        for field in ["open", "high", "low", "close", "volume"]:
            for value in [float("nan"), float("inf"), -float("inf"),
                          "100", None, True, 10 ** 400]:
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(ValueError, field):
                        self.make_candle(**{field: value})

    def test_ohlc_and_volume_rules(self):
        for changes in [dict(volume=-1), dict(low=106), dict(high=99),
                        dict(open=106), dict(close=97)]:
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    self.make_candle(**changes)

    def test_flat_negative_prices_and_zero_volume_are_allowed(self):
        candle = self.make_candle(timestamp=-60, open=-5, high=-5,
                                  low=-5, close=-5, volume=0)
        self.assertEqual(candle.volume, 0)
        self.assertEqual(candle.close, -5)


if __name__ == "__main__":
    unittest.main()
