# Hướng dẫn Đóng góp & Quy chuẩn Phát triển (CONTRIBUTING)

Tài liệu này quy định quy trình Git Flow, quy ước đặt tên nhánh, tiêu chuẩn mã nguồn Python và quy trình duyệt Pull Request (PR) bắt buộc cho toàn bộ 4 thành viên trong dự án **Interactive TradingView Stock Chart Engine (DSA Python)** (16/11/2026 – 27/12/2026).

---

## 1. Quy chuẩn Git Flow & Đặt tên Nhánh

### 1.1 Mô hình Nhánh
- **`main`**: Nhánh ổn định duy nhất dùng để demo và chấm điểm. **Tuyệt đối cấm** `git push` trực tiếp lên `main`; mọi thay đổi phải đi qua Pull Request và vượt qua CI `pytest -v`.
- **Nhánh tính năng (`feat/mX-<topic>`)**: Mỗi task hoặc sub-module thuộc Milestone `M1`–`M6` phải được phát triển trên một nhánh riêng tách từ `main` mới nhất.

### 1.2 Quy ước Đặt tên Branch Bắt buộc
Định dạng chuẩn:
```text
feat/m<số_milestone>-<chủ_đề_ngắn_gọn_kebab_case>
```

**Ví dụ hợp lệ:**
- `feat/m1-candle-csv-ringbuffer`
- `feat/m2-monotonic-indicators`
- `feat/m2-segment-tree`
- `feat/m3-coordinate-math`
- `feat/m3-lttb-quadtree`
- `feat/m4-main-window`
- `feat/m5-integration-cli-benchmark`
- `feat/m6-docs-sync`

**Các nhánh bổ trợ khi sửa lỗi hoặc tài liệu (nếu cần):**
- `fix/m<X>-<mô_tả_lỗi>` (ví dụ: `fix/m5-zoom-clamp-zero`)
- `docs/m<X>-<mô_tả>` (ví dụ: `docs/m6-final-report`)

---

## 2. Tiêu chuẩn Mã nguồn (Coding Standards)

### 2.1 Ràng buộc Tuyệt đối về Cài đặt DSA & Design Patterns (Zero-Shortcut + YAGNI Policy)
1. **CẤM dùng `collections.deque`** trong `RingBuffer` (`src/core/ring_buffer.py`) và `CircularDeque` (`src/algorithms/monotonic_deque.py`), kể cả để chuyển đổi dữ liệu nội bộ hay viết helper. Mọi thao tác phải dựa trên mảng vòng chỉ số `(idx + 1) % capacity` / `(idx - 1) % capacity` trên Python `list`.
2. **CẤM dùng thư viện vẽ biểu đồ bên thứ ba** (`matplotlib`, `pyqtgraph`, `plotly`, `mplfinance`, v.v.) cho widget chính. `ChartCanvasWidget` đã được cung cấp sẵn dùng `QPainter` của PyQt6.
3. **Không tự ý thay đổi API Contracts:** Tên class, tên hàm, thứ tự tham số, giá trị mặc định và kiểu trả về phải khớp 100% với `docs/interfaces.md`.
4. **Quy chuẩn Design Patterns chuẩn Python (theo Refactoring.Guru, không over-engineer):**
   - **Factory Method (`@classmethod`)**: Dùng `ReplayDataSource.from_csv(path)` / `from_synthetic(...)` để khởi tạo nguồn dữ liệu mà không tạo thêm class factory rườm rà.
   - **Prototype (`dataclasses.replace`)**: Clone `ViewportState` bất biến bằng `dataclasses.replace(...)` thay vì mutate tại chỗ hoặc tự viết interface `clone()`.
   - **Observer & Command + Dependency Injection**: Truyền `EventBus` và `CommandHistory` qua constructor; **CẤM** biến chúng thành global **Singleton** (làm rò rỉ state giữa các test `pytest`).
   - **KHÔNG tự ý thêm Builder / Abstract Factory** khi Python `@dataclass` defaults đã đủ và dự án chỉ có 1 backend (`PyQt6`).

