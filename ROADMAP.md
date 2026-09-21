# Kế Hoạch Phát Triển Dự Án (Roadmap)
> **Dự án:** Xây dựng Động cơ Biểu đồ Chứng khoán Tương tác & Real-Time (Môn Cấu trúc Dữ liệu & Giải thuật - DSA)
> **Đối tượng:** Nhóm 4 sinh viên năm đầu/giữa đại học.

Tài liệu này chia dự án thành **3 giai đoạn** để nhóm không bị quá tải, đồng thời tập trung tối đa vào phần cốt lõi (DSA) để đạt điểm cao nhất, trước khi tiến đến phần giao diện đồ họa.

---

## 🎯 Tổng quan 3 Giai đoạn Phát triển

- **Giai đoạn 1: Lõi DSA & Giao diện dòng lệnh (CLI)** *(Trọng tâm lấy điểm A+)*: Xây dựng toàn bộ các cấu trúc dữ liệu và giải thuật từ đầu (from scratch) bằng Python thuần, chạy thử nghiệm qua Terminal.
- **Giai đoạn 2: Đo lường & Đánh giá hiệu năng (Benchmarking)**: Viết các script đo thời gian chạy (runtime), độ phức tạp Big-O và bộ nhớ với tập dữ liệu từ 10.000 đến 300.000 bản ghi.
- **Giai đoạn 3: Giao diện đồ họa PyQt6 & Stream Real-time** *(Phần nâng cao/Bonus)*: Tích hợp giao diện trực quan, zoom/pan mượt mà và luồng dữ liệu giả lập (`QThread`).

---

## 🚀 Giai đoạn 1: Phân công 4 Vai trò cho 4 Thành viên (Lõi DSA & CLI)

Vì nhóm có 4 thành viên, chúng ta chia các cấu trúc dữ liệu cốt lõi thành 4 module độc lập để mỗi bạn tự tay thiết kế và kiểm thử.

---

### 👤 Thành viên 1: Module Ingestion & Ring Buffer (Hàng đợi vòng)
- **Nhiệm vụ & Sản phẩm:** Xây dựng cấu trúc dữ liệu **Ring Buffer (Circular Queue)** để lưu trữ các tick giá/nến đến liên tục trong bộ nhớ cố định, không bị tràn hay cấp phát lại bộ nhớ liên tục. Viết hàm đọc file CSV lịch sử giá (Open, High, Low, Close, Volume).
- **Lý thuyết & Từ khóa tìm kiếm Google/YouTube:**
  - Từ khóa: `Circular Buffer Python implementation`, `Ring buffer FIFO array`.
  - Khái niệm: Con trỏ đầu (`head`), con trỏ đuôi (`tail`), cách quản lý dung lượng cố định (fixed capacity) và ghi đè dữ liệu cũ khi đầy (`overwrite`).
- **Bài tập thực hành trước khi viết code dự án:**
  - Viết một class `CircularBuffer` có dung lượng cố định là 5 phần tử. Thêm vào 7 phần tử số nguyên, in ra xem các phần tử cũ nhất có bị ghi đè đúng cách không.
- **File đích & Giao diện mã nguồn (Class/Signatures):**
  - File: `src/core/ring_buffer.py`
  - Các hàm chính:
    ```python
    class RingBuffer:
        def __init__(self, capacity: int): ...
        def push(self, item: dict) -> None: ...
        def get_all(self) -> list: ...
        def is_full(self) -> bool: ...
    ```

---

### 👤 Thành viên 2: Module Sliding Window Min/Max (Theo dõi đỉnh/đáy trượt)
- **Nhiệm vụ & Sản phẩm:** Xây dựng giải thuật/cấu trúc dữ liệu để tìm giá trị cao nhất (`High`) và thấp nhất (`Low`) trong một cửa sổ thời gian trượt (Sliding Window, ví dụ: 20 nến gần nhất) với độ phức tạp tối ưu $O(1)$ hoặc $O(\log K)$ thay vì quét lại toàn bộ mảng $O(K)$.
- **Lý thuyết & Từ khóa tìm kiếm Google/YouTube:**
  - Từ khóa: `Sliding Window Maximum Monotonic Queue Python`, `Deque sliding window min max`.
  - Khái niệm: Hàng đợi đơn điệu (Monotonic Queue) lưu trữ chỉ số (index), loại bỏ các phần tử cũ và nhỏ hơn/lớn hơn ở hai đầu deque.
