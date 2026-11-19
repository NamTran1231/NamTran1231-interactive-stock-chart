# Đặc tả Giao diện & Khế ước Kỹ thuật (API Contracts — 15 Components)

Tài liệu này là **Nguồn chân lý duy nhất (Single Source of Truth)** cho toàn bộ 14 thành phần lõi và điểm vào CLI/Benchmark/GUI (`main_cli`) trong `DAG_MANIFEST.json` của dự án **Interactive TradingView Stock Chart Engine (DSA Python)**. Mọi thành viên phải tuân thủ chính xác tuyệt đối tên module, tên lớp/hàm, chữ ký tham số, giá trị mặc định, kiểu trả về, bất biến (invariants) và hành vi ngoại lệ (edge cases). Tham khảo thêm các sơ đồ kiến trúc trực quan tại [UML_ARCHITECTURE.md](UML_ARCHITECTURE.md).

---

## Tổng quan Danh mục Components

| # | Component | File Path | Chủ sở hữu |
|---|---|---|---|
| 1 | `Candle` | `src/core/candle.py` | Thành viên 1 |
| 2 | `csv_loader` | `src/core/csv_loader.py` | Thành viên 1 |
| 3 | `RingBuffer` | `src/core/ring_buffer.py` | Thành viên 1 |
| 4 | `data_simulator` | `src/core/data_simulator.py` | Thành viên 1 |
| 5 | `CircularDeque` | `src/algorithms/monotonic_deque.py` | Thành viên 2 |
| 6 | `MonotonicDeque` | `src/algorithms/monotonic_deque.py` | Thành viên 2 |
| 7 | `SlidingWindowIndicators` | `src/algorithms/monotonic_deque.py` | Thành viên 2 |
| 8 | `CoordinateTransformer` & `ViewportState` | `src/core/coordinate_math.py` | Thành viên 2 |
| 9 | `RangeStats`, `SegmentTree` & `scan_range` | `src/algorithms/segment_tree.py` | Thành viên 3 |
| 10 | `LTTBDecimator` & `aggregate_ohlcv_buckets` | `src/algorithms/lttb_decimator.py` | Thành viên 3 |
| 11 | `QuadTree`, `Bounds`, `SpatialPoint` | `src/algorithms/quad_tree.py` | Thành viên 3 |
| 12 | `EventBus` | `src/patterns/observer.py` | Thành viên 4 |
| 13 | `Command`, `ViewportChangeCommand`, `CommandHistory` | `src/patterns/command_history.py` | Thành viên 4 |
| 14 | `VisibleFrame`, `ChartCanvasWidget` & `MainWindow` | `src/ui/chart_canvas.py`, `src/ui/main_window.py` | Thành viên 4 |
| 15 | `main_cli` (`build_parser`, `main`, `run_cli`, `run_benchmark`, `run_gui`) | `src/main.py` | Thành viên 4 |

---

## 1. `Candle` (`src/core/candle.py`)

### Signatures
```python
@dataclass(frozen=True)
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self) -> None: ...
```

### Invariants & Validation
- Bất biến số học thực: mọi trường số (`timestamp`, `open`, `high`, `low`, `close`, `volume`) đều phải hữu hạn (`math.isfinite` là `True`, không chấp nhận `NaN`, `+inf`, `-inf`, hoặc kiểu `bool`).
- `volume >= 0.0` (khối lượng không âm).
- `low <= min(open, close)` (giá thấp nhất không được cao hơn giá mở hoặc giá đóng).
- `high >= max(open, close)` (giá cao nhất không được thấp hơn giá mở hoặc giá đóng).
- **Bất biến bất biến (Immutability):** Vì là `@dataclass(frozen=True)`, mọi thuộc tính không thể bị sửa đổi sau khi khởi tạo.

### Edge Cases & Exceptions
- `timestamp` sai kiểu (ví dụ `bool`, `float`, `str`, `None`) hoặc giá trị OHLCV không phải số (`bool`, `str`) $\to$ raise `TypeError`.
- Vi phạm bất kỳ invariant giá trị nào (`timestamp < 0`, `NaN`, `±Inf`, `volume < 0`, `low > min(open, close)`, `high < max(open, close)`) $\to$ raise `ValueError` với thông điệp mô tả rõ nguyên nhân.
- Nến Doji (`open == high == low == close` và `volume == 0.0`) là **hợp lệ**.

---

## 2. `csv_loader` (`src/core/csv_loader.py`)

### Signatures
```python
def parse_candle_row(row: dict, line_num: int) -> Candle: ...
def load_candles(path: str) -> list[Candle]: ...
```

### Invariants & Validation
- `parse_candle_row(row: dict, line_num: int) -> Candle`:
  - Đọc các cột chuẩn `timestamp`, `open`, `high`, `low`, `close`, `volume`, ép kiểu sang `int`/`float` và khởi tạo `Candle`.
  - Bất kỳ cột thiếu, chuỗi không ép được sang số, hoặc vi phạm invariant của `Candle` $\to$ raise `ValueError` **có đính kèm số dòng `line_num`** trong thông điệp lỗi.
