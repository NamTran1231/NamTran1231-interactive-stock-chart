# ROADMAP — DSA Stock Chart

## 1. Hướng đi thống nhất

Thay “DSA → benchmark → GUI bonus” bằng **M0–M6**: demo nhỏ chạy sớm, tích hợp DSA vào tính năng rồi đo hiệu quả. Bản đầu: một mã/một timeframe intraday, CSV và offline replay, Python + PyQt6/QPainter.

Ring Buffer và Segment Tree phải tự cài đặt; không dùng deque/thư viện cây để thay phần DSA cần chấm. List được dùng làm mảng; thư viện chuẩn `csv` được dùng để parsing.

**Rubric và deadline chưa được cung cấp.** Không gán lại lịch ba tuần hay hứa điểm số. Sliding Window/Quadtree/LTTB tùy chọn nếu rubric không bắt buộc.

## 2. Timeline theo dependencies và check-in

Luồng chính **M0 → M1 → M2 → M3 → M4 → M5**. Sau khi chốt contracts, thành viên 3 có thể phát triển/test cây song song M2. M6 chỉ bắt đầu khi lõi ổn định và còn thời gian.

| Mốc | Nhiệm vụ | Chủ trì | Điều kiện bắt đầu | Trạng thái |
| --- | --- | --- | --- | --- |
| M0 | Đồng bộ tài liệu, contracts và nghiên cứu | 4 + cả nhóm review | Đã đối chiếu remote | [ ] Chờ review/merge |
| M1 | Candle, CSV loader, synthetic fixture, CLI summary | 1 + 4 | M0 | [ ] Chưa nghiệm thu |
| M2 | Chart nhỏ, axes, pan/zoom/hover, clipping | 2 + 4 | M1 | [ ] Chưa nghiệm thu |
| M3 | Custom Ring Buffer/Segment Tree; scan oracle; autoscale | 1 + 3 + 2 | Contracts M1; tích hợp sau M2 | [ ] Chưa nghiệm thu |
| M4 | Timer replay, controls và append/replace | 4 + 1 + 3 | M3 | [ ] Chưa nghiệm thu |
| M5 | OHLCV grouping, benchmark và report | 4 + cả nhóm | M4 đúng | [ ] Chưa nghiệm thu |
| M6 | Extension có mục đích | Theo extension | Lõi ổn định, còn thời gian | [ ] Tùy chọn |

### Acceptance criteria

- **M0:** Tài liệu thống nhất scope/status/contracts, nguồn có link, unresolved rubric/deadline rõ ràng. Kiểm tra lại API nguồn trước implementation.
- **M1:** Synthetic fixture xác định, không phụ thuộc download; parse đúng; lỗi có số dòng; test empty/single-row, malformed, duplicate/out-of-order; README có lệnh setup/demo thực sự chạy được.
- **M2:** Khoảng 100 nến hiển thị đúng OHLC, axes có nghĩa, pan/zoom/hover đúng; xử lý resize, flat prices, empty data và bounds. Autoscale ban đầu được phép scan.
- **M3:** Tree build O(N), query/point update O(log N), storage O(N); khớp scan qua random ranges và updates. Buffer qua nhiều vòng wraparound đúng, capacity > 0. Chart thay scan bằng tree; giữ scan làm oracle. Fractional volume so với tolerance.
- **M4:** Replay xác định cho kết quả mong đợi; cùng timestamp replace latest, mới hơn append, cũ hơn reject; không rebuild toàn bộ tree mỗi event. Test restart và capacity expansion. Chart/stats không lộ nến sau cursor.
- **M5:** Grouping giữ đúng OHLCV; benchmark ghi môi trường, seed/count, baseline, repeated runs; tách loading/query/ingestion/rendering. Chỉ công bố tốc độ thực đo.
- **M6:** Mỗi extension có mục đích người dùng, edge cases và validation. Không mặc định làm tất cả.

## 3. Đúng 4 vai trò và đầu ra

Chủ dự án đã chấp thuận phân công mới. Mỗi người tự test module mình, review chéo và đọc [interfaces](docs/interfaces.md) trước triển khai. Role 4 điều phối, không gánh toàn bộ test.

### Thành viên 1 — Hưng — Dữ liệu, CSV, Ring Buffer

- **Deliverables:** Candle độc lập Qt, loader validate, fixture synthetic, buffer mảng vòng tự quản lý index/size; full history riêng.
- **Học trước:** `Python dataclass CSV validation`, `circular buffer array head tail modulo`.
- **Bài tập:** Capacity 3, push 1–8 còn `[6, 7, 8]`; parse 3 nến và báo lỗi theo dòng.
- **File/API dự kiến:** `src/core/candle.py` — `Candle`; `src/core/csv_loader.py` — `load_candles(path: str) -> list[Candle]`; `src/core/ring_buffer.py` — `RingBuffer(capacity: int)`, `push(candle)`, `get_all()`, `is_full()`.
- **Done:** CSV đạt contracts; invalid capacity bị từ chối; wraparound đúng, push O(1), snapshot O(K). Cải tiến prototype hiện có; deque wrapper chưa phải DSA from scratch.

