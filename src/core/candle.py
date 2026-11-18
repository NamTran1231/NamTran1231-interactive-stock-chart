from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self) -> None:
        """Validate every candle, including instances created outside the CSV loader."""
        if type(self.timestamp) is not int:
            raise ValueError("timestamp must be integer Unix seconds")

        for field in ("open", "high", "low", "close", "volume"):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"{field} must be a finite number")
            try:
                finite = math.isfinite(value)
            except OverflowError:
                finite = False
            if not finite:
                raise ValueError(f"{field} must be finite")

        if self.volume < 0:
            raise ValueError("volume must be nonnegative")
        if not (
            self.low <= min(self.open, self.close)
            <= max(self.open, self.close) <= self.high
        ):
            raise ValueError("invalid OHLC bounds")


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
    print("Close price:", candle.close)
