# Báo cáo Phân tích Kỹ thuật & Phân bổ Khối lượng Công việc (25% – 25% – 25% – 25%)

- **Tên đồ án:** Interactive TradingView Stock Chart Engine (DSA Python)
- **Thời gian thực hiện:** 16/11/2026 – 27/12/2026 (6 tuần / M1–M6)
- **Công nghệ sử dụng:** Python 3.10+ (đã kiểm chứng trên Python 3.14.9), PyQt6 (`PyQt6>=6.6.0`, custom `QPainter` widget), `pytest>=8.0.0` (đã kiểm chứng trên pytest 9.2.0)
- **Quy mô nhóm:** 4 thành viên — Phân bổ đồng đều **25% – 25% – 25% – 25%**
- **Kiến trúc & Trạng thái Starter Boilerplate:** Tham khảo sơ đồ UML đầy đủ tại [docs/UML_ARCHITECTURE.md](UML_ARCHITECTURE.md) và khế ước API tại [docs/interfaces.md](interfaces.md). Toàn bộ hàm/phương thức trong `src/` và `tests/` là bộ khung skeleton (`pass` + hướng dẫn từng bước) cho 4 thành viên tự triển khai qua các cột mốc M1–M6.

---

## 1. Tóm tắt Mục tiêu Học thuật & Kỹ thuật

Đồ án hướng tới việc thiết kế và tự cài đặt hoàn chỉnh một **Engine vẽ biểu đồ chứng khoán tương tác theo phong cách TradingView** viết bằng Python thuần kết hợp PyQt6. Khác với các ứng dụng thông thường chỉ gọi thư viện đồ thị đóng gói sẵn (`matplotlib`, `pyqtgraph`), trọng tâm học thuật của đồ án nằm ở việc **cài đặt từ đầu các cấu trúc dữ liệu và giải thuật kinh điển** để giải quyết các bài toán hiệu năng thực tế trong tài chính định lượng:

1. **Quản lý luồng dữ liệu thời gian thực có giới hạn bộ nhớ** bằng Mảng vòng cố định `RingBuffer` ($O(1)$ ghi đè, **không dùng `collections.deque`**).
2. **Tính toán chỉ báo kỹ thuật trên cửa sổ trượt** bằng Hàng đợi hai đầu tự mở rộng `CircularDeque` (**không dùng `collections.deque`**) và Hàng đợi đơn điệu `MonotonicDeque` ($O(1)$ amortized cho cực trị trượt).
3. **Truy vấn thống kê vùng nhìn thấy (Viewport Range Query)** tức thời bằng Cây phân đoạn động `SegmentTree` ($O(\log N)$ cho `min_low`, `max_high`, `volume_sum` trên khoảng nửa mở `[left, right)`).
4. **Nén chuỗi thời gian theo nhận thức thị giác & tìm kiếm không gian 2D** bằng thuật toán Largest-Triangle-Three-Buckets (`LTTBDecimator`), gộp nến `aggregate_ohlcv_buckets`, và cây tứ phân `QuadTree` cho bắt điểm crosshair.
5. **Tách biệt kiến trúc giao diện** thông qua Design Patterns (`Observer/EventBus`, `Command/CommandHistory`) và cơ chế `compute_visible_frame()` headless cho phép kiểm thử toàn diện trên CI/CD không cần màn hình đồ họa.

---

## 2. Cơ sở Phân tích Độ phức tạp Giải thuật

| Bài toán trong Chart Engine | Giải pháp Naive (Vét cạn) | Giải pháp DSA trong Đồ án | Cải thiện Độ phức tạp |
|---|---|---|---|
| Lưu trữ $K$ nến gần nhất & cập nhật nến mới | `list.pop(0)` + `append` ($O(K)$ dịch bộ nhớ) | `RingBuffer` mảng vòng cố định | **$O(1)$** push, **$O(K)$** snapshot |
| Tìm Min/Max cửa sổ trượt $W$ (Donchian, Rolling Min/Max) | Duyệt lại $W$ phần tử tại mỗi bước ($O(N \cdot W)$) | `MonotonicDeque` trên `CircularDeque` tự resize 2x | **$O(N)$** toàn chuỗi ($O(1)$ amortized/bước) |
| Tìm `min_low`, `max_high`, `volume_sum` khi pan/zoom | `scan_range` quét tuyến tính ($O(N)$ mỗi khung hình) | `SegmentTree` nửa mở `[left, right)` | **$O(\log N)$** query & point update |
| Vẽ $10,000$–$100,000$ điểm lên chiều rộng $1,200$ px | Vẽ toàn bộ điểm gây nghẽn `QPainter` ($O(N)$ vẽ) | `LTTBDecimator` / `aggregate_ohlcv_buckets` | Giữ hình dạng đỉnh/đáy với **$\le M$ điểm vẽ** |
| Tìm nến gần con trỏ chuột (Crosshair snapping) | Quét Euclid toàn bộ điểm đang hiện ($O(M)$ mỗi mouse move) | `QuadTree` 2D phân vùng + cắt tỉa nhánh | **$O(\log M)$** trung bình cho `nearest` |

