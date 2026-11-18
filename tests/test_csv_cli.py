"""Kiểm tra loader và luồng CLI; dùng được với unittest hoặc pytest."""

import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from src.core.csv_loader import load_candles
from src.main_cli import print_candle_table


ROOT = Path(__file__).resolve().parents[1]
HEADER = "timestamp,open,high,low,close,volume\n"
ROW = "1704067200,100,105,98,103,1000\n"


class CsvCliTests(unittest.TestCase):
    def load_text(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            path.write_text(text, encoding="utf-8")
            return load_candles(str(path))

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "src.main_cli", *args],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )

    def test_shared_fixture(self):
        candles = load_candles(str(ROOT / "tests/fixtures/candles_valid.csv"))
        self.assertEqual(len(candles), 12)
        self.assertEqual(candles[0].timestamp, 1704067200)
        self.assertEqual(candles[-1].timestamp, 1704067860)
        self.assertEqual(min(c.low for c in candles), 98)
        self.assertEqual(max(c.high for c in candles), 113)
        self.assertEqual(sum(c.volume for c in candles), 13600)

    def test_empty_and_single_row(self):
        self.assertEqual(self.load_text(""), [])
        self.assertEqual(self.load_text(HEADER), [])
        self.assertEqual(self.load_text(HEADER + ROW)[0].close, 103)

    def test_invalid_rows_have_line_numbers(self):
        invalid = [
            "x,100,105,98,103,1000\n",
            "1,100,nan,98,103,1000\n",
            "1,100,105,98,103,-1\n",
            "1,100,101,98,103,1000\n",
            "1,100,105,98,103\n",
            "1,100,105,98,103,1000,extra\n",
            "1,100,105,98,103,abc\n",
        ]
        for row in invalid:
            with self.subTest(row=row):
                with self.assertRaisesRegex(ValueError, "CSV row 2"):
                    self.load_text(HEADER + row)
        with self.assertRaisesRegex(ValueError, "CSV row 1"):
            self.load_text("Date,Close\n")

    def test_timestamp_order(self):
        for timestamp in [1704067200, 1704067199]:
            with self.subTest(timestamp=timestamp):
                with self.assertRaisesRegex(ValueError, "CSV row 3"):
                    self.load_text(HEADER + ROW + f"{timestamp},100,105,98,103,1\n")

    def test_flat_negative_prices_and_zero_volume(self):
        candle = self.load_text(HEADER + "1,-5,-5,-5,-5,0\n")[0]
        self.assertEqual(candle.close, -5)
        self.assertEqual(candle.volume, 0)

    def test_table_empty(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            print_candle_table([])
        self.assertEqual(output.getvalue().strip(), "Không có dữ liệu nến.")

    def test_cli_demo_and_csv(self):
        for args, count in [((), 3), (("tests/fixtures/candles_valid.csv",), 12)]:
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"Số nến: {count}", result.stdout)
                self.assertIn("Timestamp", result.stdout)

    def test_cli_missing_and_invalid_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            for contents in [None, HEADER + "bad\n"]:
                if contents is not None:
                    path.write_text(contents, encoding="utf-8")
                result = self.run_cli(str(path))
                self.assertEqual(result.returncode, 1)
                self.assertIn("Lỗi:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