- **Bài tập thực hành trước khi viết code dự án:**
  - Cho một mảng số nguyên `[1, 3, -1, -3, 5, 3, 6, 7]` và kích thước cửa sổ `k = 3`. Hãy viết hàm dùng Monotonic Deque để tìm giá trị lớn nhất trong từng cửa sổ trượt.
- **File đích & Giao diện mã nguồn (Class/Signatures):**
  - File: `src/algorithms/sliding_window.py`
  - Các hàm chính:
    ```python
    class SlidingWindowMinMax:
        def __init__(self, window_size: int): ...
        def add_price(self, high: float, low: float) -> None: ...
        def get_current_min_max(self) -> tuple[float, float]: ...
    ```

---

### 👤 Thành viên 3: Module Range Query & Segment Tree (Cây phân đoạn)
- **Nhiệm vụ & Sản phẩm:** Xây dựng cấu trúc **Segment Tree** (Cây phân đoạn) để thực hiện các truy vấn khoảng (Range Minimum Query - RMQ và Range Sum Volume) trên toàn bộ dữ liệu lịch sử cực nhanh với độ phức tạp $O(\log N)$.
- **Lý thuyết & Từ khóa tìm kiếm Google/YouTube:**
  - Từ khóa: `Segment Tree Range Minimum Query Python`, `Segment tree data structure tutorial`.
  - Khái niệm: Cây nhị phân biểu diễn các đoạn khoảng, xây dựng cây mất $O(N)$, truy vấn và cập nhật mất $O(\log N)$.
- **Bài tập thực hành trước khi viết code dự án:**
  - Xây dựng một Segment Tree tìm giá trị nhỏ nhất (Range Minimum) cho mảng `[8, 7, 3, 9, 5, 1, 10]`, sau đó thử truy vấn đoạn từ chỉ số 1 đến 5.
- **File đích & Giao diện mã nguồn (Class/Signatures):**
  - File: `src/algorithms/segment_tree.py`
  - Các hàm chính:
    ```python
    class SegmentTree:
        def __init__(self, data: list[float]): ...
        def query_min_max(self, L: int, R: int) -> tuple[float, float]: ...
        def update(self, index: int, new_value: float) -> None: ...
    ```

---

### 👤 Thành viên 4: Module CLI Visualizer, Benchmark & Test Runner (Trình điều khiển & Kiểm thử)
- **Nhiệm vụ & Sản phẩm:** 
  1. Viết giao diện dòng lệnh (CLI) hiển thị bảng nến ASCII trực quan hoặc tóm tắt dữ liệu qua Terminal.
  2. Viết tập kiểm thử tự động (Unit Tests bằng `pytest`) cho 3 thành viên trên.
  3. Viết script benchmark đo thời gian thực thi (mili-giây) và bộ nhớ khi chạy với 10k, 50k, 300k dòng dữ liệu CSV.
- **Lý thuyết & Từ khóa tìm kiếm Google/YouTube:**
  - Từ khóa: `Python pytest tutorial`, `Python timeit time performance measurement`, `Building terminal UI Python tables`.
  - Khái niệm: Đo benchmark thời gian chạy bằng thư viện `time` hoặc `timeit`, viết test case kiểm tra biên (edge cases).
- **Bài tập thực hành trước khi viết code dự án:**
  - Viết một file test `pytest` đơn giản kiểm tra hàm tính tổng hai số và dùng `time.perf_counter()` để đo thời gian chạy của một vòng lặp 1 triệu lần.
- **File đích & Giao diện mã nguồn (Class/Signatures):**
  - File: `src/main_cli.py`, `tests/test_performance.py`
  - Các hàm chính:
    ```python
    def run_cli_demo(csv_path: str) -> None: ...
    def benchmark_segment_tree() -> None: ...
    ```

---

## 📈 Giai đoạn 2 & 3 (Tóm tắt ngắn gọn)
- **Giai đoạn 2 (Đo lường):** Tổng hợp kết quả từ Thành viên 4 vào báo cáo `docs/complexity_analysis.md`, chứng minh các cấu trúc đạt đúng chuẩn Big-O ($O(\log N)$, $O(1)$).
- **Giai đoạn 3 (GUI & Stream - Bonus):** Lắp ráp các module lõi này vào khung cửa sổ `PyQt6` (`chart_canvas.py`, `main_window.py`) đã có sẵn trong repo để vẽ biểu đồ và chạy luồng dữ liệu thời gian thực.