---

## 3. Phân tích Phân bổ Khối lượng Công việc 25% – 25% – 25% – 25%

Để bảo đảm tính công bằng tuyệt đối trong đánh giá môn học và phân tách rạch ròi trách nhiệm kỹ thuật (Single Ownership), khối lượng công việc của cả 6 tuần (M1–M6) được chia thành **4 gói công việc độc lập có độ phức tạp tương đương (mỗi thành viên 25%)**:

### 3.1 Thành viên 1 — Data Engineer & Ring Buffer Owner (25%)
- **Trách nhiệm cốt lõi:** Toàn bộ vòng đời dữ liệu đầu vào, kiểm định tính hợp lệ tài chính của nến OHLCV, bộ đệm vòng thời gian thực và trình giả lập/phát lại dữ liệu.
- **Thành phần phụ trách:**
  1. `Candle` (`src/core/candle.py`): Frozen dataclass kèm invariant kiểm tra `math.isfinite`, `volume >= 0`, `low <= min(open, close)`, `high >= max(open, close)`.
  2. `csv_loader` (`src/core/csv_loader.py`): `parse_candle_row` và `load_candles` kiểm soát timestamp tăng nghiêm ngặt, báo lỗi `ValueError` kèm số dòng `line_num`, xử lý file rỗng/header-only.
  3. `RingBuffer` (`src/core/ring_buffer.py`): Cài đặt mảng vòng cố định từ đầu (**không dùng `collections.deque`**) với $O(1)$ `push`, $O(K)$ `get_all`, `latest`, `__len__`, `is_full`, `clear`.
  4. `data_simulator` (`src/core/data_simulator.py`) & `data/sample_ohlcv.csv`: Bộ sinh dữ liệu tất định `generate_synthetic_candles` và `ReplayDataSource` hỗ trợ cập nhật nến đang chạy (`replace_or_append`).
  5. Kiểm thử (`tests/test_ring_buffer.py`): Bao phủ toàn bộ validation, wrap-around, replay và kiểm tra cấm dùng `collections.deque`.
- **Đóng góp theo tuần (M1–M6):** Khóa `Candle`/`csv_loader` (M1) $\to$ Hoàn tất `RingBuffer`/`data_simulator`/CSV mẫu (M2) $\to$ Tối ưu nạp dữ liệu lớn (M3) $\to$ Hoàn tất `test_ring_buffer.py` (M4) $\to$ Memory/speed profiling luồng dữ liệu (M5) $\to$ Tài liệu & Demo phần 1 (M6).

### 3.2 Thành viên 2 — Sliding Window Analytics & Coordinate Math Owner (25%)
- **Trách nhiệm cốt lõi:** Cấu trúc dữ liệu hàng đợi hai đầu tự cài đặt, toàn bộ bộ chỉ báo phân tích kỹ thuật cửa sổ trượt $O(N)$ và hệ quy chiếu toán học màn hình.
- **Thành phần phụ trách:**
  1. `CircularDeque` (`src/algorithms/monotonic_deque.py`): Tự cài đặt mảng vòng hai đầu với tự động mở rộng kích thước $2\times$ (**không dùng `collections.deque`**), ném `IndexError` khi rỗng.
  2. `MonotonicDeque` (`src/algorithms/monotonic_deque.py`): Duy trì bất biến đơn điệu `'min'`/`'max'` trong $O(1)$ amortized.
  3. `SlidingWindowIndicators` (`src/algorithms/monotonic_deque.py`): 5 chỉ báo chuẩn tài chính chạy trong $O(N)$ (`rolling_min_max`, `sma`, `ema`, `donchian_channels`, `bollinger_bands`).
  4. `ViewportState` & `CoordinateTransformer` (`src/core/coordinate_math.py`): Ánh xạ Affine 2 chiều (`index_to_x`, `x_to_index`, `price_to_y`, `y_to_price`, `world_to_screen`, `screen_to_world`), thuật toán `zoom_at_pixel` bảo toàn điểm neo con trỏ và `pan_by_pixels`.
  5. Kiểm thử (`tests/test_monotonic_deque.py`): Kiểm chứng `CircularDeque` 2x resize, đối chiếu `MonotonicDeque` & 5 chỉ báo với brute-force, kiểm chứng độ chính xác khả nghịch của phép biến đổi tọa độ.
