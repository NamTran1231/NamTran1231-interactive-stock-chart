# Báo cáo cho nhóm — Điều chỉnh kế hoạch Stock Chart

**Ngày:** 14/11/2026. **Đối tượng:** Chủ dự án và 4 thành viên. Chủ dự án đã chấp thuận M0–M6 và xuất bản tài liệu qua nhánh/PR riêng; main được cập nhật sau review/merge.

## 1. Kết luận

Kế hoạch mới tốt hơn về data semantics, tích hợp và minh họa giá trị DSA. Đổi lại, GUI nhỏ bắt buộc nên không thể nói luôn nhẹ hơn. Độ phù hợp môn học phụ thuộc rubric/deadline chưa cung cấp.

Mục tiêu: một ứng dụng Python/PyQt6 vẽ OHLCV cho một mã/một timeframe, CSV + offline replay, custom Ring Buffer/Segment Tree, tests và phép đo tái lập. Không cam kết điểm số hoặc 60 FPS khi chưa đo.

## 2. Trạng thái GitHub

Sau fetch: `main` ở `6a4c245`, Ring Buffer ở `d4f3a5a`; ba nhánh Stage 1 khác ở scaffold `6a4c245`.

- Main có Python/test/workflow/report rỗng; chưa có requirements, CLI, benchmark hoặc app chạy được.
- Nhánh Ring Buffer có buffer, simulator, 2 dataset, downloader, 3 test và generated `.pyc` được track. Chưa merge; lần rà soát này chưa chạy test/benchmark.
- Buffer bọc deque, chưa custom circular array. Simulator PyQt5/pandas chưa khớp PyQt6/model độc lập Qt. Import `from ring_buffer import RingBuffer` cần xem lại khi chạy package.
- Commit `thay đổi`, `chuyển tiếng việt sang tiếng anh` chưa Conventional Commits. Đánh giá trước đây “100% đúng” không chính xác: đúng branch name không xác nhận code/test đạt nghiệm thu.

## 3. Khác biệt và mục tiêu

| Trước | Sau |
| --- | --- |
| Stage 1 DSA, Stage 2 đo, Stage 3 GUI bonus | M1 dữ liệu, M2 GUI nhỏ, M3 DSA, M4 replay, M5 đo; M0 docs/M6 optional |
| Module riêng rồi tích hợp cuối | Contracts và lát cắt chạy được sớm |
| Sliding Window bắt buộc, Quadtree/LTTB trong README | Optional theo rubric; index hover/OHLCV grouping |
| Buffer dễ lẫn full history | Recent retention tách history |
| Simulation gọi real-time | Gọi offline replay; live feed để sau |
| Benchmark chứng minh Big-O | Lập luận Big-O, đo thực nghiệm có baseline |

| Mốc | Nhóm cần đạt |
| --- | --- |
| M0 | Docs/contracts/status thống nhất |
| M1 | CSV thành Candle, CLI summary, lỗi rõ ràng |
| M2 | Khoảng 100 nến, axes/pan/zoom/hover và xử lý biên |
| M3 | Custom buffer/tree đúng với oracle, chart dùng tree |
| M4 | Replay controls, update rules đúng, không lộ future bars |
| M5 | Grouping đúng, đo load/query/update/render riêng |
| M6 | Extension vừa sức, có test và lý do |

Test đi cùng mọi mốc, không đợi M5. Nghiệm thu chi tiết ở [ROADMAP](../ROADMAP.md).

## 4. Việc của từng người

**Cập nhật 15/11/2026:** Nam đã xác nhận tên theo vai trò: Hưng (1), Dũng (2), Phát (3), Nam (4/Lead).

| Người | Trách nhiệm mới | Bước gần nhất |
| --- | --- | --- |
| 1 — Hưng | Candle/CSV/Ring Buffer | M1 model/loader/fixture; sau đó cải tiến deque thành mảng vòng |
| 2 — Dũng | Rendering/coordinates/interactions | Học transform/QPainter, chart nhỏ theo Candle contract |
| 3 — Phát | Segment Tree/scan oracle | Chốt RangeStats, query/update tests; tích hợp M3 |
| 4 — Nam (Lead) | CLI/integration/replay/benchmark/docs | CLI M1, end-to-end checks, điều phối review |

Role 2 thay đổi nhiều nhất từ Sliding Window sang GUI. Mỗi người tự test module và review chéo, không giao mọi test cho role 4. Deadline cụ thể lập sau khi có hạn nộp.

## 5. Git và bảo toàn đóng góp

Nhánh mới theo task/milestone (`feature/m1-csv-loader`, `feature/m2-chart-canvas`), PR nhỏ vào main. Giữ code/commits/branches cũ; không force-push hoặc xóa nhánh thành viên. Trao đổi với tác giả để chuyển phần hữu ích của prototype qua PR có test, không merge toàn bộ chỉ vì tên nhánh đúng. Xem [CONTRIBUTING](../CONTRIBUTING.md).

## 6. Tài liệu đã điều chỉnh

- `README.md`: trạng thái thật, scope release, optional, chưa có command demo xác minh.
- `ROADMAP.md`: M0–M6, dependencies, acceptance criteria, 4 roles và học trước.
- `CONTRIBUTING.md`: milestone/task branches và chuyển tiếp.
- `docs/interfaces.md`: data, CSV, ranges, buffer, replay và ownership.
- `docs/research_comparison.md`: nguồn brief, retained/deferred và giới hạn bằng chứng.
- `docs/complexity_analysis.md`: target, overlooked costs, protocol; results chưa đo.
- `docs/team_plan_report.md`: báo cáo này.

Chỉ sửa tài liệu; không triển khai backlog/dependencies/CI. File handoff người dùng cung cấp được giữ nguyên ngoài commit xuất bản.

## 7. Checks và điều kiện còn mở

Đã đọc brief, roadmap, contributing và prototype từ remote; kiểm tra working tree trước sửa. Bản docs được kiểm tra whitespace/diff và local Markdown links trước commit. Không công bố implementation tests pass hay benchmark chưa chạy.

Nguồn nghiên cứu dẫn từ handoff, chưa kiểm tra lại API trực tiếp trong đợt này; phải đọc trước implementation. Còn mở: rubric/số cấu trúc bắt buộc, deadline, benchmark machine, daily/intraday adapters.

**Implementation tiếp theo duy nhất: M1 — normalized Candle + CSV loader nhỏ + CLI summary, synthetic fixture và input tests.** Không tự khởi động toàn bộ backlog.