- `load_candles(path: str) -> list[Candle]`:
  - Đọc tuần tự tệp CSV theo dòng, theo dõi `prev_timestamp`.
  - Nếu `candle.timestamp <= prev_timestamp` (sai thứ tự giảm dần hoặc trùng timestamp) $\to$ raise `ValueError` **có đính kèm số dòng `line_num`**.

### Edge Cases & Exceptions
- Tệp rỗng (0 byte) hoặc chỉ có dòng tiêu đề (header-only) $\to$ trả về `[]` (danh sách rỗng, không báo lỗi).
- Tệp không tồn tại $\to$ raise `FileNotFoundError`.
- Khoảng trắng dư thừa quanh tên cột hoặc giá trị số cần được `strip()` an toàn trước khi ép kiểu.

---

## 3. `RingBuffer` (`src/core/ring_buffer.py`)

### Signatures
```python
class RingBuffer:
    def __init__(self, capacity: int) -> None: ...
    def push(self, item: Any) -> None: ...
    def get_all(self) -> list: ...
    def latest(self) -> Any | None: ...
    def __len__(self) -> int: ...
    def is_full(self) -> bool: ...
    def clear(self) -> None: ...
```

### Invariants & Complexity
- **Cấm tuyệt đối sử dụng `collections.deque`**. Phải tự cài đặt bằng mảng vòng tĩnh (`list` kích thước `capacity`) và các con trỏ chỉ số nguyên (`head` / `size`).
- `capacity > 0` (nếu `capacity <= 0` hoặc không phải số nguyên hợp lệ $\to$ raise `ValueError`).
- `push(item) -> None`: Chèn vào vị trí kế tiếp trong **$O(1)$**; khi đầy (`len == capacity`), ghi đè phần tử cũ nhất và tịnh tiến con trỏ đầu.
- `get_all() -> list`: Trả về danh sách mới gồm toàn bộ phần tử hiện tại theo thứ tự **từ cũ nhất đến mới nhất** trong **$O(K)$** ($K = \text{len}(self)$).
- `latest() -> Any | None`: Trả về phần tử mới nhất vừa `push` trong **$O(1)$**, hoặc `None` nếu rỗng.
- `__len__() -> int`, `is_full() -> bool`, `clear() -> None`: Hoạt động trong **$O(1)$** (trừ giải phóng tham chiếu ô nhớ trong `clear()` tối đa $O(\text{capacity})$).

### Edge Cases & Exceptions
- `RingBuffer(0)` hoặc `RingBuffer(-5)` $\to$ raise `ValueError`.
- `RingBuffer(1)`: Khi push 2 phần tử `A`, `B` liên tiếp, `get_all()` trả `[B]`, `latest()` trả `B`, `len(buf) == 1`, `is_full() == True`.
- Khi rỗng: `get_all() == []`, `latest() is None`, `len(buf) == 0`, `is_full() == False`.

---

## 4. `data_simulator` (`src/core/data_simulator.py`)

### Signatures
```python
def generate_synthetic_candles(
    count: int,
    seed: int = 42,
    start_ts: int = 1700000000,
    interval_sec: int = 60,
) -> list[Candle]: ...

class ReplayDataSource:
    def __init__(self, candles: Sequence[Candle]) -> None: ...
    @classmethod
    def from_csv(cls, path: str | Path) -> ReplayDataSource: ...
    @classmethod
    def from_synthetic(
        cls,
        count: int,
        seed: int = 42,
        start_ts: int = 1700000000,
        interval_sec: int = 60,
        start_price: float = 100.0,
    ) -> ReplayDataSource: ...
    def has_next(self) -> bool: ...
    def step(self) -> Candle | None: ...
    def reset(self) -> None: ...
    @property
    def progress(self) -> tuple[int, int]: ...
    @property
    def candles(self) -> list[Candle]: ...
    def replace_or_append(self, candle: Candle) -> tuple[str, int]: ...
```

### Invariants & Behavior
- `generate_synthetic_candles`: Sinh ngẫu nhiên tất định theo `seed` (`random.Random(seed)`) một chuỗi `count` nến `Candle` hợp lệ với timestamp `start_ts + i * interval_sec`.
- `ReplayDataSource`:
  - **Factory Method (`@classmethod`):** `from_csv(path)` nạp qua `load_candles(path)`; `from_synthetic(...)` sinh qua `generate_synthetic_candles(...)`.
  - `step() -> Candle | None`: Trả về nến tiếp theo và tăng con trỏ replay; trả `None` nếu đã phát hết danh sách.
  - `reset() -> None`: Đặt lại con trỏ replay về đầu (`0`).
  - `replace_or_append(candle: Candle) -> tuple[str, int]`: Nếu danh sách đang có phần tử cuối cùng trùng `timestamp` (`candle.timestamp == last.timestamp`), thay thế phần tử cuối và trả `("replaced", idx)`; nếu `candle.timestamp > last.timestamp` (hoặc nguồn đang rỗng), nối `candle` vào cuối và trả `("appended", idx)`; nếu `candle.timestamp < last.timestamp` $\to$ raise `ValueError`.