### Thành viên 2 — Dũng — Rendering, tọa độ, interactions

- **Deliverables:** QPainter candles/axes, viewport/clipping, pan/zoom/hover; nối query tree ở M3.
- **Học trước:** `PyQt6 QPainter QWidget paintEvent`, `affine transform world screen coordinates`, `cursor anchored zoom`.
- **Bài tập:** Vẽ 10 nến, round trip world↔screen, zoom giữ điểm dưới cursor.
- **File/API dự kiến:** `src/core/coordinate_math.py` — `world_to_screen(...)`, `screen_to_world(...)`; `src/ui/chart_canvas.py` — `ChartCanvasWidget`, `paintEvent(self, event)`.
- **Done:** Đạt M2; không vẽ toàn bộ history ngoài viewport; hover ngoài data không trả nến tùy ý. Sliding Window không còn nhiệm vụ bắt buộc chính.

### Thành viên 3 — Phát — Segment Tree và oracle

- **Deliverables:** Custom tree min low/max high/sum volume; scan baseline; tests interval/update/capacity.
- **Học trước:** `segment tree range minimum maximum sum point update`, `half open interval identity element`.
- **Bài tập:** Tree trên 7 phần tử, so mọi đoạn với scan rồi cập nhật từng điểm.
- **File/API dự kiến:** `src/algorithms/segment_tree.py` — `SegmentTree`, `query(left, right)`, `update(index, candle)`, `append(candle)`; `src/algorithms/range_scan.py` — `scan_range(...)`; dùng `RangeStats` trong interfaces.
- **Done:** Đạt M3, đủ ba đại lượng; empty/invalid intervals rõ ràng; không gọi append có rebuild là worst-case O(log N).

### Thành viên 4 — Nam (Lead) — Integration, replay, benchmark

- **Deliverables:** CLI/app entry points, GUI shell, replay controller, end-to-end checks, benchmark harness, tài liệu/review.
- **Học trước:** `Python argparse pytest tutorial`, `PyQt6 QTimer tutorial`, `Python perf_counter tracemalloc benchmark`.
- **Bài tập:** CLI in 5 nến, timer phát lần lượt 5 record, đo scan và tree cùng input.
- **File/API dự kiến:** `src/main_cli.py` — `run_cli_demo(csv_path: str)`; `src/main.py`; `src/ui/main_window.py`; `src/core/replay.py` — `ReplayController`; `benchmarks/benchmark_queries.py` — `run_benchmarks(...)`.
- **Done:** Entry points chạy theo README, replay không lộ tương lai, checks toàn luồng đúng; phép đo tái lập. Mỗi role vẫn sở hữu test của mình.

Các file/API mới trên đây là kế hoạch, chưa phải implementation đã tạo.

## 4. Phân công M1 — task giao cho từng thành viên

**Mục tiêu M1:** CSV synthetic nhỏ → Candle hợp lệ → CLI hiển thị tóm tắt và có hướng dẫn chạy lại. **Hiện tại chỉ Hưng và Nam triển khai chính.** Phát và Dũng chưa được giao task kiểm thử riêng ở M1; có thể ôn kiến thức cho Segment Tree và GUI ở mốc sau.

Các task dưới đây được giao theo tên trong roadmap; chưa phải GitHub Issues và chưa gán tài khoản GitHub. Nhánh là tên đề xuất, chưa xác nhận đã tồn tại. Mỗi người đọc `docs/interfaces.md` và `CONTRIBUTING.md` trước khi làm.

| Task | Người phụ trách | Nhiệm vụ và file/đầu ra | Phụ thuộc | Trạng thái |
| --- | --- | --- | --- | --- |
| M1-01A — Làm ngay | **Hưng** | Tạo `src/core/candle.py`: `@dataclass(frozen=True)` với timestamp: int và open/high/low/close/volume: float. Thêm demo trong khối `if __name__ == "__main__"` | Đọc Candle contract | [ ] Chưa nghiệm thu |
| M1-03A — Làm ngay khi import được Candle | **Nam** | Tạo `src/main_cli.py`; import Candle của Hưng, tạo 3 nến mẫu, in mỗi nến một dòng và số nến bằng `len()` | M1-01A | [ ] Chưa nghiệm thu |
| M1-02A — Giao sau lượt đầu | **Hưng** | Viết `load_candles(path) -> list[Candle]` trong `src/core/csv_loader.py`, đọc fixture chung bằng thư viện `csv` | M1-01A chạy được | [ ] Chưa nghiệm thu |
| M1-03B — Giao sau lượt đầu | **Nam** | Thay danh sách viết sẵn bằng kết quả loader; in đủ 12 nến mẫu | M1-02A | [ ] Chưa nghiệm thu |
| M1-01B / M1-02B — Hoàn thiện dữ liệu | **Hưng** | Thêm validation theo interfaces, lỗi có số dòng; viết tests model/CSV từng trường hợp | Loader cơ bản chạy được | [ ] Chưa nghiệm thu |
| M1-03C / M1-05 — Hoàn thiện CLI | **Nam** | Nhận đường dẫn CSV; thống kê min low/max high/sum volume; xử lý lỗi/empty; tests CLI và README hướng dẫn chạy | Data validation ổn định | [ ] Chưa nghiệm thu |

