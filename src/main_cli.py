"""Show three demo candles by default, or load candles from a CSV path."""

import argparse
import math
import sys

from src.core.candle import Candle
from src.core.csv_loader import load_candles


def print_candle_table(candles: list[Candle], limit: int = 10) -> None:
    """Print at most limit rows; zero shows all rows without limiting statistics."""
    if limit < 0:
        raise ValueError("limit must be nonnegative")
    if not candles:
        print("No candle data.")
        return

    print(
        f"{'Timestamp':>12} {'Open':>10} {'High':>10} "
        f"{'Low':>10} {'Close':>10} {'Volume':>12}"
    )
    visible_count = min(limit, len(candles)) if limit else len(candles)
    for index in range(visible_count):
        candle = candles[index]
        print(
            f"{candle.timestamp:>12} {candle.open:>10.2f} "
            f"{candle.high:>10.2f} {candle.low:>10.2f} "
            f"{candle.close:>10.2f} {candle.volume:>12.2f}"
        )
    print(f"\nCandle count: {len(candles)}")
    if visible_count < len(candles):
        print(f"Showing {visible_count}/{len(candles)} candles; use --limit 0 to show all.")


def print_candle_summary(candles: list[Candle]) -> None:
    """Summarize all candles with scans; M1 does not require a segment tree."""
    if not candles:
        return
    print(f"First timestamp (UTC Unix seconds): {candles[0].timestamp}")
    print(f"Last timestamp (UTC Unix seconds): {candles[-1].timestamp}")
    print(f"Min low: {min(candle.low for candle in candles):.2f}")
    print(f"Max high: {max(candle.high for candle in candles):.2f}")
    print(f"Total volume: {math.fsum(candle.volume for candle in candles):.2f}")


def nonnegative_limit(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("limit must be a nonnegative integer") from error
    if number < 0:
        raise argparse.ArgumentTypeError("limit must be a nonnegative integer")
    return number


def main() -> int:
    parser = argparse.ArgumentParser(description="Display demo candles or an OHLCV CSV.")
    parser.add_argument("csv_path", nargs="?", help="Path to a CSV in the project's standard format")
    parser.add_argument(
        "--limit", type=nonnegative_limit, default=10,
        help="Preview rows (default: 10; 0 shows all). Statistics always use the full CSV.",
    )
    args = parser.parse_args()

    if args.csv_path is None:
        candles = [
            Candle(1704067200, 100.0, 105.0, 98.0, 103.0, 1000.0),
            Candle(1704067260, 103.0, 108.0, 102.0, 107.0, 1500.0),
            Candle(1704067320, 107.0, 109.0, 101.0, 102.0, 1200.0),
        ]
    else:
        try:
            candles = load_candles(args.csv_path)
        except (OSError, UnicodeError, ValueError) as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

    print_candle_table(candles, limit=args.limit)
    print_candle_summary(candles)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