### Edge Cases & Exceptions
- `count == 0` $\to$ trả về `[]`; `count < 0` hoặc `interval_sec <= 0` $\to$ raise `ValueError`.
- `ReplayDataSource([])`: gọi `step()` trả ngay `None`.

---

## 5. `CircularDeque` (`src/algorithms/monotonic_deque.py`)

### Signatures
```python
class CircularDeque:
    def __init__(self, capacity: int = 16) -> None: ...
    def push_front(self, x: Any) -> None: ...
    def push_back(self, x: Any) -> None: ...
    def pop_front(self) -> Any: ...
    def pop_back(self) -> Any: ...
    def peek_front(self) -> Any: ...
    def peek_back(self) -> Any: ...
    def __len__(self) -> int: ...
    def is_empty(self) -> bool: ...
    def to_list(self) -> list: ...
```

### Invariants & Complexity
- **Cấm tuyệt đối sử dụng `collections.deque`**. Tự cài đặt mảng vòng hai đầu với tự động mở rộng kích thước gấp đôi (**auto-resizes 2x**) khi đầy.
- `push_front`, `push_back`: **$O(1)$ amortized** (khi đầy sẽ cấp phát mảng $2 \times \text{capacity}$ và trải lại phần tử theo thứ tự logic từ `front` tới `back`).
- `pop_front`, `pop_back`, `peek_front`, `peek_back`, `__len__`, `is_empty`: **$O(1)$**.
- `to_list()`: Trả về danh sách các phần tử từ `front` đến `back` trong **$O(N)$**.

### Edge Cases & Exceptions
- `capacity <= 0` $\to$ raise `ValueError`.
- Gọi `pop_front()`, `pop_back()`, `peek_front()`, `peek_back()` khi `is_empty()` là `True` $\to$ raise `IndexError`.
- Kiểm thử bao bọc (wrap-around): Đẩy và lấy xen kẽ nhiều lần qua ranh giới cuối mảng trước và sau khi auto-resize 2x phải bảo toàn thứ tự 100%.

---

## 6. `MonotonicDeque` (`src/algorithms/monotonic_deque.py`)

### Signatures
```python
class MonotonicDeque:
    def __init__(self, mode: str = "min") -> None: ...
    def push(self, index: int, value: float) -> None: ...
    def evict_before(self, min_valid_index: int) -> None: ...
    def extrema(self) -> tuple[int, float] | None: ...
    def clear(self) -> None: ...
```

### Invariants & Complexity
- `mode` chỉ nhận `'min'` hoặc `'max'` (khác $\to$ raise `ValueError`).
- Sử dụng `CircularDeque` làm bộ chứa nội bộ.
- `push(index, value)`:
  - Nếu `mode == 'min'`, loại bỏ ở cuối (`pop_back`) mọi phần tử có `val >= value` (hoặc `> value`) trước khi `push_back((index, value))`, giữ chuỗi giá trị tăng đơn điệu từ đầu tới cuối.
  - Nếu `mode == 'max'`, loại bỏ ở cuối mọi phần tử có `val <= value` trước khi `push_back((index, value))`, giữ chuỗi giá trị giảm đơn điệu.
  - Mỗi phần tử được đẩy vào và lấy ra tối đa 1 lần $\implies$ **$O(1)$ amortized**.
- `evict_before(min_valid_index)`: Xóa ở đầu (`pop_front`) các phần tử có `idx < min_valid_index`.
- `extrema() -> tuple[int, float] | None`: Trả về `(index, value)` ở đầu hàng đợi trong **$O(1)$**, hoặc `None` nếu rỗng.

### Edge Cases & Exceptions
- `mode` ngoài `{'min', 'max'}` $\to$ raise `ValueError`.
- `value` không hữu hạn (`not math.isfinite(value)`) $\to$ raise `ValueError`.
- Khi các phần tử có giá trị bằng nhau, phần tử mới hơn (chỉ số lớn hơn) vẫn được bảo đảm duy trì đúng cực trị hiện tại sau khi phần tử cũ bị `evict_before`.

---

## 7. `SlidingWindowIndicators` (`src/algorithms/monotonic_deque.py`)

### Signatures
```python
class SlidingWindowIndicators:
    @staticmethod
    def rolling_min_max(values: list[float], window: int) -> list[tuple[float, float]]: ...

    @staticmethod
    def sma(values: list[float], window: int) -> list[float | None]: ...

    @staticmethod
    def ema(values: list[float], window: int) -> list[float | None]: ...

    @staticmethod
    def donchian_channels(
        candles: list[Candle], window: int
    ) -> list[tuple[float, float, float]]: ...

    @staticmethod
    def bollinger_bands(
        values: list[float], window: int, num_std: float = 2.0
    ) -> list[tuple[float | None, float | None, float | None]]: ...
```

