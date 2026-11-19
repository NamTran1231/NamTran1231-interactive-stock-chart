# Kế hoạch Thực hiện, Phân công & Deadline Chi tiết (M1–M6)

- **Dự án:** Interactive TradingView Stock Chart Engine (DSA Python)
- **Thời gian thực hiện:** 16/11/2026 – 27/12/2026 (6 tuần / 6 Milestones)
- **Cơ cấu nhân sự:** 4 Thành viên — Phân bổ khối lượng công việc đồng đều **25% – 25% – 25% – 25%**
- **Môi trường chuẩn:** Python 3.10+ (đã kiểm chứng trên Python 3.14.9), `PyQt6>=6.6.0` (custom `QPainter` widget), `pytest>=8.0.0` (đã kiểm chứng trên pytest 9.2.0)
- **Kiến trúc & Starter Skeleton:** Toàn bộ `src/` và `tests/` được khởi tạo sẵn ở dạng **Skeleton (`pass` + docstring hướng dẫn từng bước)** khớp 100% với [docs/interfaces.md](docs/interfaces.md) và sơ đồ kiến trúc tại [docs/UML_ARCHITECTURE.md](docs/UML_ARCHITECTURE.md) để thành viên tự code toàn bộ phần DSA & UI.

---

## Bảng Tổng hợp Lịch trình 6 Tuần (M1–M6)

| Milestone | Thời gian | Deadline | Trọng tâm kỹ thuật | Người điều phối chính |
|---|---|---|---|---|
| **M1** | 16/11/2026 – 22/11/2026 | **22/11/2026** | Setup repo, CI/CD, API Contracts, `Candle`, `csv_loader`, `RingBuffer` core, skeleton `CircularDeque`/`SegmentTree`/`MainWindow` | Thành viên 4 (Team Lead) & Thành viên 1 |
| **M2** | 23/11/2026 – 29/11/2026 | **29/11/2026** | `RingBuffer` + `data_simulator` + `sample_ohlcv.csv`; `CircularDeque` + `MonotonicDeque` + Indicators; `SegmentTree` + `scan_range` oracle; `EventBus` + `CommandHistory` | Cả 4 thành viên (phát triển song song lõi DSA) |
| **M3** | 30/11/2026 – 06/12/2026 | **06/12/2026** | `CoordinateTransformer` (Affine + Zoom/Pan); `LTTBDecimator` + `aggregate_ohlcv_buckets` + `QuadTree`; `ChartCanvasWidget` (`QPainter` + `compute_visible_frame()`) | Thành viên 2, Thành viên 3 & Thành viên 4 |
| **M4** | 07/12/2026 – 13/12/2026 | **13/12/2026** | Tích hợp `MainWindow` (`QTimer` Replay, toggles, Undo/Redo, CSV reload), Unit Test Suites hoàn chỉnh cho cả 4 thành viên | Thành viên 4 (UI) & Toàn nhóm (Unit Tests) |
| **M5** | 14/12/2026 – 20/12/2026 | **20/12/2026** | `tests/test_integration.py`, CLI & Benchmark (`--cli`, `--benchmark`), Memory/Performance profiling (`tracemalloc`, `time.perf_counter`), Bug fix & Polish | Thành viên 4 & Toàn nhóm (Profiling) |
| **M6** | 21/12/2026 – 27/12/2026 | **27/12/2026** | Tài liệu học thuật & báo cáo hoàn chỉnh, CI GitHub Actions 100% Pass, Đóng gói & Demo cuối kỳ | Toàn nhóm (Thành viên 4 tổng hợp bàn giao) |

---

## Phân công Nhân sự Cố định (25% – 25% – 25% – 25%)

- **Thành viên 1 — Data Engineer & Ring Buffer Owner (25%):** `src/core/candle.py`, `src/core/csv_loader.py`, `src/core/ring_buffer.py`, `src/core/data_simulator.py`, `data/sample_ohlcv.csv`, `tests/test_ring_buffer.py`.
- **Thành viên 2 — Sliding Window Analytics & Coordinate Math Owner (25%):** `src/algorithms/monotonic_deque.py` (`CircularDeque`, `MonotonicDeque`, `SlidingWindowIndicators`), `src/core/coordinate_math.py` (`ViewportState`, `CoordinateTransformer`), `tests/test_monotonic_deque.py`.
- **Thành viên 3 — Range Query & Decimation Algorithms Owner (25%):** `src/algorithms/segment_tree.py` (`RangeStats`, `SegmentTree`, `scan_range`), `src/algorithms/lttb_decimator.py` (`LTTBDecimator`, `aggregate_ohlcv_buckets`), `src/algorithms/quad_tree.py` (`Bounds`, `SpatialPoint`, `QuadTree`), `tests/test_segment_tree.py`, `tests/test_lttb.py`.
- **Thành viên 4 — Team Lead, PyQt6 UI & System Integration Owner (25%):** `src/patterns/observer.py`, `src/patterns/command_history.py`, `src/ui/chart_canvas.py`, `src/ui/main_window.py`, `src/main.py`, `tests/test_integration.py`, `.github/workflows/python-tests.yml`, quản trị PR & CI/CD.

