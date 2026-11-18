# Interactive Stock Chart Engine — Dự án DSA

Dự án đại học của nhóm 4 thành viên: xây biểu đồ nến OHLCV bằng **Python + PyQt6/QPainter**, sử dụng cấu trúc dữ liệu tự cài đặt và đánh giá bằng kiểm thử, lập luận và phép đo tái lập.

## Trạng thái hiện tại

**Cập nhật 18/11/2026:** PR #3/#4 đã merge Candle cơ bản, CSV loader và CLI vào main. Bản hoàn thiện M1 này bổ sung validation tại model, thống kê CLI và kiểm thử; chờ review/merge qua PR riêng.

- Đã có: Candle bất biến và validation, CSV loader báo lỗi theo dòng, fixture synthetic, CLI in bảng và thống kê toàn bộ dữ liệu.
- Đã chạy: 19 tests bằng unittest, gồm model/CSV và CLI subprocess. Xem [báo cáo M1](docs/m1_completion.md).
- Chưa có: GUI, custom DSA tích hợp, replay hoặc benchmark. Các file scaffold tương ứng không phải tính năng đã hoạt động.
- Prototype Ring Buffer trên nhánh cũ vẫn dùng deque/PyQt5, cần điều chỉnh ở M3.
- CI workflow vẫn rỗng. Chưa xác nhận chạy lại trên máy riêng của Hưng/Nam; không gọi kiểm tra trên máy agent là xác nhận của thành viên.

## Mục tiêu bản phát hành đầu

- Một mã và một timeframe intraday; CSV chuẩn hóa thành UTC Unix seconds.
- Candle model độc lập Qt, CSV validation và CLI summary.
- Custom candles, axes, pan/zoom/hover và visible-range clipping.
- **Custom Segment Tree:** min low, max high, tổng volume trên khoảng `[left, right)`.
- **Custom Ring Buffer bằng mảng vòng:** lưu dữ liệu gần đây có giới hạn; full history lưu riêng.
- Offline replay có play/pause, restart và speed; không gọi simulator là nguồn giá thị trường thật.
- Test tính đúng và benchmark có baseline.

Khi nến quá dày, gom OHLCV: open đầu, max high, min low, close cuối, tổng volume. LTTB không thay thế phép gom nến này.

## Lộ trình M0–M6

| Mốc | Kết quả chính |
| --- | --- |
| M0 | Tài liệu và contracts thống nhất |
| M1 | Candle + CSV loader + CLI nhỏ |
| M2 | Chart khoảng 100 nến có tương tác |
| M3 | Custom Ring Buffer/Segment Tree, tích hợp vào tính năng |
| M4 | Replay và cập nhật tăng dần |
| M5 | Gom OHLCV, benchmark và báo cáo |
| M6 | Extension tùy chọn |

Test đi cùng mỗi mốc. GUI nhỏ thuộc bản đầu, không còn là bonus cuối dự án. Xem [ROADMAP.md](ROADMAP.md) để biết dependencies, phân công và nghiệm thu.

## Ngoài phạm vi bắt buộc

Nguồn trade thật, tạo nến từ trade, nhiều mã/timeframe, Quadtree, LTTB cho đường close, undo/redo, rolling-window analytics và cache nâng cao. **Nếu rubric bắt buộc cấu trúc nào, nhóm phải đưa lại vào kế hoạch.** Rubric và hạn nộp chưa được cung cấp.

## Thiết lập và chạy

M1 dùng Python 3.10+ và thư viện chuẩn; **không cần pip install, PyQt6 hoặc pandas** để chạy CLI/tests này. Cài Python, lấy repository và mở terminal tại thư mục có README.md và src/. Dùng `python3` thay `python` nếu máy yêu cầu.

Có thể tạo môi trường riêng (không bắt buộc):

```bash
python -m venv .venv
```

Kích hoạt trên Linux/macOS: `source .venv/bin/activate`; trên Windows PowerShell: `.venv\Scripts\Activate.ps1`. Nếu không kích hoạt được, có thể dùng Python đã cài trực tiếp cho các lệnh dưới.

```bash
python -m src.main_cli
python -m src.main_cli tests/fixtures/candles_valid.csv
python -m src.main_cli tests/fixtures/candles_valid.csv --limit 0
python -m unittest discover -s tests -v
```

Không truyền đường dẫn: dùng 3 nến mẫu. Với fixture: đọc 12 nến, mặc định chỉ in 10 dòng; `--limit 0` in hết, hoặc `--limit 2` chỉ xem 2 dòng. **Thống kê luôn tính trên toàn bộ dữ liệu**, không phải phần xem trước:

```text
Số nến: 12
Timestamp đầu (UTC Unix seconds): 1704067200
Timestamp cuối (UTC Unix seconds): 1704067860
Min low: 98.00
Max high: 113.00
Tổng volume: 13600.00
```

CSV dùng UTF-8 và header `timestamp,open,high,low,close,volume`; xem [contracts](docs/interfaces.md). File rỗng/chỉ header thông báo không có dữ liệu; một nến vẫn có thống kê. CSV lỗi, file không tồn tại hoặc encoding sai: thông báo qua stderr, exit status 1. Đối số không hợp lệ: argparse báo lỗi, exit status 2. Chạy thành công: status 0. Import module không tự chạy demo.

Model từ chối timestamp không phải int, bool/số không hữu hạn ở giá/volume, OHLC sai và volume âm. Giá âm, flat price và volume 0 vẫn được phép. Loader bổ sung validation header/thứ tự và số dòng vào lỗi. Tests dùng unittest, cũng tương thích pytest khi được cài. Workflow `.github/workflows/python-tests.yml` vẫn rỗng, chưa chạy CI. Stack GUI sau M1 vẫn PyQt6.

Các file scaffold khác trong `src/`, `tests/` được giữ; tên file không chứng minh tính năng tồn tại. Dataset AAPL/BTC hiện ở nhánh prototype; demo dùng fixture tổng hợp trong `tests/fixtures/`.

## M2 desktop setup (English)

The M2 setup adds an **empty window**, not a working candle chart. M1 remains usable without Qt. In an activated virtual environment, run from the repository root:

```bash
python -m pip install -r requirements-gui.txt
python -m src.main
```

Expected: a window titled `Stock Chart — M2`, initially 960 × 600. Closing the window ends the application. Run GUI commands on a graphical desktop; offscreen testing does not confirm on-screen appearance.

See [Nam's setup and Dũng's first task](docs/m2_setup_and_dung_task.md) for environment setup, the drawing checklist, and handoff instructions. Primary-source findings are recorded in [M2 GUI research](docs/m2_gui_setup_research.md).

## Tài liệu nhóm

- [M2 setup and Dũng's first drawing task (English)](docs/m2_setup_and_dung_task.md)
- [Báo cáo hoàn thiện và cách xác nhận M1](docs/m1_completion.md)
- [Lộ trình](ROADMAP.md)
- [Báo cáo cho cả nhóm](docs/team_plan_report.md)
- [So sánh nghiên cứu](docs/research_comparison.md)
- [Hợp đồng module](docs/interfaces.md)
- [Complexity và benchmark](docs/complexity_analysis.md)
- [Quy trình Git](CONTRIBUTING.md)