### Invariants & Complexity
- Tất cả các phương thức đều chạy trong thời gian tuyến tính **$O(N)$** ($N$ là độ dài đầu vào), không phụ thuộc kích thước `window`.
- `window < 1` $\to$ raise `ValueError` (với `bollinger_bands`, `num_std < 0` $\to$ raise `ValueError`).
- `rolling_min_max(values, window)`: Dùng 2 `MonotonicDeque` (`'min'` và `'max'`), trả về danh sách `[(min_val, max_val), ...]` tại mỗi chỉ số `i` trên cửa sổ `[max(0, i - window + 1), i]`.
- `sma(values, window)`: Trả về `None` cho `0 <= i < window - 1`; từ `i >= window - 1` trả về trung bình cộng trượt của `window` phần tử gần nhất.
- `ema(values, window)`: Khởi tạo bằng `sma` tại chỉ số `window - 1` (các chỉ số trước đó là `None`), sau đó cập nhật theo hệ số $\alpha = \frac{2}{\text{window} + 1}$: $\text{EMA}_i = \alpha \cdot x_i + (1 - \alpha) \cdot \text{EMA}_{i-1}$.
- `donchian_channels(candles, window)`: Dùng `MonotonicDeque('max')` trên `high` và `MonotonicDeque('min')` trên `low`, trả về `(upper_high, middle, lower_low)` với `middle = (upper_high + lower_low) / 2.0` tại mỗi chỉ số.
- `bollinger_bands(values, window, num_std=2.0)`: Trả về `(None, None, None)` khi `i < window - 1`; từ `i >= window - 1` trả về `(upper, middle, lower)` với `middle = SMA`, `upper = middle + num_std * std`, `lower = middle - num_std * std` (clamp phương sai âm nhỏ do sai số dấu phẩy động về `0.0`).

### Edge Cases & Exceptions
- Đầu vào rỗng `[]` $\to$ trả về `[]` (sau khi kiểm tra `window >= 1`).
- Khi `len(values) < window`, `sma`, `ema`, `bollinger_bands` trả về danh sách toàn `None` / `(None, None, None)` cùng độ dài `len(values)`.

---

## 8. `CoordinateTransformer` & `ViewportState` (`src/core/coordinate_math.py`)

### Signatures
```python
@dataclass(frozen=True) # hoặc @dataclass
class ViewportState:
    start_idx: float
    end_idx: float
    min_price: float
    max_price: float
    width_px: int
    height_px: int
    padding_left: int = 12
    padding_right: int = 72
    padding_top: int = 16
    padding_bottom: int = 28

class CoordinateTransformer:
    def __init__(self, viewport: ViewportState) -> None: ...
    @property
    def viewport(self) -> ViewportState: ...
    def index_to_x(self, index: float) -> float: ...
    def x_to_index(self, x_px: float) -> float: ...
    def price_to_y(self, price: float) -> float: ...
    def y_to_price(self, y_px: float) -> float: ...
    def world_to_screen(self, index: float, price: float) -> tuple[float, float]: ...
    def screen_to_world(self, x_px: float, y_px: float) -> tuple[float, float]: ...
    def zoom_at_pixel(
        self,
        anchor_x: float,
        zoom_factor: float,
        min_span: float = 5.0,
        max_span: float = 100000.0,
    ) -> ViewportState: ...
    def pan_by_pixels(self, dx_px: float) -> ViewportState: ...
```
*(Ghi chú: `pan_by_pixels(self, dx_px: float) -> ViewportState` chỉ nhận đúng tham số dịch ngang `dx_px`; trục giá Y được tự động co giãn theo `SegmentTree` qua `_auto_scale_y`).*

### Invariants & Mathematics
- Vùng vẽ biểu đồ (Plot Area):
  - `plot_w = max(1, state.width_px - state.padding_left - state.padding_right)`
  - `plot_h = max(1, state.height_px - state.padding_top - state.padding_bottom)`
- Biến đổi Affine trục X:
  - $x = \text{padding\_left} + \frac{\text{idx} - \text{start\_idx}}{\text{end\_idx} - \text{start\_idx}} \cdot \text{plot\_w}$
- Biến đổi Affine trục Y (tọa độ màn hình đảo chiều theo trục dọc):
  - $y = \text{padding\_top} + \frac{\text{max\_price} - \text{price}}{\text{max\_price} - \text{min\_price}} \cdot \text{plot\_h}$
- **Cursor-Anchored Zoom (`zoom_at_pixel`):** Giữ nguyên chỉ số thế giới `anchor_idx = x_to_index(pixel_x)` trước và sau zoom sao cho tỉ lệ tương đối của con trỏ trong vùng plot không đổi.
- **Khả nghịch:** `screen_to_world(*world_to_screen(idx, price))` khớp `(idx, price)` trong sai số dấu phẩy động ($< 10^{-9}$).