---

## Chi tiết Từng Milestone (M1 – M6)

### Milestone 1 (M1): Khởi tạo Kiến trúc, CI/CD, Data Contracts & Core Foundation
- **Thời gian:** 16/11/2026 – 22/11/2026
- **Ngày Deadline:** **22/11/2026 (23:59)**
- **Mục tiêu:** Thiết lập khung dự án chuẩn, tự động hóa kiểm thử GitHub Actions, khóa cứng khế ước API 14 thành phần tại `docs/interfaces.md`, hoàn thiện mô hình dữ liệu gốc `Candle`, bộ đọc `csv_loader`, lõi `RingBuffer` và skeleton cho các module giải thuật/UI.
- **Người chịu trách nhiệm chính:** **Thành viên 4** (chịu trách nhiệm setup repo, CI/CD, API contracts & `MainWindow` skeleton) và **Thành viên 1** (chịu trách nhiệm khóa chuẩn dữ liệu `Candle` & `csv_loader`).

#### Task chi tiết theo từng thành viên
- **Thành viên 1 (Data Engineer & Ring Buffer Owner):**
  - Cài đặt `Candle` frozen dataclass tại `src/core/candle.py` với đầy đủ kiểm tra bất biến (`math.isfinite`, `volume >= 0`, `low <= min(open, close)`, `high >= max(open, close)`), ném `ValueError` khi vi phạm.
  - Cài đặt `parse_candle_row(row, line_num)` và `load_candles(path)` tại `src/core/csv_loader.py` (kiểm tra timestamp tăng nghiêm ngặt, báo lỗi `ValueError` kèm `line_num`, trả `[]` khi file rỗng/chỉ có header).
  - Khởi tạo core `RingBuffer(capacity)` tại `src/core/ring_buffer.py` với mảng vòng cố định (**tuyệt đối không dùng `collections.deque`**).
- **Thành viên 2 (Sliding Window Analytics & Coordinate Math Owner):**
  - Rà soát và đồng ký khế ước API cho `CircularDeque`, `MonotonicDeque`, `SlidingWindowIndicators`, `ViewportState`, `CoordinateTransformer`.
  - Tạo skeleton chuẩn signatures + docstrings + type hints cho `CircularDeque` trong `src/algorithms/monotonic_deque.py` và `ViewportState` trong `src/core/coordinate_math.py`.
- **Thành viên 3 (Range Query & Decimation Algorithms Owner):**
  - Rà soát và đồng ký khế ước API cho `RangeStats`, `SegmentTree`, `scan_range`, `LTTBDecimator`, `aggregate_ohlcv_buckets`, `QuadTree`.
  - Tạo skeleton chuẩn signatures + docstrings + type hints cho `SegmentTree` trong `src/algorithms/segment_tree.py` (xác định rõ nửa mở `[left, right)` và node đơn vị `RangeStats`).
- **Thành viên 4 (Team Lead, PyQt6 UI & System Integration Owner):**
  - Khởi tạo cấu trúc thư mục `src/`, `tests/`, `data/`, `docs/`, `requirements.txt` (`PyQt6>=6.6.0`, `pytest>=8.0.0`).
  - Thiết lập workflow `.github/workflows/python-tests.yml` tự động chạy `pytest -v`.
  - Ban hành `docs/interfaces.md`, `CONTRIBUTING.md`, PR template và khởi tạo skeleton `MainWindow` tại `src/ui/main_window.py` cùng entrypoint `src/main.py`.