### Cách giao từng bước và nghiệm thu

**Chỉ giao lượt đầu M1-01A và M1-03A ngay bây giờ.** Chạy được rồi mới giao bước tiếp; không yêu cầu người mới giải quyết toàn bộ bảng một lần.

- **Hưng, bước đầu:** Học `Python dataclass cơ bản`, khai báo đủ sáu trường. Từ repo root chạy `python -m src.core.candle` (hoặc `python3`). Demo tạo một Candle với timestamp 1704067200, open 100, high 105, low 98, close 103, volume 1000; in đối tượng và close. Import từ module khác không tự in demo. Gửi Nam file, lệnh và output. Type hints chưa phải validation; phần kiểm tra dữ liệu làm ở bước sau.
- **Nam, bước đầu:** Học import/list/for/f-string; dùng đúng class của Hưng. Chạy `python -m src.main_cli` thấy 3 nến và số lượng 3; không tạo class Candle thứ hai.
- **Hưng, loader cơ bản:** Dùng [CSV chung 12 nến](tests/fixtures/candles_valid.csv) và [hướng dẫn](tests/fixtures/README.md), không tự tìm dữ liệu ngoài. Loader chuyển timestamp thành int, năm trường còn lại thành float và trả 12 Candle. Đây chưa phải loader hoàn thiện cho mọi input lỗi.
- **Nam, tích hợp:** Dùng loader thật, in dữ liệu đọc từ fixture; không viết loader thứ hai. Đối chiếu số nến và các trường với file CSV.
- **Trước khi đóng M1:** Hưng thêm tests/validation cho numeric hữu hạn, OHLC hợp lệ, volume không âm, empty/single-row, malformed, duplicate/out-of-order và lỗi theo dòng. Nam thêm CLI arguments, stats bằng scan, empty/error handling, exit status khác 0 khi lỗi và tests CLI. Hai người kiểm tra chéo, ghi lệnh thực chạy vào README. Fixture có min low 98, max high 113, tổng volume 13600 để đối chiếu.

Không giao người kiểm thử chuyên trách ở bước đầu, nhưng Hưng/Nam vẫn phải kiểm tra code mình; các acceptance criteria M1 ở mục 2 vẫn áp dụng trước nghiệm thu toàn mốc.

### Nhánh và trình tự phối hợp

1. **Hưng + Nam** chốt API theo interfaces; mọi thay đổi contract phải trao đổi.
2. **Hưng:** `feature/m1-csv-loader`; **Nam:** `feature/m1-cli-summary`. Commit nhỏ, bảo toàn code cũ; tích hợp qua PR review, không sao chép module giữa hai nhánh.
3. **Phát và Dũng:** chưa có task implementation/kiểm thử riêng trong lượt đầu M1. Phát ôn list/min/max trước Segment Tree; Dũng ôn class/tọa độ trước QPainter. Phần học này không chặn Hưng/Nam.
4. **Nam/Lead** đối chiếu acceptance criteria và review trước merge; nhờ thành viên khác review PR của Nam khi sẵn sàng. Không coi hoàn thành một task là hoàn thành cả M1.

Không gán hạn ngày tùy ý khi chưa biết deadline môn học. Mỗi check-in ghi task đang làm, PR/commit, checks thực tế, blocker và bước tiếp theo. Sau M1, Dũng chủ trì chart M2; Phát chuẩn bị cây M3, Hưng tiếp tục custom buffer M3.

## 5. Check-in và bước tiếp theo

Mỗi check-in: demo phần chạy được, tests đã chạy, blocker, thay đổi contract và PR tiếp theo. Tick khi đạt nghiệm thu, không dựa vào số file/commit.

**Nhiệm vụ implementation tiếp theo duy nhất: M1 — Candle model + CSV loader nhỏ + CLI summary.** Bổ sung rubric/deadline sớm; chưa biết vẫn có thể chốt contracts và fixture.

Xem [CONTRIBUTING.md](CONTRIBUTING.md) cho workflow và [báo cáo nhóm](docs/team_plan_report.md) cho việc chuyển kế hoạch.
