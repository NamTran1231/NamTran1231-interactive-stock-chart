"""Đọc CSV chuẩn của dự án thành danh sách Candle, không phụ thuộc GUI."""

import csv
import math

from src.core.candle import Candle


FIELDS = ["timestamp", "open", "high", "low", "close", "volume"]


def load_candles(path: str) -> list[Candle]:
    """Đọc toàn bộ file; lỗi dữ liệu gây ValueError kèm số dòng."""
    candles = []
    with open(path, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, strict=True)
        try:
            if reader.fieldnames is None:
                return []
            if reader.fieldnames != FIELDS:
                raise ValueError("CSV row 1: expected header " + ",".join(FIELDS))

            for row in reader:
                line = reader.line_num
                if None in row or any(row[field] is None for field in FIELDS):
                    raise ValueError(f"CSV row {line}: expected six fields")

                try:
                    timestamp = int(row["timestamp"])
                except ValueError as error:
                    raise ValueError(
                        f"CSV row {line}: timestamp must be integer Unix seconds"
                    ) from error

                values = {}
                for field in FIELDS[1:]:
                    try:
                        value = float(row[field])
                    except ValueError as error:
                        raise ValueError(
                            f"CSV row {line}: {field} must be a number"
                        ) from error
                    if not math.isfinite(value):
                        raise ValueError(f"CSV row {line}: {field} must be finite")
                    values[field] = value

                candle = Candle(timestamp=timestamp, **values)
                if candle.volume < 0:
                    raise ValueError(f"CSV row {line}: volume must be nonnegative")
                if not (
                    candle.low <= min(candle.open, candle.close)
                    <= max(candle.open, candle.close) <= candle.high
                ):
                    raise ValueError(f"CSV row {line}: invalid OHLC bounds")
                if candles and timestamp <= candles[-1].timestamp:
                    raise ValueError(
                        f"CSV row {line}: timestamp must be newer than previous row"
                    )
                candles.append(candle)
        except csv.Error as error:
            raise ValueError(f"CSV row {reader.line_num}: {error}") from error

    return candles