#### Tiêu chí nghiệm thu (Acceptance Criteria)
1. Cài đặt môi trường thành công bằng `pip install -r requirements.txt` trên Python 3.10+.
2. GitHub Actions CI (`.github/workflows/python-tests.yml`) chạy `pytest -v` thành công trên nhánh `main` sau các PR của M1.
3. `Candle` và `csv_loader` từ chối chính xác dữ liệu `NaN`/`Inf`, `volume < 0`, sai quan hệ `OHLC`, timestamp trùng/giảm dần kèm `line_num`.
4. Core `RingBuffer` không chứa bất kỳ import hay tham chiếu nào tới `collections.deque`.
5. Toàn bộ skeleton của `CircularDeque`, `SegmentTree`, `MainWindow` khớp 100% signatures trong `docs/interfaces.md`.

#### Checklist nộp GitHub PR (M1)
- [ ] Tạo branch đúng quy chuẩn: `feat/m1-setup-ci`, `feat/m1-candle-csv-ringbuffer`, `feat/m1-skeleton-deque`, `feat/m1-skeleton-segtree`.
- [ ] Chạy `pytest -v` tại local đạt 100% pass trước khi mở PR.
- [ ] Tuân thủ 100% signature, tên file và invariants trong `docs/interfaces.md`.
- [ ] Không dùng `collections.deque` trong `src/core/ring_buffer.py` hay `src/algorithms/monotonic_deque.py`.
- [ ] Điền đầy đủ mục trong PR template và được Thành viên 4 (Team Lead) review & approve.

---

### Milestone 2 (M2): Hoàn thiện Toàn bộ Cấu trúc Dữ liệu Lõi & Design Patterns
- **Thời gian:** 23/11/2026 – 29/11/2026
- **Ngày Deadline:** **29/11/2026 (23:59)**
- **Mục tiêu:** Hoàn thiện cài đặt đầy đủ các cấu trúc dữ liệu nền tảng: `RingBuffer` + `data_simulator` + dữ liệu mẫu `sample_ohlcv.csv`; `CircularDeque` + `MonotonicDeque` + `SlidingWindowIndicators`; `SegmentTree` + `scan_range` oracle; `EventBus` + `CommandHistory`.
- **Người chịu trách nhiệm chính:** **Thành viên 1, Thành viên 2, Thành viên 3** (mỗi người chịu trách nhiệm module DSA độc lập 25%) và **Thành viên 4** (chịu trách nhiệm Patterns & điều phối tích hợp).

#### Task chi tiết theo từng thành viên
- **Thành viên 1 (Data Engineer & Ring Buffer Owner):**
  - Hoàn thiện 100% `RingBuffer` (`push`, `get_all`, `latest`, `__len__`, `is_full`, `clear`) bảo đảm $O(1)$ push và $O(K)$ snapshot theo thứ tự cũ nhất $\to$ mới nhất.
  - Cài đặt `generate_synthetic_candles(count, seed=42, start_ts=1700000000, interval_sec=60)` và `ReplayDataSource(candles)` (`step()`, `reset()`, `replace_or_append(candle)`) tại `src/core/data_simulator.py`.
  - Tạo bộ dữ liệu thực tế chuẩn `data/sample_ohlcv.csv` phục vụ chạy demo và kiểm thử `--cli`.
- **Thành viên 2 (Sliding Window Analytics & Coordinate Math Owner):**
  - Hoàn thiện `CircularDeque(capacity=16)` (`push_front`, `push_back`, `pop_front`, `pop_back`, `peek_front`, `peek_back`, `__len__`, `is_empty`, `to_list`) với cơ chế tự mở rộng gấp đôi $2\times$ khi đầy và ném `IndexError` khi rỗng; **cấm dùng `collections.deque`**.
  - Cài đặt `MonotonicDeque(mode='min'|'max')` (`push`, `evict_before`, `extrema`, `clear`) chạy trên `CircularDeque`.
  - Cài đặt `SlidingWindowIndicators`: `rolling_min_max`, `sma`, `ema`, `donchian_channels`, `bollinger_bands` với độ phức tạp $O(N)$.
- **Thành viên 3 (Range Query & Decimation Algorithms Owner):**
  - Cài đặt `RangeStats` frozen dataclass (`min_low`, `max_high`, `volume_sum`) và `SegmentTree(candles=None)` tại `src/algorithms/segment_tree.py`.
  - Hoàn thiện `query(left, right)` trên khoảng nửa mở `[left, right)` trong $O(\log N)$, `update(index, candle)` trong $O(\log N)$, `append(candle)` có cơ chế rebuild power-of-2 capacity động khi đầy, và `__len__()`.
  - Cài đặt hàm đối chiếu vét cạn `scan_range(candles, left, right)` làm oracle kiểm chứng tính đúng đắn tuyệt đối của `SegmentTree`.
