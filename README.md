# Interactive Stock Chart Engine — Dự án DSA

Dự án đại học của nhóm 4 thành viên: xây biểu đồ nến OHLCV bằng **Python + PyQt6/QPainter**, sử dụng cấu trúc dữ liệu tự cài đặt và đánh giá bằng kiểm thử, lập luận và phép đo tái lập.

## Trạng thái hiện tại

Đối chiếu remote ngày **14/11/2026**, trước bản sửa tài liệu này:

- `main` tại `6a4c245` chỉ có tài liệu và scaffold. Các file Python trong `src/`, `tests/`, workflow CI và báo cáo complexity rỗng.
- `feature/stage1-ring-buffer` tại `d4f3a5a` có prototype buffer, simulator, dataset và test, chưa merge. Buffer dùng `collections.deque`, simulator dùng PyQt5; cần điều chỉnh theo hợp đồng mới.
- Ba nhánh Stage 1 còn lại vẫn tại scaffold `6a4c245`.
- Chưa có ứng dụng hoàn chỉnh hay kết quả benchmark được xác minh trong đợt rà soát này.

**Bổ sung trong PR demo M1:** Candle của Hưng, CSV loader và CLI in bảng đã có implementation; xem lệnh chạy bên dưới. Các chức năng GUI, DSA, replay và benchmark dưới đây vẫn là mục tiêu phát triển, chưa phải hành vi đã chạy.

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

Demo M1 trong nhánh/PR này dùng Python 3.10+ và thư viện chuẩn, chưa cần cài Qt. Chạy từ thư mục gốc repository (dùng `python3` thay `python` nếu máy yêu cầu):

```bash
python -m src.main_cli
python -m src.main_cli tests/fixtures/candles_valid.csv
python -m unittest discover -s tests -p 'test_csv_cli.py' -v
```

Lệnh đầu in 3 nến mẫu; lệnh thứ hai đọc và in 12 nến synthetic. CLI nhận đường dẫn tùy chọn, báo lỗi qua stderr và exit status 1; file rỗng thông báo không có dữ liệu. Import module không tự chạy demo.

Demo này chưa phải M1 hoàn chỉnh: CLI chưa có thống kê tổng hợp, model Candle chưa tự validation khi được tạo trực tiếp. Loader đã kiểm tra dữ liệu CSV theo contract. Stack GUI dự kiến vẫn PyQt6; tests ở đây dùng unittest và cũng có thể chạy bằng pytest sau khi nhóm thiết lập dependency. `.github/workflows/python-tests.yml` vẫn là placeholder rỗng, chưa chạy CI.

Các file scaffold khác trong `src/`, `tests/` được giữ; tên file không chứng minh tính năng tồn tại. Dataset AAPL/BTC hiện ở nhánh prototype; demo dùng fixture tổng hợp trong `tests/fixtures/`.

## Tài liệu nhóm

- [Lộ trình](ROADMAP.md)
- [Báo cáo cho cả nhóm](docs/team_plan_report.md)
- [So sánh nghiên cứu](docs/research_comparison.md)
- [Hợp đồng module](docs/interfaces.md)
- [Complexity và benchmark](docs/complexity_analysis.md)
- [Quy trình Git](CONTRIBUTING.md)
