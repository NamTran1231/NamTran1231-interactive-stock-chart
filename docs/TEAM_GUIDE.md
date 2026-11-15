# Hướng dẫn bắt đầu cho 4 thành viên và AI agent

## 1. Nhóm đang ở đâu?

**Tại thời điểm viết guide (14/11/2026): M0 đã merge qua PR #1; công việc tiếp theo là M1.** Chưa có xác nhận nghiệm thu M1. Trạng thái về sau xem trong ROADMAP và PR đã merge, không suy ra từ tên nhánh hoặc file đã tồn tại.

- **M0:** thống nhất tài liệu và contracts.
- **M1 hiện tại:** CSV nhỏ → Candle hợp lệ → CLI in kết quả, kèm test và hướng dẫn chạy.
- **M2:** chart nhỏ có tương tác.
- **M3:** custom Ring Buffer và Segment Tree, tích hợp chart.
- **M4:** offline replay.
- **M5:** grouping, benchmark và báo cáo.
- **M6:** mở rộng tùy chọn.

**Mục 3 của ROADMAP mô tả vai trò toàn dự án, không phải danh sách phải hoàn thành hết trong M1.** Test đi cùng từng mốc; không đợi M5 mới test.

## 2. Vào GitHub thì đọc ở đâu?

Mở [repository](https://github.com/NamTran1231/NamTran1231-interactive-stock-chart), chọn tab **Code**, chọn nhánh **main** để xem kế hoạch đã thống nhất. Đọc theo thứ tự:

| Thứ tự | File | Đọc để biết gì? |
| --- | --- | --- |
| 1 | [README.md](../README.md) | Mục tiêu, trạng thái thật, tính năng bắt buộc/tùy chọn |
| 2 | [ROADMAP.md — mục 2](../ROADMAP.md#2-timeline-theo-dependencies-và-check-in) | Mốc hiện tại, người chủ trì và acceptance criteria |
| 3 | [ROADMAP.md — mục 3](../ROADMAP.md#3-đúng-4-vai-trò-và-đầu-ra) | Vai trò của mình trong toàn dự án, file/API dự kiến và học trước |
| 4 | [docs/interfaces.md](interfaces.md) | Quy định chung phải đọc trước khi code |
| 5 | [CONTRIBUTING.md](../CONTRIBUTING.md) | Tạo nhánh, commit, PR và review |

Đọc thêm khi cần:

- [Báo cáo nhóm](team_plan_report.md): vì sao đổi kế hoạch, phân công cũ/mới khác nhau thế nào.
- [So sánh nghiên cứu](research_comparison.md): nguồn tham khảo và quyết định giữ/hoãn thuật toán.
- [Complexity và benchmark](complexity_analysis.md): phương pháp đo, không phải kết quả đã đo.

**Xem code đang chờ duyệt:** tab **Pull requests** → chọn PR → **Files changed**. Code trên feature branch chưa merge không phải code đã được chấp nhận trên main. Tab **Actions** chỉ là bằng chứng test nếu có workflow thực sự chạy và kết quả; file workflow rỗng không phải CI hoạt động.

## 3. Checklist M1 cho từng người

Phân công theo tên đã được Nam xác nhận:

| Vai trò | Thành viên | Trách nhiệm chính |
| --- | --- | --- |
| 1 | Hưng | Candle, CSV ingestion, custom Ring Buffer |
| 2 | Dũng | QPainter chart, tọa độ, pan/zoom/hover |
| 3 | Phát | Custom Segment Tree, range queries, scan oracle |
| 4 / Lead | Nam | CLI, integration, replay, benchmark, điều phối và review/merge PR |

Hưng và Phát tiếp tục chuyên môn cũ. Dũng chuyển từ Sliding Window sang GUI; Sliding Window là tùy chọn nếu rubric không bắt buộc. Ở M1, Hưng/Nam triển khai chính, Dũng/Phát review và chuẩn bị phần tiếp theo.

### Thành viên 1 — Hưng — Candle, CSV và dữ liệu mẫu

**Mục tiêu hiện tại:** làm nền tảng dữ liệu cho CLI và chart.

- [ ] Đọc phần Candle/CSV trong `docs/interfaces.md`, chốt API với thành viên 4.
- [ ] Xây Candle độc lập Qt: timestamp, open, high, low, close, volume.
- [ ] Viết `load_candles(path: str) -> list[Candle]` và fixture synthetic nhỏ, xác định.
- [ ] Test dữ liệu hợp lệ, file rỗng/một dòng, dữ liệu lỗi, timestamp trùng và sai thứ tự; lỗi có số dòng/lý do.
- [ ] Mở PR để review trước khi tích hợp.

File dự kiến: `src/core/candle.py`, `src/core/csv_loader.py`, `tests/test_csv_loader.py`, fixture dưới `tests/fixtures/`.

Nhánh đề xuất: `feature/m1-csv-loader`. **Custom Ring Buffer được nghiệm thu ở M3**, không cần hoàn thành trong task M1 này. Prototype cũ được giữ và cải tiến ở task riêng.

### Thành viên 4 — Nam (Lead) — CLI và tích hợp M1

**Mục tiêu hiện tại:** người khác chạy được demo từ CSV qua terminal.

- [ ] Thống nhất cách gọi loader và cách xử lý lỗi với thành viên 1.
- [ ] Viết CLI nhận đường dẫn CSV, hiển thị bảng/tóm tắt dễ đọc.
- [ ] Có thể phát triển phần hiển thị bằng Candle mẫu trong lúc loader đang được review; không viết loader thứ hai khác contract.
- [ ] Test luồng CLI thành công và lỗi; bổ sung dependencies cần thiết và hướng dẫn setup/demo đã chạy thực tế.
- [ ] Kiểm tra tích hợp sau khi loader merge, mở PR và nhờ người khác chạy theo README.

File dự kiến: `src/main_cli.py`, test CLI và hướng dẫn trong `README.md`. Không cài Qt chỉ để chạy CLI nếu chưa cần.

Nhánh đề xuất: `feature/m1-cli-summary`. Thành viên 4 điều phối test chung; từng người vẫn tự test module mình.

### Thành viên 2 — Dũng — Chuẩn bị chart M2

**Mục tiêu hiện tại:** hiểu dữ liệu sẽ vẽ và chuẩn bị kỹ năng, chưa cần hoàn thiện GUI trong M1.

- [ ] Review Candle contract với thành viên 1; làm rõ timestamp/giá trị đầu vào.
- [ ] Đọc yêu cầu M2; học QPainter, world↔screen, viewport và cursor-anchored zoom.
- [ ] Làm bài thử nhỏ vẽ 10 nến/đổi tọa độ nếu cần, tách khỏi implementation chính.
- [ ] Ghi câu hỏi hoặc vướng mắc để chốt trước khi tích hợp chart.

Nhánh implementation ví dụ khi bắt đầu M2: `feature/m2-chart-canvas`. Role chính đã chuyển từ Sliding Window sang rendering/interactions. Không tự đổi contract vì bài thử cần dữ liệu khác.

### Thành viên 3 — Phát — Chuẩn bị query M3

**Mục tiêu hiện tại:** thống nhất ý nghĩa truy vấn và chuẩn bị oracle.

- [ ] Đọc Candle, `RangeStats` và khoảng `[left, right)` trong interfaces.
- [ ] Chuẩn bị ví dụ min low/max high/sum volume tính tay để review contract.
- [ ] Thiết kế scan oracle và test query; có thể phát triển độc lập sau khi contract ổn định, phối hợp trước với nhóm.
- [ ] Học Segment Tree build/query/update và capacity expansion.

File tương lai: `src/algorithms/segment_tree.py`, `src/algorithms/range_scan.py`. Nhánh implementation ví dụ: `feature/m3-segment-tree`. Tree được tích hợp/nghiệm thu ở M3, không phải điều kiện kết thúc M1.

Các nhánh trên là **tên đề xuất**, không xác nhận đã được tạo. Mỗi task nhỏ dùng nhánh riêng; ownership không có nghĩa một người phải giữ một nhánh suốt dự án.

## 4. Cách bắt đầu làm việc trên máy

Trước tiên chạy `git status`. Nếu có thay đổi chưa commit, lưu công việc và xử lý với nhóm trước khi chuyển nhánh; không reset/clean để bỏ code.

Ví dụ thành viên 1, khi working tree sạch và nhánh task chưa tồn tại:

```bash
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c feature/m1-csv-loader
```

Nếu nhánh đã có trên remote thì checkout nhánh đó thay vì tạo lại. Nếu đang có code ở nhánh cũ, trao đổi với lead về cách chuyển commit; không xóa nhánh hoặc force-push của người khác.

Làm xong một thay đổi nhỏ, stage đúng file rồi commit/push; ví dụ:

```bash
git add src/core/candle.py
git commit -m "feat(data): define normalized candle model"
git push -u origin feature/m1-csv-loader
```

Mở PR vào `main`, ghi: làm gì, thuộc milestone nào, lệnh kiểm tra và kết quả thực tế, phần chưa làm. Không ghi test pass nếu chưa chạy. Không commit `.pyc`, `__pycache__`, môi trường ảo hoặc dữ liệu nhạy cảm.

## 5. Nếu dùng AI agent thì cho đọc gì?

Agent cần đọc **`AGENTS.md`** trước và các hướng dẫn được liên kết khi liên quan. Sau đó đọc README, ROADMAP, interfaces, CONTRIBUTING và code/test hiện có thuộc task. Không chỉ đưa mỗi đoạn “vai trò thành viên” vì agent có thể hiểu nhầm phải làm toàn bộ roadmap.

Tài liệu `Stock_Chart_Agent_Handoff.md` là brief nghiên cứu ban đầu, có thể chỉ tồn tại trên máy lead. Nó không thay thế contracts/kế hoạch đã merge; không yêu cầu các thành viên phải có file đó để bắt đầu.

### Prompt dùng chung — điền trước khi gửi

```text
Tôi là [Hưng / Dũng / Phát / Nam], thành viên [1/2/3/4] của dự án Stock Chart.
Milestone hiện tại: M1. Task được giao: [một đầu việc cụ thể].
Nhánh dự kiến/hiện tại: [tên nhánh].

Trước khi sửa code:
1. Đọc AGENTS.md và các hướng dẫn áp dụng.
2. Đọc README.md; ROADMAP.md mục 2 (M1 và nghiệm thu),
   mục 3 (vai trò của tôi); docs/interfaces.md; CONTRIBUTING.md.
3. Kiểm tra git status, nhánh hiện tại và code/test đã có.
   Nếu repo có thay đổi của người khác, giữ lại và không ghi đè.
4. Tóm tắt task và contract cần tuân thủ, chỉ ra blocker thực tế.

Chỉ triển khai task được giao. Không tự làm toàn bộ milestone/roadmap.
Không đổi stack hoặc contract liên module nếu chưa trao đổi.
Model/loader không phụ thuộc Qt; DSA cần tự cài đặt theo kế hoạch.
Thêm test phù hợp và chạy kiểm tra thực sự cho phần đã sửa.
Không tự commit, push, merge PR hoặc tạo issue khi chưa được yêu cầu.

Cuối cùng báo cáo: file đổi, hành vi đã làm, checks đã chạy và kết quả,
giới hạn còn lại, cách demo nếu có. Không nhận đã chạy test/benchmark
nếu chưa chạy; không đánh dấu M1 xong chỉ vì hoàn thành một module.
```

### Đầu việc mẫu để điền

| Người | Task nên giao agent lúc này |
| --- | --- |
| 1 — Hưng | “Xây Candle và CSV loader theo interfaces, fixture synthetic và input tests; chưa làm Ring Buffer/replay.” |
| 4 — Nam | “Xây CLI summary dùng API loader đã thống nhất, test CLI và hướng dẫn chạy; phối hợp dependency với PR thành viên 1.” |
| 2 — Dũng | “Đọc Candle contract và giải thích kế hoạch QPainter/world-screen cho M2; chỉ phân tích, chưa sửa implementation.” |
| 3 — Phát | “Review RangeStats và half-open ranges; đề xuất scan oracle và test cases; chỉ phân tích, chưa sửa implementation.” |

Nếu lead giao task chuẩn bị implementation riêng cho thành viên 2/3, sửa rõ phạm vi prompt và mở nhánh task tương ứng. Không dùng prompt M1 để tự bắt đầu M2–M6.

## 6. Check-in và kết thúc M1

Mỗi người báo bốn ý: **đã làm gì → kiểm tra thế nào → đang vướng gì → bước tiếp theo**; gửi link PR nếu có.

M1 hoàn thành khi CSV fixture nạp đúng, lỗi/edge cases có test, CLI chạy được, README có lệnh thật và một người khác chạy lại thành công. Lead kiểm tra các tiêu chí trong ROADMAP trước chuyển milestone. Rubric/hạn nộp chưa xác nhận phải được cập nhật khi nhóm nhận được.