- **Thành viên 4 (Team Lead, PyQt6 UI & System Integration Owner):**
  - Cài đặt `EventBus` (`subscribe`, `unsubscribe`, `publish`) tại `src/patterns/observer.py`.
  - Cài đặt `Command` ABC, `ViewportChangeCommand`, và `CommandHistory(max_size=100)` (`execute`, `undo`, `redo`, `can_undo`, `can_redo`) tại `src/patterns/command_history.py`.
  - Review các PR thuật toán lõi của Thành viên 1, 2, 3, bảo đảm không phá vỡ contract.

#### Tiêu chí nghiệm thu (Acceptance Criteria)
1. `RingBuffer` ghi đè chính xác khi vượt `capacity`, `get_all()` giữ đúng thứ tự thời gian, không dùng `collections.deque`.
2. `ReplayDataSource.replace_or_append` xử lý đúng cả 2 trường hợp: cập nhật nến đang mở (`timestamp == last.timestamp`) và nối nến mới (`timestamp > last.timestamp`).
3. `CircularDeque` tự nhân đôi dung lượng thành công qua nhiều chu kỳ wrap-around; `MonotonicDeque` và các chỉ báo `SlidingWindowIndicators` cho kết quả khớp tuyệt đối với nghiệm chuẩn $O(N \cdot W)$.
4. `SegmentTree.query(left, right)` khớp 100% với `scan_range(candles, left, right)` trên hàng trăm truy vấn ngẫu nhiên, kể cả sau nhiều lần `update()` và `append()` vượt ngưỡng power-of-2.
5. `EventBus` và `CommandHistory` xử lý an toàn Undo/Redo nhiều bước, xóa redo stack khi thực thi lệnh mới và tôn trọng giới hạn `max_size`.

#### Checklist nộp GitHub PR (M2)
- [ ] Branch đúng quy chuẩn: `feat/m2-ringbuffer-simulator`, `feat/m2-monotonic-indicators`, `feat/m2-segment-tree`, `feat/m2-observer-command`.
- [ ] Chạy `pytest -v` đạt 100% pass.
- [ ] Đối soát 100% signatures với `docs/interfaces.md` (đặc biệt half-open `[left, right)` của `SegmentTree` và `IndexError` của `CircularDeque`).
- [ ] Kiểm tra sạch bóng `collections.deque` trong `RingBuffer` và `CircularDeque`.
- [ ] PR template hoàn chỉnh + Team Lead review & merge.

---

### Milestone 3 (M3): Toán học Tọa độ, Giảm mẫu LTTB, QuadTree & Custom Canvas
- **Thời gian:** 30/11/2026 – 06/12/2026
- **Ngày Deadline:** **06/12/2026 (23:59)**
- **Mục tiêu:** Xây dựng tầng biến đổi không gian World $\leftrightarrow$ Screen với Cursor-Anchored Zoom/Pan, thuật toán nén đồ thị LTTB & gộp nến OHLC theo mật độ pixel, cây phân chia không gian 2D `QuadTree` cho crosshair snapping, và bộ vẽ đồ thị tùy biến `ChartCanvasWidget` có khả năng tính khung hình headless.
- **Người chịu trách nhiệm chính:** **Thành viên 2** (`CoordinateTransformer`), **Thành viên 3** (`LTTBDecimator`, `QuadTree`) và **Thành viên 4** (`ChartCanvasWidget`).

#### Task chi tiết theo từng thành viên
- **Thành viên 1 (Data Engineer & Ring Buffer Owner):**
  - Bổ sung các edge-case validation cho `csv_loader` và `data_simulator` (xử lý dataset lớn `100,000+` nến, tối ưu tốc độ sinh & nạp CSV).
  - Hỗ trợ kiểm thử tính nhất quán dữ liệu `Candle` khi truyền qua `aggregate_ohlcv_buckets` và `ChartCanvasWidget`.
- **Thành viên 2 (Sliding Window Analytics & Coordinate Math Owner):**
  - Cài đặt hoàn chỉnh `ViewportState` (với mặc định `padding_left=12`, `padding_right=72`, `padding_top=16`, `padding_bottom=28`) và `CoordinateTransformer` tại `src/core/coordinate_math.py`.
  - Triển khai `index_to_x`, `x_to_index`, `price_to_y`, `y_to_price`, `world_to_screen`, `screen_to_world`, `zoom_at_pixel`, `pan_by_pixels` bảo đảm tính khả nghịch $f^{-1}(f(x)) \approx x$ và bất biến điểm neo con trỏ khi zoom.
