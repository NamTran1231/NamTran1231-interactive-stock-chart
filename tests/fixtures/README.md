# CSV mẫu dùng chung cho M1

## File cần dùng

**[candles_valid.csv](candles_valid.csv)** là dữ liệu tổng hợp (synthetic) do agent tạo để học và kiểm thử, **không phải dữ liệu thị trường thật**, không đại diện cho mã chứng khoán thực tế.

Cả nhóm dùng cùng file này; không cần mỗi người tự tìm hoặc tải dữ liệu từ bên ngoài. File theo hợp đồng trong [docs/interfaces.md](../../docs/interfaces.md).

## Cấu trúc

- 12 nến, một khoảng thời gian đầu vào là 1 phút.
- Từ **2024-01-01 00:00:00 UTC** đến **00:11:00 UTC**; timestamp là Unix seconds tại đầu mỗi phút, tăng 60 giây mỗi dòng.
- Header: `timestamp,open,high,low,close,volume`.
- Giá và volume đều hữu hạn; OHLC hợp lệ; volume không âm.
- Có nến tăng, giảm, và nến giá phẳng/volume 0 ở timestamp `1704067440`.
- Chỉ chứa dữ liệu hợp lệ. Fixture lỗi cho tests sẽ tạo riêng, không sửa file dùng chung thành dữ liệu lỗi.

| Trường | Ý nghĩa | Ví dụ ở dòng dữ liệu đầu |
| --- | --- | --- |
| timestamp | Thời điểm đầu nến (UTC Unix seconds) | 1704067200 |
| open | Giá mở cửa | 100 |
| high | Giá cao nhất | 105 |
| low | Giá thấp nhất | 98 |
| close | Giá đóng cửa | 103 |
| volume | Khối lượng | 1000 |

## Hưng dùng thế nào?

1. Task hiện tại trong Excel vẫn là tạo `Candle` và chạy thử. Có thể dùng dòng dữ liệu đầu làm ví dụ, chưa cần tự viết CSV loader ngay.
2. Khi được giao task loader, đọc file tại `tests/fixtures/candles_valid.csv` từ repo root bằng thư viện chuẩn `csv`.
3. Loader phải trả 12 đối tượng Candle; timestamp chuyển thành int, năm trường còn lại thành float.
4. Không đổi header sang Date/Open/High hoặc sửa timestamp thành chuỗi ngày vì sẽ lệch contract chung.

## Kết quả thống kê để đối chiếu

| Đại lượng | Giá trị mong đợi |
| --- | --- |
| Số nến | 12 |
| Timestamp đầu | 1704067200 |
| Timestamp cuối | 1704067860 |
| Min low | 98 |
| Max high | 113 |
| Tổng volume | 13600 |

Các giá trị này dành cho đối chiếu loader/CLI sau này, không phải kết quả benchmark. Nếu nhóm thay fixture, cần cập nhật cả bảng này.

## Lấy file trên GitHub

Mở `tests/fixtures/candles_valid.csv` ở nhánh chứa file → chọn **Raw** để xem nội dung CSV nguyên bản hoặc tải file. Khi PR được merge vào main, cập nhật repo sẽ có file đúng đường dẫn; không cần copy thủ công cho từng người.
