# Hợp đồng tích hợp — bản đầu

Đây là đặc tả dự kiến, không phải API đã chạy. Model/algorithms độc lập Qt. Tên class có thể đổi, semantics phải thống nhất.

## Candle và CSV

`Candle(timestamp: int, open: float, high: float, low: float, close: float, volume: float)` là record bất biến dự kiến. Timestamp **UTC Unix seconds**, đầu bucket intraday; một mã/một timeframe. Daily session handling để sau.

- CSV UTF-8, header `timestamp,open,high,low,close,volume`; timestamp chuỗi số nguyên Unix seconds. Adapter explicit cho nguồn khác, không đoán date/timezone.
- Giá/volume hữu hạn; volume >= 0; `low <= min(open, close)`, `high >= max(open, close)`, `low <= high`. Không áp quy tắc giá luôn dương.
- Reject malformed/missing fields, duplicate và out-of-order timestamp. `ValueError` có số dòng vật lý (header dòng 1), field/lý do; lỗi I/O giữ loại lỗi gốc.
- File rỗng hoặc chỉ header hợp lệ trả `[]`; single-row trả một Candle; header sai gây lỗi.
- `load_candles(path: str) -> list[Candle]`; fixture đầu là synthetic xác định, không phụ thuộc download.
- CSV trường `Date` trong prototype cần adapter và session policy; chưa tương thích mặc định với intraday contract.

## History, updates, replay

- History list tăng nghiêm ngặt timestamp, không mất khi buffer overwrite.
- Initial load validate rồi build indexes một lần. Incoming candle hợp lệ: cùng latest timestamp replace latest; mới hơn append; cũ hơn reject và count/log. Historical corrections để sau.
- Replay có source history riêng và cursor. Active prefix chỉ chứa bars đã tiết lộ; chart/stats không được đọc future bars. Restart reset cursor, active indexes và buffer, giữ source history.
- Historical mode xem toàn bộ history; replay mode điều hướng phần đã tiết lộ.

## Range queries

`RangeStats(min_low: float, max_high: float, volume_sum: float)`; zero-based **`[left, right)`**. `query(left, right) -> RangeStats | None`: empty hợp lệ trả `None`; `left < 0`, `right > n`, `left > right` gây `IndexError`. `update(index, candle)` chỉ index tồn tại và không đổi timestamp; `append(candle)` chỉ timestamp mới hơn.

- Merge: min low, max high, sum volume; empty node là identity, không dùng giá 0 làm min/max mặc định.
- Build O(N), query/point update O(log N), auxiliary memory O(N).
- Capacity lũy thừa hai; đầy thì nhân đôi/rebuild O(N). Append thường O(log N), gặp expansion O(N), amortized O(log N), không phải worst-case O(log N) mọi lần.
- `scan_range` cùng semantics làm oracle; fractional volume so với tolerance.

## Ring Buffer

`RingBuffer(capacity: int)`: nguyên dương, sai gây `ValueError`; list cấp phát trước, tự quản lý index/size. `push(candle) -> None`, `get_all() -> list[Candle]` cũ→mới, `is_full() -> bool`, `clear() -> None`.

Overwrite-oldest để retention; full history riêng. Push O(1), snapshot O(K), clear đơn giản O(K) để bỏ tham chiếu; slot memory O(capacity). Không dùng deque thay DSA; giữ array không có nghĩa Python objects không allocation.

Bản đầu không dùng như pending ingestion queue và không mặc định thread-safe. Queue tương lai cần backpressure/overflow reporting, không silently drop dữ liệu cần tổng hợp.

## Rendering và aggregation

Viewport → visible indices → range query → visible geometry. Flat prices có padding; zero viewport không chia cho 0; clamp zoom và giữ world position dưới cursor. Hover dùng index hoặc timestamp binary search; ngoài biên không trả nến tùy ý.

Dense grouping theo index toàn cục: nhóm `j` là `[j*g, (j+1)*g)`, clamp theo active data. Open đầu, max high, min low, close cuối, sum volume; timestamp nhóm là timestamp nến đầu. Hover ghi rõ aggregate/gốc. Đây không phải calendar-aligned timeframe resampling; gap/session policy để sau.

## Ownership và scheduling

GUI thread sở hữu state/painting; QTimer cho replay nhỏ. Worker chỉ thêm khi có blocking I/O/CPU đã xác định, gửi event/batch qua signal; không cùng mutate container nếu chưa có synchronization. Coalesce repaint được nhưng không mất event cần cho dữ liệu đúng.