- **Thành viên 3 (Range Query & Decimation Algorithms Owner):**
  - Cài đặt `LTTBDecimator.downsample(points, threshold)` và `aggregate_ohlcv_buckets(candles, start_idx, end_idx, max_candles)` tại `src/algorithms/lttb_decimator.py`.
  - Cài đặt `Bounds`, `SpatialPoint`, và `QuadTree(bounds, capacity=4)` (`insert`, `query_range`, `nearest`) tại `src/algorithms/quad_tree.py`.
- **Thành viên 4 (Team Lead, PyQt6 UI & System Integration Owner):**
  - Xây dựng `ChartCanvasWidget` kế thừa `QWidget` tại `src/ui/chart_canvas.py` sử dụng `QPainter` vẽ nền lưới, nến Nhật (tăng/giảm + râu nến), cột volume, các đường chỉ báo kỹ thuật và crosshair.
  - Tách biệt logic dựng khung hình thuần toán học vào hàm headless `compute_visible_frame()` (không phụ thuộc QApplication/GUI loop) kết nối `CoordinateTransformer`, `SegmentTree`, `LTTBDecimator`/`aggregate_ohlcv_buckets`, `QuadTree` và `SlidingWindowIndicators`.
  - Tích hợp sự kiện chuột (Wheel zoom neo con trỏ, Drag pan tạo `ViewportChangeCommand`, Hover crosshair truy vấn `QuadTree.nearest`).

#### Tiêu chí nghiệm thu (Acceptance Criteria)
1. Biến đổi ngược `screen_to_world(*world_to_screen(idx, price))` sai số $< 10^{-9}$; `zoom_at_pixel` giữ nguyên chỉ số thế giới tại `pixel_x` trước và sau zoom.
2. `LTTBDecimator.downsample` giữ nguyên điểm đầu và điểm cuối, trả về đúng số lượng điểm `threshold` (khi `len(points) > threshold`).
3. `aggregate_ohlcv_buckets` bảo toàn chuẩn OHLC (`open` đầu bucket, `high` lớn nhất, `low` nhỏ nhất, `close` cuối bucket, `volume` bằng tổng volume các nến thành phần).
4. `QuadTree.query_range` và `QuadTree.nearest` cho kết quả chính xác 100% khi đối chiếu với tìm kiếm tuyến tính vét cạn.
5. `ChartCanvasWidget.compute_visible_frame()` chạy thành công trong môi trường headless không mở cửa sổ GUI.

#### Checklist nộp GitHub PR (M3)
- [ ] Branch đúng quy chuẩn: `feat/m3-coordinate-math`, `feat/m3-lttb-quadtree`, `feat/m3-chart-canvas`, `feat/m3-data-scale-validation`.
- [ ] Chạy `pytest -v` đạt 100% pass.
- [ ] Tuân thủ 100% API contract tại `docs/interfaces.md` (đặc biệt padding mặc định `ViewportState` và các hàm `CoordinateTransformer`, `QuadTree`, `LTTBDecimator`).
- [ ] Không gán logic vẽ PyQt6 thuần túy vào trong `compute_visible_frame()`.
- [ ] PR template hoàn chỉnh + Team Lead review & approve.

---

### Milestone 4 (M4): Tích hợp MainWindow & Hoàn thiện Bộ Unit Tests Toàn nhóm
- **Thời gian:** 07/12/2026 – 13/12/2026
- **Ngày Deadline:** **13/12/2026 (23:59)**
- **Mục tiêu:** Hoàn thiện giao diện điều khiển hoàn chỉnh `MainWindow` với live replay (`QTimer`), bật/tắt chỉ báo, Undo/Redo, nạp lại CSV và thanh trạng thái; đồng thời hoàn thành bộ Unit Tests chuyên sâu cho cả 4 thành viên.
- **Người chịu trách nhiệm chính:** **Thành viên 4** (`MainWindow` & Gatekeeper) và **Thành viên 1, 2, 3** (chịu trách nhiệm bộ Unit Test của module mình phụ trách).

