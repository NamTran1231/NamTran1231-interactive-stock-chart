# So sánh nghiên cứu và quyết định

Tổng hợp ngày 14/11/2026 từ brief `Stock_Chart_Agent_Handoff.md` và đối chiếu git remote. Mô tả nguồn dưới đây **kế thừa từ brief, chưa mở lại từng URL để xác minh độc lập trong đợt tài liệu này**. Chủ module cần kiểm tra API/version và ghi ngày truy cập trước implementation. Các nguồn không chứng minh mọi công ty dùng cùng kiến trúc.

| Nguồn | Hành vi được brief dẫn lại | Khuyến nghị thiết kế |
| --- | --- | --- |
| [S1 TradingView Datafeed](https://www.tradingview.com/charting-library-docs/latest/connecting_data/Datafeed-API/) | History/subscription riêng; live replace latest/append newer | Tách initial load và incremental update |
| [S2 Lightweight Charts](https://tradingview.github.io/lightweight-charts/docs/api/interfaces/ISeriesApi) | `setData` thay series, `update` append/replace latest | Không rebuild mỗi event; không trộn contract S1/S2 |
| [S3 PyQtGraph PlotDataItem](https://pyqtgraph.readthedocs.io/en/latest/api_reference/graphicsItems/plotdataitem.html) | Clipping/downsampling/optimized drawing paths | Giảm geometry; custom canvas phải tự triển khai |
| [S4 Highcharts grouping](https://www.highcharts.com/docs/stock/data-grouping) | Pixel-density grouping, OHLC grouping | Gom OHLCV thay LTTB cho candles |
| [S5 PyQtGraph example](https://github.com/pyqtgraph/pyqtgraph/blob/master/pyqtgraph/examples/customGraphicsItem.py) | QPainter/QPicture cache commands | Tiền lệ custom candles, không bảo đảm 300k performance |
| [S6 Qt threading](https://doc.qt.io/qt-6.8/threads-qobject.html) | Widgets main thread, worker trả kết quả | GUI sở hữu state; synchronization explicit |

## Giữ, thay, hoãn

| Cũ | Mới | Lý do của nhóm |
| --- | --- | --- |
| GUI bonus cuối | Chart nhỏ M2, DSA M3 | Tích hợp sớm, thấy giá trị DSA |
| Buffer kho chung | Retention riêng full history | Overwrite không làm mất navigation |
| Tree autoscale | Min low/max high/sum volume | Dùng cả selected-range stats |
| Quadtree hover | Index/binary search | Trục thời gian đã có thứ tự |
| LTTB nến | OHLCV grouping | Bảo toàn ý nghĩa tài chính |
| Sliding Window bắt buộc | Latest-K optional | Khác arbitrary interval; thêm khi có mục đích/rubric |
| QThread ngay | Timer replay trước | Giảm concurrency chưa cần |
| Nhiều patterns upfront | Module/contracts trước | Không thêm framework notification trùng lặp |
| Mượt/zero allocation như hiện có | Target đến khi đo | Dataset size không quyết định frame time |

Đây là quyết định thiết kế, không phải yêu cầu bắt buộc từ các thư viện. Chúng là reference, không là rendering dependencies; stack vẫn Python/PyQt6/QPainter.

Rubric, deadline, benchmark machine, CSV adapters chưa xác nhận. Daily datasets prototype cần chính sách session riêng. Nghiên cứu nguồn không chứng minh engine nhóm đạt 60 FPS; benchmark cũng không chứng minh Big-O.