### 2.2 Type Hints & Docstrings
- **Python Version:** Tương thích chuẩn **Python 3.10+** (verified trên **Python 3.14.9**), sử dụng cú pháp hiện đại `list[Candle]`, `float | None`, `tuple[float, float]`.
- **Type Annotations:** 100% hàm công khai, phương thức lớp, tham số và giá trị trả về phải có type hints đầy đủ.
- **Docstrings:** Mọi module, class và hàm/phương thức công khai phải có docstring rõ ràng mô tả: mục đích, tham số (`Args`), giá trị trả về (`Returns`), ngoại lệ (`Raises`), và **độ phức tạp Thời gian / Không gian ($O(\cdot)$)** đối với các thuật toán DSA.

### 2.3 Xử lý Lỗi & Edge Cases
- Dùng ngoại lệ đúng ngữ nghĩa:
  - `ValueError` cho vi phạm miền giá trị / dữ liệu đầu vào (`Candle`, `csv_loader`, `RingBuffer(capacity <= 0)`, `LTTBDecimator.downsample(..., threshold < 0)`, `aggregate_ohlcv_buckets(..., max_candles <= 0)`).
  - `IndexError` cho truy cập rỗng hoặc ngoài biên (`CircularDeque.pop_front()` khi rỗng, `SegmentTree.update()` sai index).
- Luôn giữ tính xác định (determinism) cho bộ sinh dữ liệu (`seed`) và bộ test.

### 2.4 Yêu cầu Kiểm thử (`pytest -m pXX` & `pytest -v`)
- Bộ test trong `tests/` đóng vai trò **LeetCode Judge** có sẵn cho từng bài `P01`–`P11` và `integration`. Trong lúc làm bài, chạy riêng bài của mình: `pytest -m p03` (hoặc lọc nhánh bằng `-k`).
- Các bài phức tạp (`SegmentTree`, `MonotonicDeque`, `QuadTree`, `RingBuffer`) đã có sẵn **differential tests** (đối chiếu ngẫu nhiên với brute-force oracle) và **AST tests** kiểm tra cấm `collections.deque`.
- Trước khi nộp/demo toàn dự án, chạy full suite `QT_QPA_PLATFORM=offscreen pytest -v` bảo đảm 100% Pass.

---

## 3. Quy trình Mở & Duyệt Pull Request (PR Checklist)

Trước khi tạo PR hợp nhất vào `main`, tác giả **bắt buộc** tự kiểm tra và đánh dấu toàn bộ checklist dưới đây:

```markdown
### PR Verification Checklist
- [ ] Tên branch tuân thủ quy ước `feat/mX-<topic>` (hoặc `fix/mX-<topic>`).
- [ ] Đã đồng bộ code với `main` mới nhất và không có merge conflict.
- [ ] Đã chạy `pytest -v` tại local và đạt 100% Pass (không skip test).
- [ ] Đã kiểm tra lệnh liên quan (`python3 -m src.main --cli` / `--benchmark` / `--gui`) khi đụng chạm pipeline hoặc entrypoint.
- [ ] Chữ ký hàm, kiểu dữ liệu, invariants khớp 100% với `docs/interfaces.md`.
- [ ] Đã xác nhận KHÔNG sử dụng `collections.deque` trong `RingBuffer` và `CircularDeque`.
- [ ] Đầy đủ Python 3.10+ type hints và docstrings (kèm độ phức tạp Big-O cho code DSA).
- [ ] Không chứa code thừa, biến debug `print()`, hay file tạm không thuộc phạm vi task.
```

### Quy tắc Review & Merge
1. Mỗi PR cần ít nhất **1 lượt duyệt chính thức từ Team Lead (Thành viên 4)** (hoặc Peer Review chéo giữa các thành viên đối với PR do Thành viên 4 mở).
2. GitHub Actions workflow `.github/workflows/python-tests.yml` phải báo **xanh 100%** trước khi nhấn Merge.
3. Sử dụng *Squash and merge* hoặc *Merge commit* rõ thông điệp theo Milestone: `[M2] Implement CircularDeque, MonotonicDeque and SlidingWindowIndicators`.