### Edge Cases & Exceptions
- `zoom_factor <= 0` (hoặc không hữu hạn), `min_span <= 0`, hoặc `min_span > max_span` $\to$ raise `ValueError`.
- Các đầu vào suy biến (`start_idx == end_idx`, `min_price == max_price`, `width_px <= 0`, `height_px <= 0`) **KHÔNG** được chia cho 0 (`plot_width`/`plot_height` luôn kẹp `>= 1.0`, khoảng world bằng 0 ánh xạ về tâm vùng vẽ).
- **Prototype Pattern:** `zoom_at_pixel` và `pan_by_pixels` tạo bản sao `ViewportState` mới qua `dataclasses.replace(...)` mà không sửa trạng thái gốc.

---

## 9. `RangeStats`, `SegmentTree` & `scan_range` (`src/algorithms/segment_tree.py`)

### Signatures
```python
@dataclass(frozen=True)
class RangeStats:
    min_low: float
    max_high: float
    volume_sum: float

class SegmentTree:
    def __init__(self, candles: list[Candle] | None = None) -> None: ...
    def query(self, left: int, right: int) -> RangeStats | None: ...
    def update(self, index: int, candle: Candle) -> None: ...
    def append(self, candle: Candle) -> None: ...
    def __len__(self) -> int: ...

def scan_range(candles: list[Candle], left: int, right: int) -> RangeStats | None: ...
```

### Invariants & Complexity
- **Khoảng truy vấn nửa mở `[left, right)`:** Bao gồm các phần tử có chỉ số $i$ thỏa mãn $\text{left} \le i < \text{right}$.
- `query(left, right) -> RangeStats | None`: Độ phức tạp **$O(\log N)$**, trả về `RangeStats(min(low), max(high), sum(volume))` trên `[left, right)`. Nếu khoảng giao với `[0, len)` rỗng (`left >= right` hoặc cây rỗng) $\to$ trả về `None`.
- `update(index, candle) -> None`: Cập nhật lá tại `index` và lan truyền lên nút cha trong **$O(\log N)$**. Nếu `index < 0` hoặc `index >= len(self)` $\to$ raise `IndexError`.
- `append(candle) -> None`: Tăng kích thước cây lên 1; nếu vượt quá sức chứa lũy thừa của 2 hiện tại (`capacity`), tự động cấp phát sức chứa power-of-2 mới gấp đôi và rebuild cây (**$O(\log N)$ amortized**).
- `scan_range(candles, left, right) -> RangeStats | None`: Oracle đối chiếu tuyến tính $O(N)$ dùng trong differential tests và benchmark.

### Edge Cases & Exceptions
- `SegmentTree()` khởi tạo rỗng (`len(tree) == 0`, `tree.query(0, 1) is None`), sau đó gọi `append(candle)` liên tiếp phải hoạt động đúng qua các mốc `1 -> 2 -> 4 -> 8 -> ...`.
- Kích thước mảng ban đầu không phải lũy thừa của 2 (ví dụ 0, 1, 3, 5, 7, 1000) vẫn phải cho kết quả `query` trùng khớp 100% với `scan_range`.

---

## 10. `LTTBDecimator` & `aggregate_ohlcv_buckets` (`src/algorithms/lttb_decimator.py`)

### Signatures
```python
class LTTBDecimator:
    @staticmethod
    def downsample(
        points: Sequence[tuple[float, float]],
        threshold: int,
    ) -> list[tuple[float, float]]: ...

def aggregate_ohlcv_buckets(
    candles: Sequence[Candle],
    start_idx: int,
    end_idx: int,
    max_candles: int,
) -> list[Candle]: ...
```

### Invariants & Complexity
- `LTTBDecimator.downsample(points, threshold)`:
  - Độ phức tạp thời gian **$O(N)$**, không gian đầu ra **$O(\text{threshold})$**.
  - Luôn giữ nguyên điểm đầu `points[0]` và điểm cuối `points[-1]` (khi `len(points) >= 2` và `threshold >= 2`).
  - Với mỗi bucket trung gian, chọn điểm $P_j$ tạo diện tích tam giác lớn nhất với điểm đã chọn ở bucket trước và tâm trung bình (average point) của bucket kế tiếp.
- `aggregate_ohlcv_buckets(candles, start_idx, end_idx, max_candles)`:
  - Chia đoạn `candles[start_idx:end_idx]` thành tối đa `max_candles` bucket liên tiếp.
  - Mỗi bucket gộp thành 1 `Candle` duy nhất tuân thủ bất biến OHLCV tài chính:
    - `timestamp = bucket[0].timestamp`
    - `open = bucket[0].open`
    - `high = max(c.high for c in bucket)`
    - `low = min(c.low for c in bucket)`
    - `close = bucket[-1].close`
    - `volume = sum(c.volume for c in bucket)`