- **Đóng góp theo tuần (M1–M6):** Skeleton `CircularDeque` & `ViewportState` (M1) $\to$ Hoàn tất `CircularDeque`, `MonotonicDeque` & 5 chỉ báo (M2) $\to$ Hoàn tất `CoordinateTransformer` (M3) $\to$ Hoàn tất `test_monotonic_deque.py` (M4) $\to$ Profiling chỉ báo & tinh chỉnh biên zoom (M5) $\to$ Tài liệu & Demo phần 2 (M6).

### 3.3 Thành viên 3 — Range Query & Decimation Algorithms Owner (25%)
- **Trách nhiệm cốt lõi:** Truy vấn khoảng đoạn động trên chuỗi nến, thuật toán nén chuỗi thời gian bảo toàn hình dáng/OHLCV và chỉ mục không gian 2D.
- **Thành phần phụ trách:**
  1. `RangeStats`, `SegmentTree` & `scan_range` (`src/algorithms/segment_tree.py`): Cây phân đoạn hỗ trợ nửa mở `[left, right)` trong $O(\log N)$, point `update`, `append` tự động mở rộng dung lượng power-of-2, kèm hàm đối chiếu `scan_range` oracle.
  2. `LTTBDecimator` & `aggregate_ohlcv_buckets` (`src/algorithms/lttb_decimator.py`): Giảm mẫu tuyến tính bảo toàn đỉnh/đáy (LTTB) và gộp nến theo bucket pixel bảo toàn chuẩn OHLCV.
  3. `QuadTree`, `Bounds`, `SpatialPoint` (`src/algorithms/quad_tree.py`): Cây tứ phân chia 4 góc phần tư (`insert`, `query_range`, `nearest`) phục vụ bắt điểm nến nhanh.
  4. Kiểm thử (`tests/test_segment_tree.py`, `tests/test_lttb.py`): Differential testing hàng trăm truy vấn ngẫu nhiên giữa `SegmentTree` và `scan_range`, kiểm thử LTTB, gộp OHLC và truy vấn `QuadTree`.
- **Đóng góp theo tuần (M1–M6):** Skeleton `SegmentTree` (M1) $\to$ Hoàn tất `SegmentTree` & `scan_range` (M2) $\to$ Hoàn tất `LTTBDecimator`, `aggregate_ohlcv_buckets` & `QuadTree` (M3) $\to$ Hoàn tất `test_segment_tree.py` & `test_lttb.py` (M4) $\to$ Benchmark `SegmentTree` vs `scan_range` (M5) $\to$ Tài liệu & Demo phần 3 (M6).

### 3.4 Thành viên 4 — Team Lead, PyQt6 UI & System Integration Owner (25%)
- **Trách nhiệm cốt lõi:** Kiến trúc mẫu thiết kế giao tiếp, bộ vẽ đồ họa tùy biến PyQt6, cửa sổ tương tác chính, điểm vào CLI/Benchmark/GUI và quản trị chất lượng CI/CD.
- **Thành phần phụ trách:**
  1. `EventBus` (`src/patterns/observer.py`): Hệ thống sự kiện Observer tách rời UI và trạng thái ứng dụng.
  2. `Command`, `ViewportChangeCommand`, `CommandHistory` (`src/patterns/command_history.py`): Cơ chế Undo/Redo tối đa `max_size=100` thao tác pan/zoom.
  3. `ChartCanvasWidget` (`src/ui/chart_canvas.py`): Widget PyQt6 tùy biến sử dụng `QPainter`, sở hữu `compute_visible_frame()` chạy độc lập headless kết nối 3 tầng thuật toán trên.
  4. `MainWindow` (`src/ui/main_window.py`) & `src/main.py`: Giao diện đầy đủ `QTimer` Replay (Play/Pause/Reset/Speed), Indicator Toggles, Undo/Redo, CSV Reload, Status bar, cùng CLI flags `--cli`, `--benchmark`, `--gui`, `--csv`, `--count`.
  5. Tích hợp & CI/CD (`tests/test_integration.py`, `.github/workflows/python-tests.yml`): Kiểm thử End-to-End và kiểm duyệt toàn bộ PR trên GitHub.
