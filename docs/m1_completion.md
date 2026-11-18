# Báo cáo hoàn thiện M1 — 18/11/2026

## 1. Trạng thái

PR #3/#4 đã merge nền tảng Candle/CSV/CLI vào main tại `3590729`. Nhánh `feature/m1-completion` bổ sung phần còn lại: model validation, summary, preview limit và tests. **Code và kiểm tra trên máy agent đã hoàn thành; chờ Nam review/merge và xác nhận chạy lại trên máy nhóm.**

Phân công vẫn Hưng (model/CSV) và Nam (CLI/integration). Hưng tạo model ban đầu; agent hỗ trợ triển khai loader/CLI và phần hoàn thiện theo yêu cầu Nam. Không ghi các phần agent làm là đóng góp tự viết của thành viên khác. Phát/Dũng chưa có task kiểm thử chuyên trách M1.

## 2. Đầu ra đã có

| Thành phần | File | Hành vi |
| --- | --- | --- |
| Model | `src/core/candle.py` | Immutable; validate khi tạo trực tiếp: timestamp int, numeric finite, OHLC hợp lệ, volume >= 0 |
| Loader | `src/core/csv_loader.py` | UTF-8 CSV đúng header → list Candle; reject malformed, duplicate/out-of-order; lỗi theo dòng; giữ I/O errors |
| CLI | `src/main_cli.py` | Demo 3 nến hoặc CSV, bảng mẫu giới hạn dòng, stats toàn bộ dữ liệu, empty/error handling |
| Fixture | `tests/fixtures/candles_valid.csv` | 12 nến synthetic xác định, không tải ngoài |
| Kiểm thử | `tests/test_candle.py`, `tests/test_csv_cli.py` | Model trực tiếp và end-to-end CLI subprocess |

Model là nơi kiểm tra tính hợp lệ một nến; loader chỉ convert và bổ sung số dòng cho lỗi. Không duy trì hai bộ OHLC validation khác nhau. CLI thống kê bằng scan; không cần Segment Tree để hoàn thành M1.

## 3. Cách chạy lại

Tại repo root, Python 3.10+; không cần pip install. Có thể tạo venv theo README. Dùng `python3` thay `python` nếu máy yêu cầu:

```bash
python -m src.core.candle
python -m src.main_cli
python -m src.main_cli tests/fixtures/candles_valid.csv --limit 2
python -m src.main_cli tests/fixtures/candles_valid.csv --limit 0
python -m unittest discover -s tests -v
```

Kỳ vọng: demo model close 103; CLI mặc định 3 nến; CSV 12 nến. Khi --limit 2 chỉ in 2 dòng nhưng vẫn thống kê cả 12 nến:

```text
Số nến: 12
Timestamp đầu (UTC Unix seconds): 1704067200
Timestamp cuối (UTC Unix seconds): 1704067860
Min low: 98.00
Max high: 113.00
Tổng volume: 13600.00
```

--limit 0 in hết; giá trị âm/không nguyên gây argparse error (status 2). File lỗi/không tồn tại trả 1 và stderr rõ ràng; thành công trả 0. Empty/header-only không crash; single-row vẫn có summary.

## 4. Evidence và nghiệm thu

Trên máy agent Linux (kernel `7.0.0-43-generic`), Python **3.14.4**, đã chạy `python3 -m unittest discover -s tests -v`: **19 tests PASS**. Chưa chạy trên Python 3.10 hoặc OS khác trong đợt này. Có subtests cho nhiều field/giá trị lỗi, không tính mỗi subtest thành một test riêng. Lệnh CSV --limit 2 cho số liệu đúng bảng trên. Whitespace và 16 local Markdown link targets được kiểm tra trước commit.

Đã kiểm tra: frozen model, timestamp types (loại bool), mọi numeric field với NaN/infinity/nonnumeric, OHLC/negative volume, flat/negative price/zero volume; CSV empty/single-row/headers/columns/format/ordering; row-number errors; CLI preview không cắt summary, all rows, invalid limit, missing file, broken quotes/encoding và import không tự demo.

- [x] Fixture và load/validation không phụ thuộc GUI hay download.
- [x] CLI summary và sample table chạy được.
- [x] Tests model/CSV/CLI đạt trên máy agent.
- [x] README có lệnh setup/demo/test và expected output.
- [ ] Nam review/merge PR hoàn thiện.
- [ ] Hưng hoặc Nam chạy lại từ README trên máy mình, ghi OS/Python/commit/lệnh/output và kết quả vào PR.

Chưa có xác nhận chạy độc lập từ thành viên; không dùng automation trên máy agent để giả lập việc đó. CI vẫn là file workflow rỗng, không tuyên bố CI pass. Chưa benchmark hay đo tốc độ. GUI/DSA/replay thuộc các mốc sau.

## 5. Bước sau

Sau review/merge và chạy lại đạt, Nam cập nhật trạng thái M1 hoàn thành trong ROADMAP. M2 sẽ bắt đầu bằng QPainter chart nhỏ; chưa triển khai M2 trong bản thay đổi này. Rubric/deadline vẫn cần nhóm cung cấp.