### Edge Cases & Exceptions
- Quy tắc biên chính xác của `LTTBDecimator.downsample(points, threshold)` (khớp `src/algorithms/lttb_decimator.py`):
  - `threshold < 0` $\to$ raise `ValueError`.
  - `threshold == 0` hoặc `not points` $\to$ trả về `[]`.
  - `threshold == 1` (khi `points` không rỗng) $\to$ trả về `[(float(points[0][0]), float(points[0][1]))]`.
  - `len(points) <= threshold` $\to$ trả về toàn bộ `points` đã ép kiểu `float`: `[(float(x), float(y)) for x, y in points]`.
  - `threshold == 2` (khi `len(points) > 2`) $\to$ trả về `[first, last]` với `first = (float(points[0][0]), float(points[0][1]))` và `last = (float(points[-1][0]), float(points[-1][1]))`.
- Quy tắc biên của `aggregate_ohlcv_buckets(candles, start_idx, end_idx, max_candles)`:
  - `max_candles <= 0` $\to$ raise `ValueError`.
  - Đoạn `[start_idx, end_idx)` rỗng sau khi clamp về `[0, len(candles)]` hoặc `candles` rỗng $\to$ trả `[]`.

---

## 11. `QuadTree`, `Bounds`, `SpatialPoint` (`src/algorithms/quad_tree.py`)

### Signatures
```python
@dataclass(frozen=True)
class Bounds:
    x_min: float
    y_min: float
    x_max: float
    y_max: float

@dataclass(frozen=True)
class SpatialPoint:
    x: float
    y: float
    payload: Any

class QuadTree:
    def __init__(self, bounds: Bounds, capacity: int = 4) -> None: ...
    def insert(self, point: SpatialPoint) -> bool: ...
    def query_range(self, rect: Bounds) -> list[SpatialPoint]: ...
    def nearest(self, x: float, y: float, max_dist: float) -> SpatialPoint | None: ...
```

### Invariants & Behavior
- `Bounds`: Phải bảo đảm `x_min <= x_max` và `y_min <= y_max` (nếu vi phạm $\to$ raise `ValueError`).
- `QuadTree(bounds, capacity=4)`: Validate `capacity >= 1` (`ValueError`). Khi số điểm trong nút lá vượt quá `capacity` (và chưa chạm ngưỡng sâu chống tràn stack với điểm trùng tọa độ), chia nút thành 4 góc phần tư con (`NW`, `NE`, `SW`, `SE`).
- `insert(point) -> bool`: Trả về `False` nếu điểm nằm ngoài `bounds`; ngược lại chèn vào cây và trả về `True`.
- `query_range(rect) -> list[SpatialPoint]`: Cắt tỉa nhánh không giao cắt với `rect`, trả về mọi `SpatialPoint` nằm trong `rect`.
- `nearest(x, y, max_dist) -> SpatialPoint | None`: Tìm `SpatialPoint` gần `(x, y)` nhất theo khoảng cách Euclid với điều kiện `dist <= max_dist`; cắt tỉa các nhánh con có khoảng cách tối thiểu từ `(x, y)` đến bounding box lớn hơn khoảng cách tốt nhất hiện tại.

### Edge Cases & Exceptions
- Nhiều điểm có tọa độ `(x, y)` trùng hệt nhau vượt quá `capacity` $\to$ không gây đệ quy vô hạn `RecursionError` (có giới hạn `max_depth` hoặc danh sách điểm trùng tại nút).
- `max_dist < 0` $\to$ raise `ValueError`; cây rỗng $\to$ `query_range` trả `[]`, `nearest` trả `None`.

---

## 12. `EventBus` (`src/patterns/observer.py`)

### Signatures
```python
class EventBus:
    def __init__(self) -> None: ...
    def subscribe(self, event_name: str, callback: Callable[..., Any]) -> Callable[[], None]: ...
    def unsubscribe(self, event_name: str, callback: Callable[..., Any]) -> bool: ...
    def publish(self, event_name: str, *args: Any, **kwargs: Any) -> int: ...
    def clear(self, event_name: str | None = None) -> None: ...
    def listener_count(self, event_name: str | None = None) -> int: ...
```

### Invariants & Edge Cases
- `subscribe`: Validate `event_name` khác rỗng (`ValueError`) và `callable(callback)` (`TypeError`); bỏ qua trùng lặp cùng `(event_name, callback)` và trả về closure `unsubscribe()`.
- `unsubscribe`: Hủy đăng ký an toàn; trả về `True` nếu tìm thấy và xóa, `False` nếu chưa tồn tại (không ném lỗi).
- `publish`: Duyệt trên **bản sao danh sách subscribers** tại thời điểm gọi (bảo vệ bằng `RLock`) để an toàn khi callback tự gọi `subscribe`/`unsubscribe` trong lúc dispatch; trả về số callback đã gọi.
- Không biến `EventBus` thành global Singleton — luôn truyền qua constructor (Dependency Injection).

