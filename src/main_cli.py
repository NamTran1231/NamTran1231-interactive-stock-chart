"""Demo terminal: chạy không đối số để xem ba nến, hoặc truyền đường dẫn CSV."""

import argparse
import sys

from src.core.candle import Candle
from src.core.csv_loader import load_candles


def print_candle_table(candles: list[Candle]) -> None:
    if not candles:
        print("Không có dữ liệu nến.")
        return

    print(
        f"{'Timestamp':>12} {'Open':>10} {'High':>10} "
        f"{'Low':>10} {'Close':>10} {'Volume':>12}"
    )
    for candle in candles:
        print(
            f"{candle.timestamp:>12} {candle.open:>10.2f} "
            f"{candle.high:>10.2f} {candle.low:>10.2f} "
            f"{candle.close:>10.2f} {candle.volume:>12.2f}"
        )
    print(f"\nSố nến: {len(candles)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="In bảng nến mẫu hoặc CSV OHLCV.")
    parser.add_argument("csv_path", nargs="?", help="Đường dẫn CSV chuẩn của dự án")
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
            print(f"Lỗi: {error}", file=sys.stderr)
            return 1

    print_candle_table(candles)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
