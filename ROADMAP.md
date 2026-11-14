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

### Thành viên 1 — Dữ liệu, CSV, Ring Buffer

- **Deliverables:** Candle độc lập Qt, loader validate, fixture synthetic, buffer mảng vòng tự quản lý index/size; full history riêng.
- **Học trước:** `Python dataclass CSV validation`, `circular buffer array head tail modulo`.
- **Bài tập:** Capacity 3, push 1–8 còn `[6, 7, 8]`; parse 3 nến và báo lỗi theo dòng.
- **File/API dự kiến:** `src/core/candle.py` — `Candle`; `src/core/csv_loader.py` — `load_candles(path: str) -> list[Candle]`; `src/core/ring_buffer.py` — `RingBuffer(capacity: int)`, `push(candle)`, `get_all()`, `is_full()`.
- **Done:** CSV đạt contracts; invalid capacity bị từ chối; wraparound đúng, push O(1), snapshot O(K). Cải tiến prototype hiện có; deque wrapper chưa phải DSA from scratch.

### Thành viên 2 — Rendering, tọa độ, interactions

- **Deliverables:** QPainter candles/axes, viewport/clipping, pan/zoom/hover; nối query tree ở M3.
- **Học trước:** `PyQt6 QPainter QWidget paintEvent`, `affine transform world screen coordinates`, `cursor anchored zoom`.
- **Bài tập:** Vẽ 10 nến, round trip world↔screen, zoom giữ điểm dưới cursor.
- **File/API dự kiến:** `src/core/coordinate_math.py` — `world_to_screen(...)`, `screen_to_world(...)`; `src/ui/chart_canvas.py` — `ChartCanvasWidget`, `paintEvent(self, event)`.
- **Done:** Đạt M2; không vẽ toàn bộ history ngoài viewport; hover ngoài data không trả nến tùy ý. Sliding Window không còn nhiệm vụ bắt buộc chính.

### Thành viên 3 — Segment Tree và oracle

- **Deliverables:** Custom tree min low/max high/sum volume; scan baseline; tests interval/update/capacity.
- **Học trước:** `segment tree range minimum maximum sum point update`, `half open interval identity element`.
- **Bài tập:** Tree trên 7 phần tử, so mọi đoạn với scan rồi cập nhật từng điểm.
- **File/API dự kiến:** `src/algorithms/segment_tree.py` — `SegmentTree`, `query(left, right)`, `update(index, candle)`, `append(candle)`; `src/algorithms/range_scan.py` — `scan_range(...)`; dùng `RangeStats` trong interfaces.
- **Done:** Đạt M3, đủ ba đại lượng; empty/invalid intervals rõ ràng; không gọi append có rebuild là worst-case O(log N).

### Thành viên 4 — Integration, replay, benchmark

- **Deliverables:** CLI/app entry points, GUI shell, replay controller, end-to-end checks, benchmark harness, tài liệu/review.
- **Học trước:** `Python argparse pytest tutorial`, `PyQt6 QTimer tutorial`, `Python perf_counter tracemalloc benchmark`.
- **Bài tập:** CLI in 5 nến, timer phát lần lượt 5 record, đo scan và tree cùng input.
- **File/API dự kiến:** `src/main_cli.py` — `run_cli_demo(csv_path: str)`; `src/main.py`; `src/ui/main_window.py`; `src/core/replay.py` — `ReplayController`; `benchmarks/benchmark_queries.py` — `run_benchmarks(...)`.
- **Done:** Entry points chạy theo README, replay không lộ tương lai, checks toàn luồng đúng; phép đo tái lập. Mỗi role vẫn sở hữu test của mình.

Các file/API mới trên đây là kế hoạch, chưa phải implementation đã tạo.

## 4. Check-in và bước tiếp theo

Mỗi check-in: demo phần chạy được, tests đã chạy, blocker, thay đổi contract và PR tiếp theo. Tick khi đạt nghiệm thu, không dựa vào số file/commit.

**Nhiệm vụ implementation tiếp theo duy nhất: M1 — Candle model + CSV loader nhỏ + CLI summary.** Bổ sung rubric/deadline sớm; chưa biết vẫn có thể chốt contracts và fixture.

Xem [CONTRIBUTING.md](CONTRIBUTING.md) cho workflow và [báo cáo nhóm](docs/team_plan_report.md) cho việc chuyển kế hoạch.