---

## 13. `Command`, `ViewportChangeCommand`, `CommandHistory` (`src/patterns/command_history.py`)

### Signatures
```python
class Command(ABC):
    @property
    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...

class ViewportChangeCommand(Command):
    def __init__(
        self,
        apply_fn: Callable[[ViewportState], None],
        old_viewport: ViewportState,
        new_viewport: ViewportState,
        description: str = "Viewport Change",
    ) -> None: ...

class CommandHistory:
    def __init__(self, max_size: int = 100) -> None: ...
    def execute(self, cmd: Command) -> None: ...
    def undo(self) -> Command | None: ...
    def redo(self) -> Command | None: ...
    def can_undo(self) -> bool: ...
    def can_redo(self) -> bool: ...
    def clear(self) -> None: ...
    def __len__(self) -> int: ...
```

### Invariants & Edge Cases
- `max_size < 1` $\to$ raise `ValueError`; `not callable(apply_fn)` $\to$ raise `TypeError`.
- `execute(cmd)`: Gọi `cmd.execute()`, đẩy `cmd` vào `undo_stack`, **xóa sạch `redo_stack`**, và nếu `len(undo_stack) > max_size` thì loại bỏ lệnh cũ nhất ở đáy stack.
- `undo()`: Nếu `can_undo()` là `False` trả `None`; ngược lại gọi `cmd.undo()`, pop khỏi `undo_stack`, đẩy vào `redo_stack`, trả về `cmd`.
- `redo()`: Nếu `can_redo()` là `False` trả `None`; ngược lại gọi `cmd.execute()`, pop khỏi `redo_stack`, đẩy vào `undo_stack`, trả về `cmd`.

---

## 14. `VisibleFrame`, `ChartCanvasWidget` & `MainWindow` (`src/ui/chart_canvas.py`, `src/ui/main_window.py`)

### Signatures & Responsibilities
```python
# src/ui/chart_canvas.py
@dataclass(frozen=True)
class VisibleFrame:
    viewport: ViewportState
    range_stats: RangeStats | None
    render_candles: list[Candle]
    candle_indices: list[float]
    sma_points: list[tuple[float, float]]
    donchian_upper: list[tuple[float, float]]
    donchian_middle: list[tuple[float, float]]
    donchian_lower: list[tuple[float, float]]
    decimated_close_points: list[tuple[float, float]]
    total_candles: int
    start_idx: int
    end_idx: int

class ChartCanvasWidget(QWidget):
    def __init__(
        self,
        event_bus: EventBus | None = None,
        command_history: CommandHistory | None = None,
        sma_window: int = 20,
        donchian_window: int = 20,
        parent: QWidget | None = None,
    ) -> None: ...

    def compute_visible_frame(
        self,
        width_px: int | None = None,
        height_px: int | None = None,
        max_render_candles: int = 300,
    ) -> VisibleFrame: ...
    def set_candles(self, candles: Sequence[Candle], fit: bool = True) -> None: ...
    def append_or_update_candle(self, candle: Candle, auto_follow: bool = True) -> str: ...
    def set_viewport(
        self,
        viewport: ViewportState,
        record_history: bool = False,
        description: str = "Viewport Change",
    ) -> None: ...
    def get_viewport(self) -> ViewportState: ...
    def fit_all(self, record_history: bool = False) -> None: ...
    def set_overlays(
        self,
        *,
        sma: bool | None = None,
        donchian: bool | None = None,
        volume: bool | None = None,
    ) -> None: ...
    def paintEvent(self, event: QPaintEvent) -> None: ...

# src/ui/main_window.py
class MainWindow(QMainWindow):
    def __init__(
        self,
        csv_path: str | Path | None = None,
        ring_capacity: int = 256,
        sma_window: int = 20,
        donchian_window: int = 20,
        parent: QWidget | None = None,
    ) -> None: ...
```

### Invariants & Behavior
- **`ChartCanvasWidget`:**
  - Kế thừa `PyQt6.QtWidgets.QWidget` và vẽ hoàn toàn bằng `PyQt6.QtGui.QPainter` (nền lưới, thân & râu nến, cột khối lượng, SMA/Donchian overlays, crosshair).
  - Phương thức **`compute_visible_frame(self, width_px: int | None = None, height_px: int | None = None, max_render_candles: int = 300) -> VisibleFrame`** phải chạy **100% headless** (không phụ thuộc sự kiện sơn `paintEvent` hay vòng lặp GUI), thực hiện:
    1. Xác định dải chỉ số hiển thị từ `ViewportState` (với kích thước `width_px`, `height_px` truyền vào hoặc từ widget).
    2. Truy vấn `SegmentTree.query(start_idx, end_idx + 1)` để lấy `RangeStats(min_low, max_high, volume_sum)`.
    3. Áp dụng `aggregate_ohlcv_buckets(...)` khi số nến hiển thị vượt quá `max_render_candles` và `LTTBDecimator.downsample(...)` cho `decimated_close_points`.
    4. Cập nhật `CoordinateTransformer` và xây dựng `QuadTree` cho các điểm nến hiển thị để phục vụ hover snapping.
    5. Tính các đường chỉ báo (`SlidingWindowIndicators.sma`, `donchian_channels`) và trả về `VisibleFrame` frozen dataclass chứa đầy đủ `viewport`, `range_stats`, `render_candles`, `candle_indices`, `sma_points`, `donchian_upper`, `donchian_middle`, `donchian_lower`, `decimated_close_points`, `total_candles`, `start_idx`, `end_idx`.
