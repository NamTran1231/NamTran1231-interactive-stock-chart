"""Check the loader and CLI workflows with unittest or pytest."""

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
        self.assertEqual(output.getvalue().strip(), "No candle data.")

    def test_cli_demo_and_csv(self):
        for args, count in [((), 3), (("tests/fixtures/candles_valid.csv",), 12)]:
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"Candle count: {count}", result.stdout)
                self.assertIn("Timestamp", result.stdout)

    def test_cli_missing_and_invalid_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            for contents in [None, HEADER + "bad\n"]:
                if contents is not None:
                    path.write_text(contents, encoding="utf-8")
                result = self.run_cli(str(path))
                self.assertEqual(result.returncode, 1)
                self.assertIn("Error:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_model_errors_keep_csv_line_and_reason(self):
        for row, reason in [
            ("1,100,105,98,103,-1\n", "volume"),
            ("1,100,inf,98,103,1\n", "high"),
            ("1,100,99,98,103,1\n", "OHLC"),
        ]:
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(ValueError, f"CSV row 2:.*{reason}"):
                    self.load_text(HEADER + row)

    def test_cli_summary_uses_entire_dataset_with_limited_preview(self):
        result = self.run_cli("tests/fixtures/candles_valid.csv", "--limit", "2")
        self.assertEqual(result.returncode, 0, result.stderr)
        for expected in ["Candle count: 12", "Showing 2/12", "Min low: 98.00",
                         "Max high: 113.00", "Total volume: 13600.00",
                         "First timestamp (UTC Unix seconds): 1704067200",
                         "Last timestamp (UTC Unix seconds): 1704067860"]:
            self.assertIn(expected, result.stdout)
        self.assertEqual(len([line for line in result.stdout.splitlines()
                              if line.strip().startswith("170406")]), 2)

    def test_cli_all_rows_and_invalid_limits(self):
        result = self.run_cli("tests/fixtures/candles_valid.csv", "--limit", "0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len([line for line in result.stdout.splitlines()
                              if line.strip().startswith("170406")]), 12)
        for value in ["-1", "bad", "1.5"]:
            with self.subTest(value=value):
                result = self.run_cli("--limit", value)
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("Traceback", result.stderr)

    def test_cli_empty_and_single_row_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            for text in ["", HEADER]:
                path.write_text(text, encoding="utf-8")
                result = self.run_cli(str(path))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("No candle data.", result.stdout)
                self.assertNotIn("Min low:", result.stdout)
            path.write_text(HEADER + ROW, encoding="utf-8")
            result = self.run_cli(str(path))
            self.assertEqual(result.returncode, 0, result.stderr)
            for expected in ["Candle count: 1", "Min low: 98.00", "Max high: 105.00",
                             "Total volume: 1000.00"]:
                self.assertIn(expected, result.stdout)

    def test_cli_import_has_no_demo_output(self):
        result = subprocess.run(
            [sys.executable, "-c", "import src.core.candle; import src.main_cli"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_cli_rejects_broken_quotes_and_invalid_utf8(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.csv"
            for content in [(HEADER + '"unterminated').encode(), b"\xff\xfe"]:
                path.write_bytes(content)
                result = self.run_cli(str(path))
                self.assertEqual(result.returncode, 1)
                self.assertIn("Error:", result.stderr)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