#### Task chi tiết theo từng thành viên
- **Thành viên 1 (Data Engineer & Ring Buffer Owner):**
  - Hoàn thiện bộ test toàn diện `tests/test_ring_buffer.py` bao gồm: kiểm tra validation `Candle` (NaN, Inf, âm, sai OHLC), `csv_loader` (lỗi dòng kèm `line_num`, duplicate/out-of-order timestamp, file rỗng/header-only), wrap-around `RingBuffer`, `ReplayDataSource.replace_or_append`, và kiểm tra tĩnh cấm dùng `collections.deque`.
- **Thành viên 2 (Sliding Window Analytics & Coordinate Math Owner):**
  - Hoàn thiện bộ test toàn diện `tests/test_monotonic_deque.py` bao gồm: `CircularDeque` (`2x` auto-resize, `IndexError` khi rỗng, cấm `collections.deque`), `MonotonicDeque` đối chiếu brute-force, kiểm chứng `sma`, `ema`, `donchian_channels`, `bollinger_bands`, `rolling_min_max`, và kiểm chứng biến đổi tọa độ/zoom/pan của `CoordinateTransformer`.
- **Thành viên 3 (Range Query & Decimation Algorithms Owner):**
  - Hoàn thiện `tests/test_segment_tree.py`: kiểm tra differential testing giữa `SegmentTree.query` và `scan_range` oracle trên nhiều kích thước không phải lũy thừa của 2, kiểm tra `update`, `append` kích hoạt rebuild power-of-2, và `QuadTree` (`insert`, `query_range`, `nearest`).
  - Hoàn thiện `tests/test_lttb.py`: kiểm tra bảo toàn điểm đầu/cuối của `LTTBDecimator`, tính chất giảm sai số hình học, và bảo toàn OHLCV của `aggregate_ohlcv_buckets`.
- **Thành viên 4 (Team Lead, PyQt6 UI & System Integration Owner):**
  - Hoàn thiện `MainWindow` (`src/ui/main_window.py`) nhúng `ChartCanvasWidget`:
    - Bộ điều khiển `QTimer` Replay: Play, Pause, Reset, chọn tốc độ phát lại.
    - Checkbox / Toggle bật tắt các chỉ báo: SMA, EMA, Bollinger Bands, Donchian Channels, chế độ LTTB/OHLC Aggregation.
    - Nút & phím tắt Undo / Redo kết nối `CommandHistory` qua `EventBus`.
    - Chức năng CSV Reload đọc file mới qua `csv_loader.load_candles` và tái xây dựng `RingBuffer`/`SegmentTree`.
    - Status bar hiển thị OHLCV tại crosshair, khoảng giá `SegmentTree` (`min_low`, `max_high`, `volume_sum`), số lượng nến đang hiển thị/tổng số nến.

#### Tiêu chí nghiệm thu (Acceptance Criteria)
1. Cửa sổ `MainWindow` mở được bằng `python3 -m src.main` (trên môi trường có display) và thao tác mượt các nút Play/Pause/Reset/Speed, Indicator Toggles, Undo/Redo, CSV Reload.
2. Toàn bộ 4 tệp unit tests (`tests/test_ring_buffer.py`, `tests/test_monotonic_deque.py`, `tests/test_segment_tree.py`, `tests/test_lttb.py`) đạt tỷ lệ pass 100% khi chạy `pytest -v`.
3. Không có hiện tượng rò rỉ tham chiếu hoặc crash khi nhấn Reset / CSV Reload nhiều lần liên tiếp.
4. Status bar phản ánh đồng bộ kết quả từ `SegmentTree.query` trên viewport hiện tại.

#### Checklist nộp GitHub PR (M4)
- [ ] Branch đúng quy chuẩn: `feat/m4-tests-ringbuffer`, `feat/m4-tests-deque-math`, `feat/m4-tests-segtree-lttb`, `feat/m4-main-window`.
- [ ] Chạy `pytest -v` tất cả unit test files đạt 100% pass.
- [ ] Kiểm tra 100% tuân thủ `docs/interfaces.md` và không có cảnh báo type/lint nghiêm trọng.
- [ ] Có docstring & type annotations đầy đủ trên mọi hàm/lớp công khai.
- [ ] PR template hoàn chỉnh + Team Lead review & approve.

---