- **`MainWindow`:**
  - Kế thừa `PyQt6.QtWidgets.QMainWindow`, chứa `ChartCanvasWidget`.
  - Tích hợp `QTimer` Replay: các nút Play, Pause, Reset, Speed selector.
  - Indicator Toggles: bật/tắt SMA, Donchian Channels, Volume.
  - Undo / Redo: gắn `CommandHistory` và cập nhật trạng thái bật/tắt nút qua `EventBus`.
  - CSV Reload: nạp lại tệp CSV qua `csv_loader.load_candles` và làm mới toàn bộ `RingBuffer` / `SegmentTree` / `ViewportState`.
  - Status bar: hiển thị OHLCV tại vị trí crosshair, `RangeStats` vùng nhìn thấy từ `SegmentTree`, và thông số khung hình.

### Edge Cases
- Tập dữ liệu rỗng (`0` nến) hoặc `1` nến có `high == low`: `compute_visible_frame()` không được chia cho 0 khi tính `min_price`/`max_price` (tự động mở rộng epsilon/padding quanh mức giá đơn lẻ) và trả về `VisibleFrame` an toàn (`range_stats=None`, danh sách rỗng khi `total_candles == 0`).
- `max_render_candles < 1` $\to$ raise `ValueError`.

---

## 15. `main_cli` (`src/main.py`)

### Signatures
```python
def build_parser() -> argparse.ArgumentParser: ...

def main(argv: Sequence[str] | None = None) -> int: ...

def run_cli(
    csv_path: str | Path = "data/sample_ohlcv.csv",
    capacity: int = 256,
    window: int = 20,
) -> dict[str, Any]: ...

def run_benchmark(
    count: int = 10000,
    capacity: int = 256,
    window: int = 20,
) -> dict[str, Any]: ...

def run_gui(
    csv_path: str | Path | None = "data/sample_ohlcv.csv",
    capacity: int = 256,
    window: int = 20,
) -> int: ...
```

### CLI Flags Contract (`build_parser()`)
| Cờ CLI | Nhóm / Kiểu | Giá trị mặc định | Mô tả |
|---|---|---|---|
| `--cli` | Mutually exclusive mode (`store_true`) | `False` | Chạy phân tích tổng hợp OHLCV, `RingBuffer`, `SegmentTree`, chỉ báo & LTTB ở chế độ headless CLI (`return 0`). |
| `--benchmark` | Mutually exclusive mode (`store_true`) | `False` | Chạy benchmark `time.perf_counter()` & `tracemalloc` so sánh `RingBuffer`, `SlidingWindowIndicators` vs naive $O(N \cdot W)$, `SegmentTree` vs `scan_range`, và `LTTBDecimator` (`return 0`). |
| `--gui` | Mutually exclusive mode (`store_true`) | Chế độ mặc định khi không truyền `--cli`/`--benchmark` | Khởi chạy giao diện desktop PyQt6 `MainWindow` (`return int(app.exec())`). |
| `--csv` | `str` | `"data/sample_ohlcv.csv"` | Đường dẫn tới tệp dữ liệu OHLCV CSV đầu vào. |
| `--count` | `int` | `10000` | Số lượng nến giả lập tạo cho chế độ `--benchmark`. |
| `--capacity` | `int` | `256` | Dung lượng `RingBuffer` (`ring_capacity` trong `MainWindow`). |
| `--window` | `int` | `20` | Kích thước cửa sổ cho các chỉ báo trượt (`sma_window`, `donchian_window`). |

### Invariants & Edge Cases
- Nhóm cờ `--cli`, `--benchmark`, `--gui` là **mutually exclusive** (truyền đồng thời hai cờ chế độ sẽ bị `argparse` từ chối). Khi không truyền cờ nào, `main()` mặc định gọi `run_gui(...)`.
- Tham số số nguyên `capacity`, `window`, `count` được kiểm tra bởi `_validate_positive_int`: nếu là `bool` hoặc `< 1` $\to$ raise `ValueError`.
- Khi `run_cli` đọc tệp CSV rỗng (`total_candles == 0`), trả về `dict` tóm tắt hợp lệ với `total_candles == 0`, `range_stats is None`, `lttb_count == 0` mà không ném lỗi chia cho 0.
