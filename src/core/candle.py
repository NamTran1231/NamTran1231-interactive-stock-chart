from dataclasses import dataclass


@dataclass(frozen=True)
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float


if __name__ == "__main__":
    candle = Candle(
        timestamp=1704067200,
        open=100.0,
        high=105.0,
        low=98.0,
        close=103.0,
        volume=1000.0,
    )
    print(candle)
    print("Giá đóng cửa:", candle.close)