### Milestone 5 (M5): Kiểm thử Tích hợp, CLI/Benchmark & Tối ưu Hiệu năng
- **Thời gian:** 14/12/2026 – 20/12/2026
- **Ngày Deadline:** **20/12/2026 (23:59)**
- **Mục tiêu:** Triển khai bộ kiểm thử tích hợp đầu-cuối (`tests/test_integration.py`), hoàn thiện chế độ chạy `--cli` và `--benchmark` trên `src/main.py`, đo lường hiệu năng thời gian (`time.perf_counter`) và bộ nhớ (`tracemalloc`), xử lý triệt để các lỗi biên & tối ưu điểm nghẽn.
- **Người chịu trách nhiệm chính:** **Thành viên 4** (chịu trách nhiệm `test_integration.py` và `src/main.py`) cùng **Thành viên 1, 2, 3** (chịu trách nhiệm profiling & bug fix theo từng module).

#### Task chi tiết theo từng thành viên
- **Thành viên 1 (Data Engineer & Ring Buffer Owner):**
  - Profiling tốc độ `csv_loader.load_candles`, `generate_synthetic_candles(count=10000)` và `RingBuffer` với `tracemalloc` & `time.perf_counter`.
  - Sửa lỗi biên liên quan đến định dạng CSV thực tế hoặc `ReplayDataSource` khi chạy tốc độ cao.
- **Thành viên 2 (Sliding Window Analytics & Coordinate Math Owner):**
  - Profiling bộ nhớ và thời gian thực thi của `CircularDeque`, `MonotonicDeque`, `SlidingWindowIndicators` trên chuỗi `10,000`–`100,000` nến.
  - Tinh chỉnh ngưỡng zoom min/max của `CoordinateTransformer` để tránh chia cho 0 hoặc méo khung hình khi zoom quá sâu.
- **Thành viên 3 (Range Query & Decimation Algorithms Owner):**
  - Profiling `SegmentTree` (build, query, append), `LTTBDecimator` và `QuadTree` trên tập dữ liệu lớn (`--count 10000` trở lên).
  - So sánh tốc độ `SegmentTree.query` so với `scan_range` oracle trong chế độ benchmark để chứng minh ưu thế tiệm cận $O(\log N)$ so với $O(N)$.
- **Thành viên 4 (Team Lead, PyQt6 UI & System Integration Owner):**
  - Hoàn thiện `tests/test_integration.py` kiểm thử luồng tích hợp hoàn chỉnh: load CSV / generate synthetic $\to$ nạp `RingBuffer` + `SegmentTree` $\to$ tính `SlidingWindowIndicators` $\to$ Zoom/Pan qua `CommandHistory` (Undo/Redo) + `EventBus` $\to$ `ChartCanvasWidget.compute_visible_frame()`.
  - Hoàn thiện `src/main.py` hỗ trợ đầy đủ tham số chuẩn: `python3 -m src.main [--cli | --benchmark | --gui] [--csv data/sample_ohlcv.csv] [--count 10000]`.

#### Tiêu chí nghiệm thu (Acceptance Criteria)
1. Lệnh `python3 -m src.main --cli` thực thi trọn vẹn pipeline dữ liệu & giải thuật, in báo cáo tổng hợp OHLCV, chỉ báo và RangeStats mà không cần X11/GUI display.
2. Lệnh `python3 -m src.main --benchmark` thực thi hoàn chỉnh bộ đo `time.perf_counter` & `tracemalloc` (ví dụ trên `--count 10000`), đối chiếu tốc độ `SegmentTree` vs `scan_range`, `MonotonicDeque` vs brute-force, `LTTBDecimator`, và `compute_visible_frame()`.
3. Lệnh `pytest -v` chạy toàn bộ unit tests và `tests/test_integration.py` đạt 100% pass.
4. Không phát sinh lỗi chia cho 0 khi zoom tối đa, pan vượt biên hoặc dataset rỗng/ít nến (`< 3` nến).

#### Checklist nộp GitHub PR (M5)
- [ ] Branch đúng quy chuẩn: `feat/m5-integration-cli-benchmark`, `feat/m5-perf-ringbuffer`, `feat/m5-perf-math-indicators`, `feat/m5-perf-segtree-lttb`.
- [ ] Đính kèm log thực tế của `pytest -v`, `python3 -m src.main --cli`, và `python3 -m src.main --benchmark` vào phần mô tả PR.
- [ ] Tuân thủ 100% CLI flags chuẩn và API contracts trong `docs/interfaces.md`.
- [ ] Không còn issue/bug mức Critical hoặc High mở trong danh sách theo dõi.
- [ ] PR template hoàn chỉnh + Team Lead review & approve.

---