- **Đóng góp theo tuần (M1–M6):** Setup repo, CI, Contracts & Skeleton UI (M1) $\to$ Hoàn tất `EventBus` & `CommandHistory` (M2) $\to$ Hoàn tất `ChartCanvasWidget` (`QPainter` + `compute_visible_frame()`) (M3) $\to$ Hoàn tất `MainWindow` (M4) $\to$ Hoàn tất `test_integration.py` & `--cli`/`--benchmark` (M5) $\to$ Tổng rà soát đồng bộ & Demo cuối kỳ (M6).

---

## 4. Tổng hợp Định lượng Cân bằng Khối lượng (25% × 4)

| Tiêu chí đánh giá | Thành viên 1 | Thành viên 2 | Thành viên 3 | Thành viên 4 |
|---|---|---|---|---|
| **Tỷ trọng chính thức** | **25%** | **25%** | **25%** | **25%** |
| **Số lượng Component (`DAG_MANIFEST`)** | 4 components (`Candle`, `csv_loader`, `RingBuffer`, `data_simulator`) | 4 components (`CircularDeque`, `MonotonicDeque`, `SlidingWindowIndicators`, `CoordinateTransformer`/`ViewportState`) | 3 components sâu (`SegmentTree`+`RangeStats`+`scan_range`, `LTTBDecimator`+`aggregate_ohlcv_buckets`, `QuadTree`+`Bounds`+`SpatialPoint`) | 3 components tích hợp lớn (`EventBus`, `CommandHistory`, `ChartCanvasWidget`+`MainWindow`) + `main.py` + CI |
| **Độ khó DSA / Kỹ thuật** | Validation bất biến tài chính, I/O an toàn theo dòng, Circular Array $O(1)$ | Circular Array 2x resize, Monotonic Queue $O(1)$, 5 chỉ báo $O(N)$, Affine Geometry | Dynamic power-of-2 Segment Tree $O(\log N)$, LTTB hình học, 2D QuadTree | Observer & Command Undo/Redo, Custom `QPainter`, Headless Frame Engine, CI/CD & CLI/Benchmark |
| **Bộ Test chuyên trách** | `tests/test_ring_buffer.py` | `tests/test_monotonic_deque.py` | `tests/test_segment_tree.py`, `tests/test_lttb.py` | `tests/test_integration.py` + GitHub Actions CI |
| **Số tuần tham gia tích cực** | M1 – M6 (6/6 tuần) | M1 – M6 (6/6 tuần) | M1 – M6 (6/6 tuần) | M1 – M6 (6/6 tuần) |

---

## 5. Lệnh Kiểm chứng Chính thức cho Hội đồng Đánh giá

Khi chấm điểm hoặc tái lập kết quả trên môi trường **Python 3.10+** (đã xác nhận tương thích **Python 3.14.9** và **pytest 9.2.0**), sử dụng chính xác bộ lệnh sau:

```bash
# 1. Cài đặt môi trường
pip install -r requirements.txt

# 2. Chạy toàn bộ bộ kiểm thử đơn vị và tích hợp
pytest -v

# 3. Kiểm thử luồng xử lý dữ liệu & tính toán ở chế độ dòng lệnh (Headless)
python3 -m src.main --cli

# 4. Chạy bộ đo hiệu năng thời gian & bộ nhớ (perf_counter + tracemalloc)
python3 -m src.main --benchmark

# 5. Khởi chạy ứng dụng giao diện tương tác PyQt6
python3 -m src.main
```

Cú pháp tùy biến dữ liệu và số lượng nến đầu vào:
```bash
python3 -m src.main [--cli | --benchmark | --gui] [--csv data/sample_ohlcv.csv] [--count 10000]
```
