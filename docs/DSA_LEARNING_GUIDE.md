# CẨM NANG HỌC THUẬT DSA & KIẾN TRÚC HỆ THỐNG: INTERACTIVE TRADINGVIEW STOCK CHART ENGINE

**Dự án:** Interactive TradingView Stock Chart Engine (DSA Python)  
**Ngôn ngữ & Công nghệ:** Python 3.10+ (đã kiểm chứng trên Python 3.14.9), PyQt6 (`PyQt6>=6.6.0`, custom `QPainter` widget), `pytest>=8.0.0` (đã kiểm chứng trên pytest 9.2.0).  
**Cấu trúc phân công:** 4 Thành viên (25% – 25% – 25% – 25%).

---

## MỤC LỤC TỔNG QUAN

1. [Tổng quan Kiến trúc Hệ thống & Quy ước Kỹ thuật](#0-tổng-quan-kiến-trúc-hệ-thống--quy-ước-kỹ-thuật)
2. [Chương 1 — Thành viên 1 (25%): Data Engineer & Ring Buffer Owner](#chương-1--thành-viên-1-25-data-engineer--ring-buffer-owner)
3. [Chương 2 — Thành viên 2 (25%): Sliding Window Analytics & Coordinate Math Owner](#chương-2--thành-viên-2-25-sliding-window-analytics--coordinate-math-owner)
4. [Chương 3 — Thành viên 3 (25%): Range Query & Decimation Algorithms Owner](#chương-3--thành-viên-3-25-range-query--decimation-algorithms-owner)
5. [Chương 4 — Thành viên 4 (25%): Team Lead, PyQt6 UI & System Integration Owner](#chương-4--thành-viên-4-25-team-lead-pyqt6-ui--system-integration-owner)
6. [Phụ lục — Danh mục Tài liệu Tham khảo Chính thức (Verified Official URLs)](#phụ-lục--danh-mục-tài-liệu-tham-khảo-chính-thức)

---

## 0. TỔNG QUAN KIẾN TRÚC HỆ THỐNG & QUY ƯỚC KỸ THUẬT

### 0.1. Sơ đồ Luồng Dữ liệu & Kiến trúc Tổng thể

Hệ thống mô phỏng kiến trúc lõi của một công cụ biểu đồ tài chính thời gian thực đạt **60 FPS** ($\le 16.67\text{ ms}$ cho mỗi khung hình), ngay cả khi dữ liệu chứa $10{,}000$ đến $100{,}000+$ cây nến OHLCV:

```text
+-------------------------------------------------------------------------------+
| 1. DATA INGESTION & STREAMING LAYER (Thành viên 1 - 25%)                      |
|   data/sample_ohlcv.csv / data_simulator.py                                   |
|     --> Candle (Frozen Dataclass + OHLCV Invariants)                          |
|     --> csv_loader.py (Strict monotonic timestamp & finite number validation) |
|     --> RingBuffer (Custom Circular Array, O(1) push overwrite, NO deque)     |
|     --> ReplayDataSource (step, reset, replace_or_append)                     |
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+---------------------------------------+---------------------------------------+
| 2. INDEXING, ANALYTICS & SPATIAL LAYER (Thành viên 2 & Thành viên 3 - 50%)    |
|                                                                               |
|  [Thành viên 3: Range & Decimation]     [Thành viên 2: Sliding Analytics]     |
|   - SegmentTree: O(log N) query [L,R)    - CircularDeque: 2x auto-resize      |
|     tra ve RangeStats(min, max, vol)     - MonotonicDeque: O(1) amortized     |
|   - LTTBDecimator: Line series shape     - SlidingWindowIndicators:           |
|   - aggregate_ohlcv_buckets: Nến Nhật      SMA, EMA, Donchian, Bollinger      |
|   - QuadTree 2D: Crosshair snapping      - CoordinateTransformer: Affine W<->S|
+---------------------------------------+---------------------------------------+
                                        |
                                        v
+---------------------------------------+---------------------------------------+
| 3. PATTERNS, UI RENDERING & INTEGRATION (Thành viên 4 - 25%)                  |
|   - EventBus (Observer Pattern: subscribe / unsubscribe / publish)            |
|   - CommandHistory (Command Pattern: execute / undo / redo, max_size=100)     |
|   - ChartCanvasWidget.compute_visible_frame()  <-- Headless testable logic    |
|   - ChartCanvasWidget.paintEvent(QPainter)     <-- Pure 60 FPS GPU/CPU draw   |
|   - MainWindow (QTimer Replay, Indicator Toggles, Undo/Redo, CSV Reload)      |
+-------------------------------------------------------------------------------+
```

### 0.2. Lệnh Chạy Chuẩn Toàn Dự Án

Mọi thành viên sử dụng thống nhất bộ lệnh chuẩn sau đây trong môi trường dự án:

```bash
# 1. Cài đặt dependencies
pip install -r requirements.txt

# 2. Chạy toàn bộ test suite (pytest)
pytest -v

# 3. Chạy chế độ CLI kiểm tra pipeline dữ liệu & thuật toán không cần GUI
python3 -m src.main --cli

# 4. Chạy chế độ Benchmark đo độ trễ p50/p95/p99 và bộ nhớ
python3 -m src.main --benchmark

# 5. Khởi chạy ứng dụng Desktop PyQt6 GUI (mặc định --gui)
python3 -m src.main

# Cú pháp CLI đầy đủ:
python3 -m src.main [--cli | --benchmark | --gui] [--csv data/sample_ohlcv.csv] [--count 10000] [--capacity 256] [--window 20]
```

### 0.3. Bảng Phân công 25% – 25% – 25% – 25%

| Thành viên | Vai trò | Tỷ trọng | Modules & Tests sở hữu |
| :--- | :--- | :---: | :--- |
| **Thành viên 1** | Data Engineer & Ring Buffer Owner | **25%** | `src/core/candle.py`, `src/core/csv_loader.py`, `src/core/ring_buffer.py`, `src/core/data_simulator.py`, `data/sample_ohlcv.csv`, `tests/test_ring_buffer.py` |
| **Thành viên 2** | Sliding Window Analytics & Coordinate Math Owner | **25%** | `src/algorithms/monotonic_deque.py`, `src/core/coordinate_math.py`, `tests/test_monotonic_deque.py` |
| **Thành viên 3** | Range Query & Decimation Algorithms Owner | **25%** | `src/algorithms/segment_tree.py`, `src/algorithms/lttb_decimator.py`, `src/algorithms/quad_tree.py`, `tests/test_segment_tree.py`, `tests/test_lttb.py` |
| **Thành viên 4** | Team Lead, PyQt6 UI & System Integration Owner | **25%** | `src/patterns/observer.py`, `src/patterns/command_history.py`, `src/ui/chart_canvas.py`, `src/ui/main_window.py`, `src/main.py`, `tests/test_integration.py`, `.github/workflows/python-tests.yml` |

---

## CHƯƠNG 1 — THÀNH VIÊN 1 (25%): DATA ENGINEER & RING BUFFER OWNER

**Phạm vi files:**
- `src/core/candle.py`
- `src/core/csv_loader.py`
- `src/core/ring_buffer.py`
- `src/core/data_simulator.py`
- `data/sample_ohlcv.csv`
- `tests/test_ring_buffer.py`

### 1.1. Bất biến Dữ liệu của `Candle` (Frozen Dataclass & OHLCV Invariants)

Trong tài chính định lượng, một cây nến Nhật (Candlestick) biểu diễn phân phối giá trong một khung thời gian cố định (`interval_sec`) thông qua 6 đại lượng: `timestamp`, `open`, `high`, `low`, `close`, `volume`.

```text
          |  <-- high  (Giá cao nhất trong phiên: high >= max(open, close))
          |
      +---+---+  <-- max(open, close)  [Thân nến: Xanh nếu close >= open, Đỏ nếu close < open]
      |       |
      | BODY  |
      |       |
      +---+---+  <-- min(open, close)
          |
          |  <-- low   (Giá thấp nhất trong phiên: low <= min(open, close))
```

**Hợp đồng API (`src/core/candle.py`):**
- Class `Candle` sử dụng `@dataclass(frozen=True, slots=True)` với các trường:
  - `timestamp: int` (Unix epoch seconds)
  - `open: float`
  - `high: float`
  - `low: float`
  - `close: float`
  - `volume: float`
- **Bất biến bắt buộc kiểm tra trong `__post_init__`**:
  1. Tất cả giá trị số (`open`, `high`, `low`, `close`, `volume`) phải hữu hạn (`math.isfinite(val)` $\to$ loại bỏ `NaN`, `+inf`, `-inf`).
  2. `volume >= 0.0` (khối lượng giao dịch không thể âm).
  3. `low <= min(open, close)` (giá thấp nhất không thể lớn hơn giá mở hoặc đóng cửa).
  4. `high >= max(open, close)` (giá cao nhất không thể nhỏ hơn giá mở hoặc đóng cửa).
  5. `timestamp >= 0` (hoặc số nguyên hợp lệ, không phải boolean).

**Vì sao dùng `frozen=True`?**
1. **Tính bất biến (Immutability):** Một cây nến lịch sử sau khi đóng cửa không bao giờ bị sửa đổi ngẫu nhiên từ một module khác trong hệ thống đa sự kiện (`EventBus`).
2. **Tối ưu bộ nhớ & Hashability:** Khi kết hợp `frozen=True` (và `slots=True` trong Python 3.10+), Python không tạo `__dict__` cho từng instance `Candle`, tiết kiệm hàng chục MB RAM khi lưu $100{,}000+$ nến và cho phép đưa `Candle` vào `set`/`dict` nếu cần.

```python
from dataclasses import dataclass
import math


@dataclass(frozen=True, slots=True)
class Candle:
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self) -> None:
        if isinstance(self.timestamp, bool) or not isinstance(self.timestamp, int):
            raise ValueError(f"timestamp must be an integer, got {self.timestamp!r}")
        for name, val in (
            ("open", self.open),
            ("high", self.high),
            ("low", self.low),
            ("close", self.close),
            ("volume", self.volume),
        ):
            if not math.isfinite(val):
                raise ValueError(f"{name} must be finite, got {val!r}")
        if self.volume < 0:
            raise ValueError(f"volume must be >= 0, got {self.volume}")
        if self.low > min(self.open, self.close):
            raise ValueError(
                f"low ({self.low}) must be <= min(open={self.open}, close={self.close})"
            )
        if self.high < max(self.open, self.close):
            raise ValueError(
                f"high ({self.high}) must be >= max(open={self.open}, close={self.close})"
            )
```

### 1.2. Nạp & Kiểm định CSV Nghiêm ngặt (`src/core/csv_loader.py`)

**Hợp đồng API:**
- `parse_candle_row(row: dict, line_num: int) -> Candle`
- `load_candles(path: str) -> list[Candle]`

**Nguyên tắc kiểm định từng dòng (Row-by-row Validation):**
1. **Lỗi số học & thiếu cột:** Nếu bất kỳ cột nào (`timestamp`, `open`, `high`, `low`, `close`, `volume`) bị thiếu, rỗng (`""` / `None`), hoặc không ép kiểu được sang `int`/`float`, ném ra `ValueError` kèm **số dòng chính xác (`line_num`)** để kỹ sư dữ liệu định vị tức thì (ví dụ: `f"Line {line_num}: invalid numeric value for 'close'"`).
2. **Thứ tự thời gian đơn điệu tăng nghiêm ngặt:** Mọi dòng $i > 0$ phải thỏa mãn `candle.timestamp > prev_timestamp`. Nếu phát hiện timestamp **trùng lặp** (`==`) hoặc **sai thứ tự** (`<`), phải ném `ValueError` kèm `line_num`. Lý do: Thuật toán `SegmentTree`, `CoordinateTransformer` và tìm kiếm nhị phân theo thời gian giả định trục thời gian luôn tăng nghiêm ngặt.
3. **File rỗng / chỉ có header:** Nếu file trống hoàn toàn hoặc chỉ có dòng tiêu đề (`timestamp,open,high,low,close,volume`) mà không có dòng dữ liệu nào, `load_candles` trả về `[]` (danh sách rỗng) thay vì báo lỗi.

### 1.3. Ring Buffer — Mảng Vòng Kích Thước Cố Định (`src/core/ring_buffer.py`)

#### 1.3.1. Trực giác & Cơ chế Modulo Wrap-Around

Khi dữ liệu tick/nến truyền trực tiếp theo thời gian thực (streaming), nếu ta cứ `.append()` mãi vào một `list` vô hạn, bộ nhớ sẽ tăng tuyến tính $O(T)$ cho đến khi cạn RAM. **Ring Buffer (Circular Buffer)** giải quyết bài toán này bằng cách cấp phát **một mảng kích thước cố định `capacity`** ngay từ đầu: `self._buffer: list[Any] = [None] * capacity`.

Ta duy trì 2 chỉ số (hoặc `write_idx` và `size`):
- `self._write_idx` (hoặc `tail`): vị trí ô nhớ sẽ ghi phần tử kế tiếp.
- `self._size`: số phần tử hiện đang lưu hợp lệ ($0 \le \text{size} \le \text{capacity}$).
- Chỉ số phần tử cũ nhất (`head` / `start_idx`) được suy ra trực tiếp:
  $$\text{head} = (\text{write\_idx} - \text{size}) \bmod \text{capacity}$$

**Minh họa ASCII qua từng bước với `capacity = 4`:**

```text
Bước 0: Khởi tạo (capacity = 4)
  _buffer = [ None, None, None, None ]   write_idx = 0, size = 0

Bước 1: push(10), push(20), push(30)
  _buffer = [  10,   20,   30,  None ]   write_idx = 3, size = 3
               ^                 ^
              head              write_idx

Bước 2: push(40)  --> Bộ đệm ĐẦY (is_full() == True)
  _buffer = [  10,   20,   30,   40  ]   write_idx = (3 + 1) % 4 = 0, size = 4
               ^
          head & write_idx

Bước 3: push(50)  --> GHI ĐÈ O(1) lên phần tử cũ nhất (10 tại index 0)!
  _buffer = [  50,   20,   30,   40  ]   write_idx = (0 + 1) % 4 = 1, size = 4
                     ^     ^
                    head  ...   (oldest = 20 ở idx 1, newest = 50 ở idx 0)

  get_all() duyệt i từ 0 đến size-1 tại vị trí (head + i) % capacity:
  idx = (1+0)%4=1 -> 20
  idx = (1+1)%4=2 -> 30
  idx = (1+2)%4=3 -> 40
  idx = (1+3)%4=0 -> 50   ==> Kết quả đúng thứ tự thời gian: [20, 30, 40, 50]
```

#### 1.3.2. Tại sao TUYỆT ĐỐI KHÔNG dùng `collections.deque` ở Module này?

Trong Python chuẩn có `collections.deque(maxlen=capacity)`. Tuy nhiên, trong học phần DSA này ta **cấm sử dụng `collections.deque`** để tự cài đặt `RingBuffer` vì 4 lý do kỹ thuật và sư phạm cốt lõi:
1. **Tư duy Index Arithmetic & Wrap-Around:** Làm chủ phép toán chia dư `(idx + 1) % capacity` và suy diễn vị trí đầu/cuối từ con trỏ vòng — đây là nền tảng của bộ đệm mạng (network ring buffers), audio DSP, và lock-free SPSC queues trong C/C++/Rust.
2. **Hiểu mô hình cấp phát bộ nhớ liên tục cố định:** `self._buffer = [None] * capacity` cấp phát một mảng con trỏ liên tục đúng 1 lần, không cấp phát/giải phóng block động trong quá trình stream (ngược lại, `collections.deque` trong CPython là danh sách liên kết đôi các khối 64 con trỏ — doubly-linked list of 64-element blocks).
3. **Truy cập ngẫu nhiên $O(1)$ thực sự:** Mảng vòng hỗ trợ ánh xạ chỉ số logic $i \mapsto (\text{head} + i) \bmod \text{capacity}$ trong $O(1)$, trong khi truy cập giữa `collections.deque` tốn $O(N)$.
4. **Kiểm soát tường minh chính sách Overwrite $O(1)$:** Tự định nghĩa hành vi ghi đè khi đầy và dựng lại snapshot theo thứ tự thời gian (`get_all()`) trong $O(K)$.

#### 1.3.3. Hợp đồng API đầy đủ của `RingBuffer`

```python
from typing import Any


class RingBuffer:
    def __init__(self, capacity: int) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity <= 0:
            raise ValueError(f"capacity must be a positive integer, got {capacity!r}")
        self._capacity: int = capacity
        self._buffer: list[Any] = [None] * capacity
        self._write_idx: int = 0
        self._size: int = 0

    def push(self, item: Any) -> None:
        self._buffer[self._write_idx] = item
        self._write_idx = (self._write_idx + 1) % self._capacity
        if self._size < self._capacity:
            self._size += 1

    def get_all(self) -> list[Any]:
        if self._size == 0:
            return []
        head = (self._write_idx - self._size) % self._capacity
        if head + self._size <= self._capacity:
            return self._buffer[head : head + self._size]
        return self._buffer[head:] + self._buffer[: self._write_idx]

    def latest(self) -> Any | None:
        if self._size == 0:
            return None
        last_idx = (self._write_idx - 1) % self._capacity
        return self._buffer[last_idx]

    def __len__(self) -> int:
        return self._size

    def is_full(self) -> bool:
        return self._size == self._capacity

    def clear(self) -> None:
        self._buffer = [None] * self._capacity
        self._write_idx = 0
        self._size = 0
```

### 1.4. Bộ sinh Dữ liệu Giả lập & Replay (`src/core/data_simulator.py`)

- `generate_synthetic_candles(count: int, seed: int = 42, start_ts: int = 1700000000, interval_sec: int = 60) -> list[Candle]`: Sử dụng `random.Random(seed)` để tái lập 100% chuỗi dữ liệu kiểm thử (deterministic seeding). Giá mở cửa nến sau nối tiếp giá đóng cửa nến trước (`open = prev_close`), tính `high` và `low` sao cho luôn thỏa mãn bất biến `Candle`.
- `ReplayDataSource(candles: list[Candle])`:
  - `step()`: phát ra cây nến tiếp theo theo con trỏ nội bộ (trả về `None` nếu đã hết).
  - `reset()`: đặt con trỏ về đầu chuỗi.
  - `replace_or_append(candle: Candle)`: nếu `candle.timestamp` bằng timestamp nến cuối cùng trong nguồn, cập nhật (thay thế) nến đang chạy đó; nếu lớn hơn, nối thêm vào cuối; nếu nhỏ hơn, ném `ValueError`.

### 1.5. Edge Cases & Bài tập Thực hành Từng bước (Thành viên 1)

**Edge Cases cần kiểm thử bắt buộc:**
- `RingBuffer(0)` hoặc `RingBuffer(-5)` phải ném `ValueError`.
- `RingBuffer(1)` (dung lượng tối thiểu): `push(a)`, `push(b)` $\implies$ `latest() == b`, `get_all() == [b]`.
- `clear()` trên `RingBuffer` đầy phải giải phóng tham chiếu đối tượng (`[None] * capacity`) tránh memory leak.
- `Candle` với `float('nan')`, `float('inf')`, `volume = -0.1`, `low > open`, hoặc `high < close` đều phải bị từ chối với `ValueError`.
- `csv_loader` với file rỗng (`""`) hoặc chỉ có header trả về `[]`; file có timestamp trùng lặp hoặc giảm dần tại dòng 5 phải báo `ValueError` chứa `"5"`.

**Bài tập thực hành từng bước:**
- **Step 1:** Viết `src/core/candle.py` với `frozen=True` dataclass và kiểm thử tất cả 5 bất biến bằng các case hợp lệ/không hợp lệ.
- **Step 2:** Viết `src/core/ring_buffer.py` chỉ dùng Python `list` cố định kích thước (`[None] * capacity`) và phép toán `%`. Vẽ tay trạng thái sau 7 lần `push` trên `capacity=4`.
- **Step 3:** Tối ưu `get_all()` dùng lát cắt slice (tối đa 2 lát cắt liên tiếp thay vì vòng lặp Python từng phần tử) và xác minh kết quả khớp 100%.
- **Step 4:** Viết `src/core/csv_loader.py` (`parse_candle_row`, `load_candles`) và sinh file mẫu `data/sample_ohlcv.csv` bằng `data_simulator.py`.
- **Step 5:** Hoàn thiện `tests/test_ring_buffer.py` và chạy `pytest tests/test_ring_buffer.py -v` đạt 100% pass.

---

## CHƯƠNG 2 — THÀNH VIÊN 2 (25%): SLIDING WINDOW ANALYTICS & COORDINATE MATH OWNER

**Phạm vi files:**
- `src/algorithms/monotonic_deque.py`
- `src/core/coordinate_math.py`
- `tests/test_monotonic_deque.py`

### 2.1. `CircularDeque` 2 Đầu Tự Cài Đặt với Auto-Resize 2x

Để phục vụ `MonotonicDeque` (cần thêm/xóa hiệu quả ở **cả 2 đầu** `front` và `back`), Thành viên 2 tự cài đặt `CircularDeque` trên mảng vòng (tuyệt đối không dùng `collections.deque`).

**Hợp đồng API (`CircularDeque`):**
- `CircularDeque(capacity: int = 16)`
- `push_front(x)`, `push_back(x)`, `pop_front()`, `pop_back()`, `peek_front()`, `peek_back()`, `__len__()`, `is_empty()`, `to_list()`.
- Khi mảng đầy (`_size == _capacity`), tự động gọi `_resize(self._capacity * 2)`.

**Cơ chế Duỗi thẳng (Unrolling) khi Auto-Resize 2x:**

Khi mảng vòng đầy trong trạng thái wrap-around (`_head` không nằm tại `0`), ta **không được** chỉ nối thêm `None` vào cuối mảng (sẽ phá vỡ thứ tự logic khi modulo thay đổi từ `% cap` sang `% (2*cap)`!). Thay vào đó, ta phải chép theo thứ tự logic từ `0` đến `_size - 1`:

```text
Trước resize (cap = 4, _head = 2, _size = 4):
  Vật lý:  [ 30,  40,  10,  20 ]
                       ^
                     _head (logic: [10, 20, 30, 40])

Sau _resize(8):
  for i in range(_size):
      new_buf[i] = _buffer[(_head + i) % _capacity]
  _buffer   = [ 10,  20,  30,  40,  None, None, None, None ]
  _head     = 0
  _capacity = 8
```

Mỗi phép `push_front`/`push_back` đạt **$O(1)$ amortized** (xem chứng minh đầy đủ bằng Potential Method trong `docs/complexity_analysis.md`).

### 2.2. `MonotonicDeque` — Hàng Đợi Đơn Điệu $O(1)$ Amortized

Bài toán kinh điển: Cho chuỗi giá $A[0 \dots N-1]$ và độ dài cửa sổ $W$. Tại mỗi vị trí $i$, tìm giá trị nhỏ nhất (hoặc lớn nhất) trong cửa sổ $[i - W + 1, i]$.

- Nếu quét lại cửa sổ ở mỗi bước: $O(N \cdot W)$ $\to$ với $N = 100{,}000, W = 500$ tốn $5 \times 10^7$ phép toán (treo UI!).
- Nếu dùng Heap (Min/Max Heap): $O(N \log W)$ và cần lazy deletion.
- Nếu dùng **`MonotonicDeque`**: đạt **$O(N)$ tổng thời gian**, tức **$O(1)$ amortized mỗi bước**, và bộ nhớ chỉ $O(W)$!

**Nguyên lý hoạt động (`mode='min'`):**
Giả sử phần tử mới `(idx_new, val_new)` chuẩn bị vào cửa sổ. Nếu trong hàng đợi đang có phần tử `(idx_old, val_old)` ở cuối (`back`) mà `val_old >= val_new`:
- Vì `idx_old < idx_new`, phần tử cũ sẽ hết hạn (ra khỏi cửa sổ) **trước** phần tử mới, và lại tệ hơn (lớn hơn hoặc bằng) phần tử mới.
- Do đó `(idx_old, val_old)` **không bao giờ có cơ hội trở thành giá trị nhỏ nhất** ở hiện tại hay bất kỳ cửa sổ tương lai nào! Ta tự tin `pop_back()` loại bỏ vĩnh viễn.

```text
Ví dụ dãy giá: [10, 14, 12, 8, 15], W = 3, mode = 'min'
Lưu cặp (index, value) trong deque tăng dần về value:

i=0 (val=10): push(0,10)            -> Deque: [(0,10)]            | min=10
i=1 (val=14): 10 < 14, giữ          -> Deque: [(0,10), (1,14)]    | min=10
i=2 (val=12): 14 >= 12 -> pop(1,14) -> Deque: [(0,10), (2,12)]    | min=10
i=3 (val=8):  evict_before(3-3+1=1) -> pop_front(0,10)
              12 >= 8  -> pop(2,12) -> Deque: [(3,8)]             | min=8
i=4 (val=15): 8 < 15, giữ           -> Deque: [(3,8), (4,15)]     | min=8
```

**Hợp đồng API (`MonotonicDeque`):**
- `MonotonicDeque(mode: str = "min")` (chấp nhận `"min"` hoặc `"max"`, giá trị khác ném `ValueError`).
- `push(index: int, value: float) -> None`: xóa các phần tử cuối vi phạm tính đơn điệu (tăng nghiêm ngặt cho `'min'`, giảm nghiêm ngặt cho `'max'`), rồi `push_back((index, value))`.
- `evict_before(min_valid_index: int) -> None`: lặp `while not empty and peek_front()[0] < min_valid_index: pop_front()`.
- `extrema() -> tuple[int, float] | None`: trả về `peek_front()` hoặc `None` nếu rỗng.
- `clear() -> None`.

### 2.3. `SlidingWindowIndicators` — Chỉ báo Kỹ thuật Thời gian Thực

| Chỉ báo | Hàm & Signature | Thuật toán Cài đặt | Độ phức tạp |
| :--- | :--- | :--- | :---: |
| **Rolling Min/Max** | `rolling_min_max(values: list[float], window: int) -> list[tuple[float, float]]` | Chạy đồng thời 1 `MonotonicDeque("min")` và 1 `MonotonicDeque("max")`. | $O(N)$ |
| **SMA** (Simple Moving Average) | `sma(values: list[float], window: int) -> list[float \| None]` | Tổng trượt `running_sum += values[i] - values[i - window]`. Trước khi đủ `window` phần tử ($i < W - 1$) trả `None`. | $O(N)$ |
| **EMA** (Exponential Moving Average) | `ema(values: list[float], window: int) -> list[float \| None]` | $\alpha = \frac{2}{W + 1}$. Với $i < W - 1$: `None`; $i = W - 1$: khởi tạo bằng SMA đầu tiên; $i \ge W$: `alpha * values[i] + (1 - alpha) * prev_ema`. | $O(N)$ |
| **Donchian Channels** | `donchian_channels(candles: list[Candle], window: int) -> list[tuple[float, float, float]]` | Dùng `MonotonicDeque("max")` trên `candle.high` $\to$ `upper`; `MonotonicDeque("min")` trên `candle.low` $\to$ `lower`; `middle = (upper + lower) / 2.0`. Trả `(upper, middle, lower)`. | $O(N)$ |
| **Bollinger Bands** | `bollinger_bands(values: list[float], window: int, num_std: float = 2.0) -> list[tuple[float \| None, float \| None, float \| None]]` | Trả về `(upper, middle, lower)` với `middle = SMA`, `std = sqrt(variance)`. Dùng cửa sổ trượt phương sai hoặc căn chỉnh sai số số thực `max(0.0, E[X^2] - E[X]^2)` (hoặc Welford/cục bộ khi cần độ chính xác cao). | $O(N)$ |

> [!WARNING]
> **Cẩn trọng sai số dấu phẩy động (Catastrophic Cancellation) trong Bollinger Bands:** Nếu giá cổ phiếu lớn (ví dụ $50{,}000.00$) mà biến động nhỏ ($\pm 0.5$), công thức $\sum x^2 / W - \mu^2$ có thể tạo số âm cực nhỏ $-10^{-11}$ do làm tròn IEEE-754. Luôn kẹp `variance = max(0.0, variance)` trước khi gọi `math.sqrt(variance)` (hoặc tính $\sum (x_k - \mu)^2 / W$ hoặc Welford trên cửa sổ trượt).

### 2.4. Toán học Biến đổi Tọa độ Affine (`src/core/coordinate_math.py`)

Trên màn hình máy tính (`QWidget`), gốc tọa độ `(0, 0)` nằm ở **góc trên bên trái**, trục $X$ hướng sang phải, còn trục $Y$ hướng **từ trên xuống dưới**. Ngược lại, trong không gian đồ thị tài chính (World Space), giá cao nằm **phía trên**, giá thấp nằm **phía dưới**!

**Hợp đồng API (`ViewportState` & `CoordinateTransformer`):**
```python
@dataclass
class ViewportState:
    start_idx: float
    end_idx: float
    min_price: float
    max_price: float
    width_px: int
    height_px: int
    padding_left: int = 12
    padding_right: int = 72    # Dành chỗ cho nhãn giá trục Y bên phải
    padding_top: int = 16
    padding_bottom: int = 28   # Dành chỗ cho trục thời gian bên dưới
```

Đặt kích thước vùng vẽ thực tế (plot area):
$$W_{\text{plot}} = \max(1, \text{width\_px} - \text{padding\_left} - \text{padding\_right})$$
$$H_{\text{plot}} = \max(1, \text{height\_px} - \text{padding\_top} - \text{padding\_bottom})$$

```text
(0, 0) +-------------------------------------------------------+
       |                     padding_top (16px)                |
       |  pad  +-----------------------------------+   pad     |
       |  left |       VÙNG VẼ NẾN (PLOT AREA)     |   right   |
       | (12px)|   max_price  --> y = padding_top  |  (72px)   |
       |       |   min_price  --> y = pad_top+H    |  Nhãn giá |
       |       +-----------------------------------+           |
       |                   padding_bottom (28px)               |
       +-------------------------------------------------------+ (width_px, height_px)
```

**4 Phép biến đổi Affine cốt lõi:**
1. **`index_to_x(idx)`**:
   $$x = \text{padding\_left} + \frac{\text{idx} - \text{start\_idx}}{\text{end\_idx} - \text{start\_idx}} \cdot W_{\text{plot}}$$
2. **`x_to_index(x)`**:
   $$\text{idx} = \text{start\_idx} + \frac{x - \text{padding\_left}}{W_{\text{plot}}} \cdot (\text{end\_idx} - \text{start\_idx})$$
3. **`price_to_y(price)`** *(Đảo chiều trục $Y$)*:
   $$y = \text{padding\_top} + \left(1.0 - \frac{\text{price} - \text{min\_price}}{\text{max\_price} - \text{min\_price}}\right) \cdot H_{\text{plot}}$$
4. **`y_to_price(y)`**:
   $$\text{price} = \text{min\_price} + \left(1.0 - \frac{y - \text{padding\_top}}{H_{\text{plot}}}\right) \cdot (\text{max\_price} - \text{min\_price})$$

Kết hợp lại tạo thành `world_to_screen(idx, price) -> tuple[float, float]` và `screen_to_world(x, y) -> tuple[float, float]`. (Lưu ý bảo vệ chia cho `0` khi `max_price == min_price` hoặc `end_idx == start_idx`).

#### Cursor-Anchored Zoom (`zoom_at_pixel`) & Pan (`pan_by_pixels`)

Khi người dùng lăn con lăn chuột tại tọa độ `anchor_x`, trải nghiệm chuẩn TradingView đòi hỏi **cây nến ngay dưới đầu con trỏ chuột phải đứng yên tại đúng `anchor_x` đó** sau khi phóng to/thu nhỏ:
- Tính tỷ lệ vị trí con trỏ trong vùng vẽ:
  $$r = \frac{\text{anchor\_x} - \text{padding\_left}}{W_{\text{plot}}}$$
- Chỉ số thế giới neo dưới con trỏ trước khi zoom:
  $$\text{anchor\_idx} = \text{start\_idx} + r \cdot (\text{end\_idx} - \text{start\_idx})$$
- Với `zoom_at_pixel(self, anchor_x: float, zoom_factor: float, min_span: float = 5.0, max_span: float = 100000.0) -> ViewportState` (`zoom_factor > 1.0` là phóng to / thu hẹp số nến hiển thị), độ rộng khung mới là $\text{new\_span} = \text{clamp}\!\left(\frac{\text{end\_idx} - \text{start\_idx}}{\text{zoom\_factor}},\, \text{min\_span},\, \text{max\_span}\right)$.
- Để `anchor_idx` vẫn nằm đúng tỷ lệ $r$:
  $$\text{new\_start} = \text{anchor\_idx} - r \cdot \text{new\_span}, \qquad \text{new\_end} = \text{new\_start} + \text{new\_span}$$

Đối với **`CoordinateTransformer.pan_by_pixels(self, dx_px: float) -> ViewportState`**: kéo chuột sang phải (`dx_px > 0`) tức là kéo lịch sử quá khứ sang phải để xem nến cũ hơn, nên `start_idx` và `end_idx` **giảm đi**:
$$\Delta \text{idx} = \frac{\text{dx\_px}}{W_{\text{plot}}} \cdot (\text{end\_idx} - \text{start\_idx}), \qquad \text{new\_start} = \text{start\_idx} - \Delta \text{idx}, \qquad \text{new\_end} = \text{end\_idx} - \Delta \text{idx}$$

### 2.5. Edge Cases & Bài tập Thực hành Từng bước (Thành viên 2)

**Edge Cases cần kiểm thử bắt buộc:**
- `CircularDeque`: `push_front` liên tiếp vượt quá `capacity=16` (kích hoạt auto-resize $16 \to 32 \to 64$) khi `_head != 0`.
- `pop_front()` / `pop_back()` trên deque rỗng phải ném `IndexError`; `peek_front()` / `peek_back()` xử lý nhất quán theo contract.
- `SlidingWindowIndicators` với `values = []`, `window = 1`, `window > len(values)`, và chuỗi giá phẳng hoàn toàn (`min_price == max_price` cho Bollinger `std == 0.0`).
- `CoordinateTransformer` khi `width_px` quá nhỏ, hoặc `max_price == min_price` (tránh `ZeroDivisionError`).

**Bài tập thực hành từng bước:**
- **Step 1:** Cài đặt `CircularDeque` dùng mảng vòng thuần túy, vẽ tay trạng thái trước và sau `_resize()`.
- **Step 2:** Cài đặt `MonotonicDeque` (`mode='min'` và `mode='max'`) trên nền `CircularDeque`.
- **Step 3:** Cài đặt 5 phương thức trong `SlidingWindowIndicators` và đối chiếu với cài đặt brute-force $O(N \cdot W)$ trên dữ liệu ngẫu nhiên 5,000 phần tử.
- **Step 4:** Cài đặt `ViewportState` & `CoordinateTransformer`; kiểm tra tính chất nghịch đảo `screen_to_world(*world_to_screen(i, p)) == (i, p)` với sai số $< 10^{-9}$.
- **Step 5:** Kiểm thử bất biến Cursor-Anchored Zoom: trước và sau `zoom_at_pixel(px, factor)`, giá trị `x_to_index(px)` không đổi; chạy `pytest tests/test_monotonic_deque.py -v`.

---

## CHƯƠNG 3 — THÀNH VIÊN 3 (25%): RANGE QUERY & DECIMATION ALGORITHMS OWNER

**Phạm vi files:**
- `src/algorithms/segment_tree.py`
- `src/algorithms/lttb_decimator.py`
- `src/algorithms/quad_tree.py`
- `tests/test_segment_tree.py`
- `tests/test_lttb.py`

### 3.1. `SegmentTree` & `RangeStats` — Truy vấn Thống kê Khoảng $O(\log N)$

Khi người dùng pan/zoom biểu đồ đến khoảng chỉ số $[L, R)$, trục giá $Y$ phải tự động co giãn vừa khít với `min_low` và `max_high` của tất cả cây nến trong khoảng nhìn thấy đó. Nếu quét tuyến tính $O(N)$ mỗi khung hình với $N = 100{,}000$, riêng bước tìm min/max đã tốn hàng chục mili-giây!

**Hợp đồng API (`src/algorithms/segment_tree.py`):**
- `RangeStats`: `@dataclass(frozen=True, slots=True)` với `min_low: float`, `max_high: float`, `volume_sum: float`.
- `SegmentTree(candles: list[Candle] | None = None)`:
  - `query(left: int, right: int) -> RangeStats | None`: truy vấn đoạn **nửa mở `[left, right)`**. Trả về `None` nếu khoảng rỗng hoặc ngoài biên hợp lệ.
  - `update(index: int, candle: Candle) -> None`: cập nhật cây nến tại `index` (ví dụ live tick cập nhật cây nến cuối) trong $O(\log N)$.
  - `append(candle: Candle) -> None`: thêm nến mới vào cuối; khi vượt quá sức chứa lũy thừa của 2 (`capacity = 2^k`), tự động nhân đôi dung lượng (dynamic power-of-2 capacity rebuild) đạt **$O(\log N)$ amortized**.
  - `__len__() -> int`: trả về số nến hiện tại.
- `scan_range(candles: list[Candle], left: int, right: int) -> RangeStats | None`: hàm quét vét cạn (Brute-Force Oracle $O(N)$) dùng để đối chiếu kiểm định tính đúng đắn 100% của `SegmentTree`.

**Cấu trúc Đại số Monoid của `RangeStats`:**
Phép hợp nhất hai đoạn rời nhau $A$ và $B$:
$$\text{combine}(A, B) = \text{RangeStats}\big(\min(A.\text{min\_low}, B.\text{min\_low}),\; \max(A.\text{max\_high}, B.\text{max\_high}),\; A.\text{volume\_sum} + B.\text{volume\_sum}\big)$$
Phép toán $\text{combine}$ có tính **kết hợp (Associative)** và có phần tử đơn vị $\text{ID} = (+\infty, -\infty, 0.0)$. Đây là điều kiện cần và đủ để `SegmentTree` hoạt động chính xác!

**Sơ đồ Cây Phân đoạn Iterative 1-Indexed (Power-of-2 Capacity = 4):**

```text
Chỉ số nút mảng tree (kích thước 2 * cap = 8, bỏ qua index 0):
                   [1] (0..4)
                 /            \
           [2] (0..2)        [3] (2..4)
           /       \         /       \
       [4] c0   [5] c1   [6] c2   [7] c3

Truy vấn nửa mở [left=1, right=4):
  Khởi tạo l = left + cap = 5, r = right + cap = 8
  - Vòng 1: l=5 (lẻ) -> gom tree[5], l += 1 (l=6); r=8 (chẵn) -> dịch lên l=3, r=4
  - Vòng 2: l=3 (lẻ) -> gom tree[3], l += 1 (l=4); r=4 -> l == r -> Dừng!
  Kết quả = combine(tree[5], tree[3]) = c1 (+) (c2 (+) c3) trong O(log N)!
```

### 3.2. `LTTBDecimator` — Giảm mẫu Chuỗi Thời gian Bảo toàn Hình thái

Khi vẽ các đường chỉ báo (EMA, SMA, đường giá Close) trên màn hình rộng $1200\text{ px}$ với $100{,}000$ điểm dữ liệu, vẽ cả $100{,}000$ đoạn thẳng vừa lãng phí GPU/CPU (hàng trăm điểm đè lên cùng 1 cột pixel) vừa làm khung hình rớt xuống dưới 15 FPS.

**Thuật toán LTTB (Largest-Triangle-Three-Buckets)** từ luận văn thạc sĩ của *Sveinn Steinarsson (2013)* giải quyết bài toán giảm từ $N$ điểm xuống `threshold` điểm ($M \ll N$) sao cho **giữ nguyên hình dáng trực quan, đỉnh nhọn và đáy nhọn**:

1. Giữ nguyên điểm đầu tiên `points[0]` (vào kết quả) và điểm cuối cùng `points[-1]`.
2. Chia $N - 2$ điểm ở giữa thành $M - 2$ buckets có kích thước tương đối bằng nhau.
3. Với mỗi bucket thứ $i$:
   - Gọi $A = (x_A, y_A)$ là điểm **đã được chọn** từ bucket $i - 1$ ngay trước đó.
   - Tính điểm trung bình (centroid) $C = (\bar{x}_{i+1}, \bar{y}_{i+1})$ của toàn bộ các điểm trong **bucket kế tiếp $i + 1$**.
   - Trong bucket hiện tại $i$, chọn điểm $B_j = (x_j, y_j)$ sao cho diện tích tam giác $\triangle A B_j C$ là **lớn nhất**:
     $$\text{Area}(A, B_j, C) = \frac{1}{2} \left| (x_A - \bar{x}_{i+1})(y_j - y_A) - (x_A - x_j)(\bar{y}_{i+1} - y_A) \right|$$

```text
  Bucket i-1        Bucket i (Tìm B_j max Area)         Bucket i+1
     * A  -----------------  * B_2 (Đỉnh nhọn -> Chọn!)  ------ * C (Trung bình)
                           /   \
                         * B_1   * B_3
```

**Hợp đồng API & Quy tắc biên (`src/algorithms/lttb_decimator.py`):**
`LTTBDecimator.downsample(points: Sequence[tuple[float, float]], threshold: int) -> list[tuple[float, float]]`
- `threshold < 0` $\implies$ ném `ValueError`.
- `threshold == 0` hoặc `not points` $\implies$ trả về `[]`.
- `threshold == 1` $\implies$ trả về `[(float(points[0][0]), float(points[0][1]))]`.
- `len(points) <= threshold` $\implies$ trả về toàn bộ `points` đã ép kiểu `(float(x), float(y))`.
- `threshold == 2` (khi `len(points) > 2`) $\implies$ trả về `[first, last]` với `first = (float(points[0][0]), float(points[0][1]))` và `last = (float(points[-1][0]), float(points[-1][1]))`.

### 3.3. `aggregate_ohlcv_buckets` — Gộp Nến Nhật Theo Mật độ Pixel

**Tại sao Nến Nhật KHÔNG thể dùng LTTB thuần?**
LTTB chỉ chọn ra 1 điểm `(x, y)` đơn lẻ để đại diện cho cả một bucket. Nếu áp dụng cho nến Nhật, ta sẽ đánh mất râu nến cao nhất (`high`) hoặc râu nến thấp nhất (`low`) của các cây nến bị bỏ qua, đồng thời làm sai lệch giá mở/đóng cửa và làm mất tổng khối lượng (`volume`) — vi phạm nghiêm trọng độ trung thực phân tích kỹ thuật!

**Giải pháp (`aggregate_ohlcv_buckets`):**
Hợp đồng API: `aggregate_ohlcv_buckets(candles: list[Candle], start_idx: int, end_idx: int, max_candles: int) -> list[Candle]`.
- Cắt vùng nhìn thấy `visible = candles[start:end]`. Nếu `len(visible) <= max_candles`, trả về `visible`.
- Ngược lại, chia `len(visible)` nến thành `max_candles` nhóm (buckets) liên tiếp. Mỗi nhóm gộp tất cả nến $c_0, c_1, \dots, c_{k-1}$ thành **1 cây nến tổng hợp duy nhất**:
  - `timestamp = c_0.timestamp` (thời điểm bắt đầu cụm)
  - `open = c_0.open` (giá mở cửa nến đầu tiên)
  - `high = max(c.high for c in bucket)` (đỉnh cao nhất toàn cụm)
  - `low = min(c.low for c in bucket)` (đáy thấp nhất toàn cụm)
  - `close = c_{-1}.close` (giá đóng cửa nến cuối cùng)
  - `volume = sum(c.volume for c in bucket)` (tổng khối lượng toàn cụm)

**Tính chất bảo toàn bất biến:** Bởi vì `low <= min(c.low) <= min(c_0.open, c_{-1}.close)` và `high >= max(c.high) >= max(c_0.open, c_{-1}.close)`, cây nến tổng hợp **tự động thỏa mãn 100% bất biến `Candle`**.

### 3.4. `QuadTree` 2D — Crosshair Snapping & Truy vấn Không gian

Khi người dùng rê chuột trên biểu đồ (hover tooltip, crosshair nam châm hút vào giá Open/High/Low/Close hoặc các điểm đánh dấu kỹ thuật), ta cần tìm điểm gần con trỏ chuột nhất trong không gian 2D `(x, y)` hoặc truy vấn các đối tượng nằm trong một vùng chọn hình chữ nhật (`Bounds`).

**Hợp đồng API (`src/algorithms/quad_tree.py`):**
- `Bounds(x_min: float, y_min: float, x_max: float, y_max: float)`: hình chữ nhật giới hạn, hỗ trợ `contains(x, y)` và `intersects(other: Bounds)`.
- `SpatialPoint(x: float, y: float, payload: Any)`: điểm dữ liệu 2D mang payload (ví dụ index nến và giá).
- `QuadTree(bounds: Bounds, capacity: int = 4)`:
  - `insert(point: SpatialPoint) -> bool`: chèn điểm; nếu nút lá đầy (`len(points) >= capacity`) và chưa chia, gọi `subdivide()` tách thành 4 nút con `NW, NE, SW, SE`.
  - `query_range(rect: Bounds) -> list[SpatialPoint]`: cắt tỉa các nhánh có `not self.bounds.intersects(rect)`.
  - `nearest(x: float, y: float, max_dist: float) -> SpatialPoint | None`: thuật toán **Branch-and-Bound**.

```text
+-------------------+-------------------+
|       NW          |        NE         |
|  (x_min..mid_x,   |  (mid_x..x_max,   |
|   mid_y..y_max)   |   mid_y..y_max)   |
+-------------------+-------------------+  <-- mid_y
|       SW          |        SE         |
|  (x_min..mid_x,   |  (mid_x..x_max,   |
|   y_min..mid_y)   |   y_min..mid_y)   |
+-------------------+-------------------+
                    ^ mid_x
```

**Cơ chế Cắt tỉa Khoảng cách (Branch-and-Bound) cho `nearest(x, y, max_dist)`:**
1. Khởi tạo `best_dist = max_dist`, `best_point = None`.
2. Tính khoảng cách Euclid tối thiểu từ điểm truy vấn `(x, y)` tới hình chữ nhật bao `node.bounds`:
   `dx = max(b.x_min - x, 0.0, x - b.x_max)` và `dy = max(b.y_min - y, 0.0, y - b.y_max)`, suy ra `min_dist = hypot(dx, dy)`.
3. Nếu `min_dist > best_dist`, **cắt tỉa toàn bộ nhánh cây con** ngay lập tức (không đi vào!).
4. Nếu có 4 nút con, sắp xếp chúng theo `min_dist` tăng dần để duyệt nhánh có khả năng chứa điểm gần nhất trước $\implies$ thu hẹp `best_dist` cực nhanh và cắt bỏ đa số nhánh còn lại ($O(\log N)$ trung bình).

*(Lưu ý phòng chống đệ quy vô tận: Khi nhiều điểm trùng tọa độ chính xác, đặt thêm giới hạn chiều sâu tối đa `max_depth` hoặc kiểm tra kích thước hình chữ nhật tối thiểu trước khi `subdivide()`).*

### 3.5. Edge Cases & Bài tập Thực hành Từng bước (Thành viên 3)

**Edge Cases cần kiểm thử bắt buộc:**
- `SegmentTree([])` (cây rỗng): `query(0, 1)` trả `None`; `append` từ rỗng lên nhiều phần tử qua các ngưỡng lũy thừa của 2 ($1 \to 2 \to 4 \to 8 \to 16$).
- `SegmentTree.query(left, right)` khi `left >= right` hoặc vùng ngoài biên `[0, len)`.
- `LTTBDecimator.downsample` khi đường thẳng có 1 đỉnh gai (spike) cực lớn ở giữa một vùng phẳng — xác minh đỉnh gai đó BẮT BUỘC được giữ lại!
- `QuadTree` với nhiều điểm trùng tọa độ `(x, y)` vượt quá `capacity=4` (không bị `RecursionError`).

**Bài tập thực hành từng bước:**
- **Step 1:** Cài đặt `RangeStats`, `scan_range`, và `SegmentTree` (query nửa mở `[left, right)`, `update`, `append` với dynamic power-of-2 rebuild).
- **Step 2:** Viết property/randomized test trong `tests/test_segment_tree.py`: sinh 1,000 cặp `(left, right)` ngẫu nhiên xen kẽ `update` và `append`, đối chiếu 100% với oracle `scan_range`.
- **Step 3:** Cài đặt `LTTBDecimator.downsample` và `aggregate_ohlcv_buckets` trong `src/algorithms/lttb_decimator.py`; kiểm tra mọi cây nến tổng hợp đều thỏa mãn bất biến `Candle`.
- **Step 4:** Cài đặt `Bounds`, `SpatialPoint`, `QuadTree` (`insert`, `query_range`, `nearest`) và đối chiếu kết quả `nearest` với brute-force scan.
- **Step 5:** Chạy `pytest tests/test_segment_tree.py tests/test_lttb.py -v` đạt 100% pass.

---

## CHƯƠNG 4 — THÀNH VIÊN 4 (25%): TEAM LEAD, PYQT6 UI & SYSTEM INTEGRATION OWNER

**Phạm vi files:**
- `src/patterns/observer.py`
- `src/patterns/command_history.py`
- `src/ui/chart_canvas.py`
- `src/ui/main_window.py`
- `src/main.py`
- `tests/test_integration.py`
- `.github/workflows/python-tests.yml`

### 4.1. Observer Pattern — `EventBus` (`src/patterns/observer.py`)

Trong một ứng dụng tương tác nhiều thành phần (Replay Timer, Toolbar, Chart Canvas, Status Bar), nếu các module gọi trực tiếp phương thức của nhau sẽ tạo ra **sự phụ thuộc vòng (circular dependencies)** và cực khó viết unit test độc lập. `EventBus` thực thi **Observer Pattern** (Publish-Subscribe) để tách rời hoàn toàn bên phát sự kiện và bên lắng nghe:

**Hợp đồng API (`EventBus`):**
- `subscribe(event_name: str, callback: Callable[[Any], None]) -> None` (tránh đăng ký trùng lặp cùng một callback trên cùng event).
- `unsubscribe(event_name: str, callback: Callable[[Any], None]) -> None` (an toàn nếu callback không tồn tại).
- `publish(event_name: str, payload: Any = None) -> None` (duyệt trên bản sao `list(self._subscribers[event_name])` để không gặp lỗi `RuntimeError` nếu một listener tự `unsubscribe` ngay trong callback!).

### 4.2. Command Pattern — `CommandHistory` (`src/patterns/command_history.py`)

Mỗi thao tác làm thay đổi trạng thái khung nhìn của người dùng (Pan, Zoom, Reset View) được đóng gói thành một đối tượng `Command` bất biến lịch sử, giúp cài đặt **Undo / Redo** sạch sẽ:

**Hợp đồng API:**
- `Command(ABC)`:
  - `execute() -> None` (abstract)
  - `undo() -> None` (abstract)
  - `description: str` (property mô tả lệnh, ví dụ `"Zoom in"` / `"Pan chart"`)
- `ViewportChangeCommand(apply_fn: Callable[[ViewportState], None], old_viewport: ViewportState, new_viewport: ViewportState, description: str = "Viewport Change")`: lưu callback áp dụng trạng thái `apply_fn`, trạng thái trước (`old_viewport: ViewportState`), và trạng thái sau (`new_viewport: ViewportState`).
- `CommandHistory(max_size: int = 100)`:
  - `execute(cmd: Command) -> None`: gọi `cmd.execute()`, đẩy vào `undo_stack`, **xóa trắng `redo_stack`**, và nếu `len(undo_stack) > max_size` thì loại bỏ lệnh cũ nhất ở đáy stack (ngăn rò rỉ bộ nhớ).
  - `undo() -> Command | None`: lấy từ `undo_stack`, gọi `cmd.undo()`, đẩy sang `redo_stack`, trả về `cmd` (hoặc `None` nếu rỗng).
  - `redo() -> Command | None`: lấy từ `redo_stack`, gọi `cmd.execute()`, đẩy lại vào `undo_stack`, trả về `cmd` (hoặc `None` nếu rỗng).
  - `can_undo() -> bool`, `can_redo() -> bool`, `clear() -> None`, `__len__() -> int`.

### 4.3. PyQt6 Rendering Pipeline (`ChartCanvasWidget` & `MainWindow`)

#### 4.3.1. Kiến trúc Headless Compute vs Paint (`src/ui/chart_canvas.py`)

Một lỗi phổ biến của lập trình viên GUI là viết toàn bộ phép tính toán toán học, truy vấn thuật toán, và biến đổi tọa độ ngay bên trong hàm `QWidget.paintEvent(self, event)`. Cách làm đó khiến **không thể viết unit test chạy trên server CI không có màn hình** và dễ gây giật khung hình.

**Kiến trúc chuẩn của dự án tách thành 2 bước rõ ràng:**
1. **`ChartCanvasWidget.compute_visible_frame(self, width_px: int | None = None, height_px: int | None = None, max_render_candles: int = 300) -> VisibleFrame` (Pure Python / Headless):**
   - Nhận kích thước khung vẽ tùy chọn (`width_px`, `height_px`) và giới hạn số nến vẽ tối đa `max_render_candles` (mặc định `300`; ném `ValueError` nếu `< 1`).
   - Gọi `SegmentTree.query(start_idx, end_idx + 1)` lấy `RangeStats(min_low, max_high, volume_sum)` để auto-fit trục $Y$.
   - Khi `vis_count > max_render_candles`, gọi `aggregate_ohlcv_buckets(...)` để giảm số nến hiển thị về tối đa `max_render_candles` cây nến.
   - Tính toán các chỉ báo (`SlidingWindowIndicators.sma`, `donchian_channels`) và dùng `LTTBDecimator.downsample()` cho đường giá đóng cửa `decimated_close_points`.
   - Dùng `CoordinateTransformer` ánh xạ toàn bộ tọa độ World $\to$ Screen `(x, y)` và dựng `QuadTree` trên các nến hiển thị để phục vụ `mouseMoveEvent` snap crosshair tức thời.
   - Trả về **`VisibleFrame`** (`@dataclass(frozen=True)`) chứa đúng 12 trường: `viewport`, `range_stats`, `render_candles`, `candle_indices`, `sma_points`, `donchian_upper`, `donchian_middle`, `donchian_lower`, `decimated_close_points`, `total_candles`, `start_idx`, `end_idx`.
2. **`paintEvent(self, event)` (Pure `QPainter`):**
   - Khởi tạo `painter = QPainter(self)`, bật `QPainter.RenderHint.Antialiasing` cho đường chỉ báo mượt mà.
   - Thiết lập `painter.setClipRect(plot_rect)` để nến không bị vẽ tràn vào vùng padding nhãn giá bên phải.
   - Vẽ lưới nền (gridlines), vẽ râu nến (`drawLine`) và thân nến (`fillRect`: xanh `#26a69a` khi `close >= open`, đỏ `#ef5350` khi `close < open`), vẽ đường SMA/Donchian/Volume, tắt clip và vẽ trục giá, trục thời gian, crosshair và tooltip.

#### 4.3.2. `MainWindow` & `src/main.py`

- **`MainWindow` (`src/ui/main_window.py`):** Kế thừa `QMainWindow`, chứa `ChartCanvasWidget` làm `centralWidget`, kết hợp `QTimer` điều khiển **Replay Loop** (nút Play/Pause, Reset, lựa chọn tốc độ Replay), hộp kiểm bật/tắt các chỉ báo (SMA, Donchian Channels, Volume), nút Undo/Redo kết nối `CommandHistory`, nút Reload CSV (`QFileDialog`), và `QStatusBar` hiển thị giá trị OHLCV tại vị trí crosshair cùng `RangeStats` vùng nhìn thấy.
- **Entry Point (`src/main.py`):** Các hàm `build_parser() -> argparse.ArgumentParser`, `main(argv: Sequence[str] | None = None) -> int`, `run_cli(...)`, `run_benchmark(...)`, `run_gui(...)` phân tích đối số dòng lệnh chuẩn:
  `python3 -m src.main [--cli | --benchmark | --gui] [--csv data/sample_ohlcv.csv] [--count 10000] [--capacity 256] [--window 20]`
  - `--cli`: Nạp hoặc sinh dữ liệu, chạy toàn bộ pipeline headless (`RingBuffer`, `SegmentTree`, `SlidingWindowIndicators`, `LTTBDecimator`) và in báo cáo tóm tắt ra stdout.
  - `--benchmark`: Đo hiệu năng trên tập dữ liệu lớn (mặc định `--count 10000`, `--capacity 256`, `--window 20`), đối chiếu `SlidingWindowIndicators` vs naive $O(N \cdot W)$ và `SegmentTree` vs `scan_range` qua `time.perf_counter()` và `tracemalloc`.
  - `--gui` (mặc định nếu không truyền `--cli`/`--benchmark`): Khởi tạo `QApplication`, hiển thị `MainWindow`.

### 4.4. Kiểm thử Headless & Benchmarking (`pytest`, `perf_counter`, `tracemalloc`)

1. **Headless GUI Testing trong CI (`.github/workflows/python-tests.yml`):**
   - Trên máy chủ GitHub Actions Linux không có màn hình, đặt biến môi trường `QT_QPA_PLATFORM=offscreen` để PyQt6 chạy mượt mà các test kiểm tra `ChartCanvasWidget` / `MainWindow`, hoặc test trực tiếp `compute_visible_frame()` mà không cần khởi tạo X11.
2. **Đo độ trễ khung hình bằng `time.perf_counter()`:**
   - Luôn dùng `time.perf_counter()` (đồng hồ đơn điệu độ phân giải nano-giây) thay vì `time.time()` (có thể bị nhảy lùi khi NTP đồng bộ giờ hệ thống).
   - Thu thập mảng thời gian các khung hình, sắp xếp và tính p50 (trung vị), p95, p99 để chắc chắn $p99 \le 16.67\text{ ms}$.
3. **Kiểm toán Bộ nhớ bằng `tracemalloc`:**
   - Chạy `tracemalloc.start()`, đẩy $100{,}000$ nến liên tiếp vào `RingBuffer(capacity=5000)`, gọi `tracemalloc.get_traced_memory()` để chứng minh bộ nhớ giữ ở mức ổn định (plateau) thay vì tăng tuyến tính.

### 4.5. Edge Cases & Bài tập Thực hành Từng bước (Thành viên 4)

**Edge Cases cần kiểm thử bắt buộc:**
- `EventBus`: một callback tự gọi `unsubscribe` chính nó khi đang `publish`.
- `CommandHistory`: thực thi $150$ lệnh liên tiếp với `max_size=100` $\implies$ chỉ giữ đúng $100$ lệnh mới nhất; thực thi lệnh mới sau khi `undo()` phải xóa sạch nhánh `redo`.
- `ChartCanvasWidget.compute_visible_frame()` với danh sách nến rỗng `[]` hoặc chỉ có 1 cây nến duy nhất (`start_idx == 0, end_idx == 1`).
- Chế độ `--cli` và `--benchmark` trên file CSV mẫu và dữ liệu tổng hợp chạy sạch với exit code `0`.

**Bài tập thực hành từng bước:**
- **Step 1:** Cài đặt `src/patterns/observer.py` (`EventBus`) và `src/patterns/command_history.py` (`Command`, `ViewportChangeCommand`, `CommandHistory`).
- **Step 2:** Thiết kế `compute_visible_frame()` trong `src/ui/chart_canvas.py` kết nối `SegmentTree`, `aggregate_ohlcv_buckets`, `SlidingWindowIndicators`, `LTTBDecimator`, `QuadTree`, và `CoordinateTransformer`.
- **Step 3:** Cài đặt `paintEvent(QPainter)` và các sự kiện chuột (`wheelEvent` cho cursor-anchored zoom, `mousePressEvent`/`mouseMoveEvent` cho pan & crosshair snapping).
- **Step 4:** Cài đặt `MainWindow` với `QTimer` replay, indicator toggles, Undo/Redo, CSV reload; hoàn thiện `src/main.py` với `--cli`, `--benchmark`, `--gui`.
- **Step 5:** Viết `tests/test_integration.py` và cấu hình `.github/workflows/python-tests.yml`; chạy `pytest -v`, `python3 -m src.main --cli`, `python3 -m src.main --benchmark`.

---

## PHỤ LỤC — DANH MỤC TÀI LIỆU THAM KHẢO CHÍNH THỨC

Toàn bộ lý thuyết và triển khai trong dự án tham chiếu tới các nguồn tài liệu học thuật và kỹ thuật chính thức sau:

1. **Circular Buffer / Ring Buffer:**
   - Wikipedia — Circular buffer: https://en.wikipedia.org/wiki/Circular_buffer
2. **Python Core Data Structures, Validation & Profiling:**
   - Python `dataclasses`: https://docs.python.org/3/library/dataclasses.html
   - Python `csv` module: https://docs.python.org/3/library/csv.html
   - Python `collections.deque` (đối chiếu để hiểu lý do tự cài đặt): https://docs.python.org/3/library/collections.html#collections.deque
   - Python `time.perf_counter`: https://docs.python.org/3/library/time.html#time.perf_counter
   - Python `tracemalloc`: https://docs.python.org/3/library/tracemalloc.html
3. **Monotonic Queue & Sliding Window Algorithms:**
   - CP-Algorithms — Minimum stack / Minimum queue: https://cp-algorithms.com/data_structures/stack_queue_minimum.html
   - USACO Guide — Sliding Window: https://usaco.guide/gold/sliding-window
4. **Segment Tree (Range Queries):**
   - CP-Algorithms — Segment Tree: https://cp-algorithms.com/data_structures/segment_tree.html
   - USACO Guide — Point Update Range Sum / Segment Tree: https://usaco.guide/gold/segtree
5. **Time-Series Downsampling (LTTB):**
   - Sveinn Steinarsson (2013), *Downsampling Time Series for Visual Representation* (MS Thesis PDF): https://skemman.is/bitstream/1946/15343/3/SS_MSthesis.pdf
   - University of Iceland Skemman Repository Handle: http://hdl.handle.net/1946/15343
6. **Financial Charting Architecture:**
   - TradingView Lightweight Charts Official Docs: https://tradingview.github.io/lightweight-charts/
7. **PyQt6 / Qt 6 Rendering & Timers:**
   - Qt 6 `QPainter`: https://doc.qt.io/qt-6/qpainter.html
   - Qt 6 `QWidget`: https://doc.qt.io/qt-6/qwidget.html
   - Qt 6 `QTimer`: https://doc.qt.io/qt-6/qtimer.html
8. **Software Design Patterns:**
   - Refactoring.Guru — Observer Pattern: https://refactoring.guru/design-patterns/observer
   - Refactoring.Guru — Command Pattern: https://refactoring.guru/design-patterns/command
9. **Testing Framework:**
   - Pytest Official Documentation: https://docs.pytest.org/
