"""Demo terminal: chạy không đối số để xem ba nến, hoặc truyền đường dẫn CSV."""

import argparse
import math
import sys

from src.core.candle import Candle
from src.core.csv_loader import load_candles


def print_candle_table(candles: list[Candle], limit: int = 10) -> None:
    """In tối đa limit dòng; limit=0 in toàn bộ, không cắt dữ liệu thống kê."""
    if limit < 0:
        raise ValueError("limit must be nonnegative")
    if not candles:
        print("Không có dữ liệu nến.")
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
    print(f"\nSố nến: {len(candles)}")
    if visible_count < len(candles):
        print(f"Hiển thị {visible_count}/{len(candles)} nến; dùng --limit 0 để xem hết.")


def print_candle_summary(candles: list[Candle]) -> None:
    """Thống kê toàn bộ dữ liệu bằng scan; chưa cần Segment Tree ở M1."""
    if not candles:
        return
    print(f"Timestamp đầu (UTC Unix seconds): {candles[0].timestamp}")
    print(f"Timestamp cuối (UTC Unix seconds): {candles[-1].timestamp}")
    print(f"Min low: {min(candle.low for candle in candles):.2f}")
    print(f"Max high: {max(candle.high for candle in candles):.2f}")
    print(f"Tổng volume: {math.fsum(candle.volume for candle in candles):.2f}")


def nonnegative_limit(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("limit phải là số nguyên không âm") from error
    if number < 0:
        raise argparse.ArgumentTypeError("limit phải là số nguyên không âm")
    return number


def main() -> int:
    parser = argparse.ArgumentParser(description="In bảng nến mẫu hoặc CSV OHLCV.")
    parser.add_argument("csv_path", nargs="?", help="Đường dẫn CSV chuẩn của dự án")
    parser.add_argument(
        "--limit", type=nonnegative_limit, default=10,
        help="Số dòng mẫu hiển thị (mặc định 10; 0 để in hết). Thống kê luôn dùng toàn bộ CSV.",
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
            print(f"Lỗi: {error}", file=sys.stderr)
            return 1

    print_candle_table(candles, limit=args.limit)
    print_candle_summary(candles)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