### Milestone 6 (M6): Hoàn thiện Tài liệu Học thuật, Kiểm chứng CI & Demo Cuối kỳ
- **Thời gian:** 21/12/2026 – 27/12/2026
- **Ngày Deadline:** **27/12/2026 (23:59)**
- **Mục tiêu:** Chốt toàn bộ tài liệu kỹ thuật & báo cáo phân công học thuật (`README.md`, `ROADMAP.md`, `DEADLINES_AND_TASKS.md`, `CONTRIBUTING.md`, `docs/interfaces.md`, `docs/team_plan_report.md`), đảm bảo CI GitHub Actions xanh 100% trên commit cuối cùng, đóng gói sản phẩm và diễn tập Demo bảo vệ đồ án.
- **Người chịu trách nhiệm chính:** **Toàn nhóm** (mỗi thành viên chịu trách nhiệm trình bày & nghiệm thu phần 25% của mình) và **Thành viên 4** (tổng hợp đóng gói & xác nhận CI cuối).

#### Task chi tiết theo từng thành viên
- **Thành viên 1 (Data Engineer & Ring Buffer Owner):**
  - Hoàn thiện phần mô tả thiết kế `Candle`, `csv_loader`, `RingBuffer`, `data_simulator` và minh chứng độ phức tạp $O(1)$/$O(K)$ trong báo cáo.
  - Chuẩn bị kịch bản demo chứng minh xử lý CSV lỗi và replay nến thời gian thực.
- **Thành viên 2 (Sliding Window Analytics & Coordinate Math Owner):**
  - Hoàn thiện phần mô tả thuật toán `CircularDeque`, `MonotonicDeque`, 5 chỉ báo `SlidingWindowIndicators` và ma trận tọa độ Affine/Cursor-Anchored Zoom.
  - Chuẩn bị kịch bản demo minh họa các đường SMA/EMA/Bollinger/Donchian và thao tác zoom neo con trỏ.
- **Thành viên 3 (Range Query & Decimation Algorithms Owner):**
  - Hoàn thiện phần phân tích lý thuyết & kết quả benchmark `SegmentTree` vs `scan_range`, thuật toán `LTTBDecimator` và `QuadTree` 2D.
  - Chuẩn bị kịch bản demo trực quan hóa khả năng nén `10,000+` điểm xuống mật độ màn hình mà vẫn giữ đỉnh/đáy.
- **Thành viên 4 (Team Lead, PyQt6 UI & System Integration Owner):**
  - Tổng rà soát tính đồng bộ 100% giữa mã nguồn, bộ test và hệ thống tài liệu (`README.md`, `ROADMAP.md`, `DEADLINES_AND_TASKS.md`, `CONTRIBUTING.md`, `docs/interfaces.md`, `docs/team_plan_report.md`).
  - Xác nhận GitHub Actions CI chạy `pytest -v` đạt 100% Pass trên nhánh `main`, tag bản release cuối kỳ và điều phối buổi diễn tập Demo.

#### Tiêu chí nghiệm thu (Acceptance Criteria)
1. Tất cả các lệnh chuẩn (`pip install -r requirements.txt`, `pytest -v`, `python3 -m src.main --cli`, `python3 -m src.main --benchmark`, `python3 -m src.main`) hoạt động trơn tru trên bản snapshot cuối cùng.
2. GitHub Actions CI (`.github/workflows/python-tests.yml`) đạt trạng thái xanh 100% trên nhánh `main` không có test bị skip hoặc fail.
3. Toàn bộ tài liệu học thuật đồng nhất số liệu ngày tháng (16/11/2026 – 27/12/2026), phân công (25% – 25% – 25% – 25%), và đặc tả 14 components.
4. Bộ slide/kịch bản demo 4 thành viên sẵn sàng trình bày rõ đóng góp cá nhân và năng lực kỹ thuật của từng người.

#### Checklist nộp GitHub PR (M6)
- [ ] Branch đúng quy chuẩn: `feat/m6-docs-sync`, `feat/m6-final-polish-tv1`, `feat/m6-final-polish-tv2`, `feat/m6-final-polish-tv3`.
- [ ] Chạy lại toàn bộ `pytest -v` và kiểm tra CI GitHub Actions xanh 100%.
- [ ] Đối soát toàn bộ 14 components trong `docs/interfaces.md` khớp 100% với code thực tế trên `main`.
- [ ] Xác nhận không còn file rác, log debug thừa hay code dead/commented-out.
- [ ] PR template hoàn chỉnh + Team Lead (Thành viên 4) duyệt & tạo tag bàn giao cuối kỳ.
