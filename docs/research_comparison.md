# SO SÁNH KIẾN TRÚC & PHÂN TÍCH ĐÁNH ĐỔI CẤU TRÚC DỮ LIỆU

**Dự án:** Interactive TradingView Stock Chart Engine (DSA Python)  
**Tài liệu đối chiếu chuẩn ngành:** TradingView Lightweight Charts (`https://tradingview.github.io/lightweight-charts/`).

---

## 1. SO SÁNH KIẾN TRÚC VỚI TRADINGVIEW LIGHTWEIGHT CHARTS

**TradingView Lightweight Charts** là chuẩn mực công nghiệp mã nguồn mở cho biểu đồ tài chính hiệu năng cao trên nền Web (HTML5 Canvas). Bảng dưới đây đối chiếu kiến trúc hệ thống của dự án với Lightweight Charts:

| Tiêu chí Kiến trúc | TradingView Lightweight Charts (Web/TS) | Dự án Stock Chart Engine (Python/PyQt6) | Phân tích Đánh đổi |
| :--- | :--- | :--- | :--- |
| **Engine Đồ họa** | HTML5 Canvas 2D (tách 2 canvas: lớp dữ liệu & lớp crosshair/overlay) | PyQt6 `QWidget` + `QPainter` (C++ Qt6 bindings, tách `compute_visible_frame` và `paintEvent`) | Desktop Native `QPainter` tránh được độ trễ trình duyệt/DOM, nhưng phải kiểm soát số lượng Python-to-C++ draw calls qua decimation. |
| **Biến đổi Tọa độ** | TimeScale (index $\leftrightarrow$ x) & PriceScale (price $\leftrightarrow$ y, đảo trục) + Cursor-Anchored Zoom | `CoordinateTransformer` + `ViewportState` (4 padding tách nhãn giá & trục thời gian) | Hoàn toàn tương đồng về mô hình toán học Affine; bản Python tách riêng module thuần toán học để unit test độc lập. |
| **Auto-Fit Trục Giá Y** | Quét min/max trên các thanh hiển thị (hoặc phân đoạn theo bar spacing) | **`SegmentTree`** trả về `RangeStats(min_low, max_high, volume_sum)` trong $O(\log N)$ | `SegmentTree` cho tốc độ $O(\log N)$ bất biến kể cả khi zoom out toàn bộ $100{,}000+$ nến. |
| **Nén Dữ liệu theo Pixel** | Co độ rộng thân nến / gộp theo bar spacing khi thu nhỏ quá mức | **`aggregate_ohlcv_buckets`** (nến Nhật) + **`LTTBDecimator`** (đường chỉ báo) | Bảo toàn tuyệt đối cấu trúc OHLCV cho nến và hình thái đỉnh/đáy cho đường chỉ báo theo mật độ pixel màn hình. |
| **Crosshair Snapping** | Tra cứu trực tiếp theo chỉ số thời gian `x -> barIndex` (1D) | **`QuadTree`** 2D (`nearest(x, y, max_dist)`) + Branch-and-Bound | Chi phí dựng chỉ $O(M \log M)$ trên tập hiển thị, tổng quát hóa được cả hit-testing 2D cho điểm đánh dấu/chỉ báo phi tuyến. |
| **Giao tiếp & Lịch sử** | Event emitters nội bộ (`subscribeCrosshairMove`, `subscribeVisibleTimeRangeChange`) | **`EventBus`** (Observer Pattern) + **`CommandHistory`** (Command Pattern Undo/Redo) | Bổ sung khả năng Undo/Redo thao tác Pan/Zoom chuẩn ứng dụng Desktop chuyên nghiệp. |

---

## 2. ĐÁNH ĐỔI 1: CUSTOM `RingBuffer` VS `collections.deque` VS PYTHON `list`

Thành viên 1 sử dụng Custom Circular Array (`RingBuffer`) thay vì dùng sẵn `collections.deque(maxlen=K)` hay `list`:

| Tiêu chí | Custom `RingBuffer` (Mảng vòng cố định) | `collections.deque(maxlen=K)` (CPython) | Python `list` thông thường |
| :--- | :--- | :--- | :--- |
| **Cấu trúc Vật lý** | 1 mảng con trỏ liên tục cố định `[None] * K` | Danh sách liên kết đôi gồm các block 64 phần tử | Mảng động tự cấp phát dư (over-allocation) |
| **Thêm & Ghi đè khi đầy** | **$O(1)$ worst-case** (ghi đè tại `_write_idx`, cập nhật modulo) | $O(1)$ (tự pop đầu khi đầy `maxlen`) | **$O(N)$** nếu gọi `pop(0)` khi đầy; hoặc rò rỉ RAM nếu cứ `.append()` |
| **Truy cập phần tử thứ $i$** | **$O(1)$ thực sự** qua `(head + i) % K` | **$O(N)$** (phải duyệt qua các block liên kết) | $O(1)$ |
| **Ổn định Bộ nhớ (Streaming)** | Cấp phát đúng 1 lần khi `__init__`, không cấp phát block mới khi stream | Cấp phát/giải phóng block 64-item khi xoay vòng | Liên tục resize 1.125x nếu không giới hạn |
| **Giá trị Sư phạm DSA** | Nắm vững modulo wrap-around, tính `head` từ `write_idx`, thiết kế ring buffer cấp thấp | Che giấu hoàn toàn cơ chế con trỏ vòng bên dưới C | Không thể hiện được cấu trúc hàng đợi vòng cố định |

**Kết luận:** Với yêu cầu hệ thống streaming kích thước cố định kết hợp đào tạo tư duy DSA nền tảng, **Custom `RingBuffer`** là lựa chọn tối ưu tuyệt đối.

---

## 3. ĐÁNH ĐỔI 2: `SegmentTree` VS SPARSE TABLE VS FENWICK TREE (BIT)

Yêu cầu của hệ thống trên đoạn nến bất kỳ `[left, right)` là truy vấn đồng thời **3 đại lượng** trong `RangeStats`: `min_low` (cực tiểu), `max_high` (cực đại), và `volume_sum` (tổng khối lượng), đồng thời hỗ trợ **`update()`** (live tick) và **`append()`** (thêm nến mới):

| Tiêu chí | **`SegmentTree`** (Power-of-2 Iterative) | **Sparse Table** | **Fenwick Tree (BIT)** |
| :--- | :---: | :---: | :---: |
| **Xây dựng ban đầu** | $O(N)$ | $O(N \log N)$ | $O(N)$ |
| **Truy vấn `min`, `max` đoạn `[L, R)`** | **$O(\log N)$** | $O(1)$ | **Không hỗ trợ trực tiếp** (vì `min`/`max` không có phần tử nghịch đảo!) |
| **Truy vấn `volume_sum` đoạn `[L, R)`** | **$O(\log N)$** | $O(\log N)$ (không idempotent!) | $O(\log N)$ |
| **Cập nhật điểm `update(idx, val)`** | **$O(\log N)$** | **$O(N \log N)$** (phải build lại toàn bảng!) | $O(\log N)$ (chỉ cho phép cộng/XOR) |
| **Thêm mới `append(candle)`** | **$O(\log N)$ amortized** | $O(N \log N)$ | $O(\log N)$ (chỉ cho tổng) |
| **Bộ nhớ** | $O(N)$ ($\le 4N$) | $O(N \log N)$ (tốn gấp ~17 lần khi $N = 100k$) | $O(N)$ |

**Tại sao Sparse Table và BIT đều thất bại trước bài toán này?**
- **Sparse Table** chỉ tỏa sáng khi mảng **tĩnh 100% (immutable)** và chỉ hỏi `min`/`max`. Biểu đồ tài chính nhận nến mới (`append`) và cập nhật nến hiện tại (`update`) liên tục theo mỗi tick; hơn nữa `volume_sum` không có tính lũy đẳng (idempotence: $x + x \neq x$), làm mất lợi thế $O(1)$ của Sparse Table.
- **Fenwick Tree (BIT)** phụ thuộc vào tính chất tồn tại **phần tử nghịch đảo** ($\text{Sum}[L, R) = \text{Prefix}(R) - \text{Prefix}(L)$). Vì phép `min` và `max` không có nghịch đảo, BIT không thể trả về `min_low`/`max_high` của đoạn `[L, R)` chuẩn bằng phép trừ hai tiền tố.
- **`SegmentTree`** là cấu trúc duy nhất gộp cả `min_low`, `max_high`, và `volume_sum` vào một **Monoid `RangeStats`** thống nhất, hỗ trợ truy vấn, cập nhật, và mở rộng động trong $O(\log N)$.

---

## 4. ĐÁNH ĐỔI 3: `LTTBDecimator` VS UNIFORM SAMPLING VS MIN-MAX DOWNSAMPLING VS `aggregate_ohlcv_buckets`

| Phương pháp | Độ phức tạp | Bảo toàn Đỉnh/Đáy | Bảo toàn Hình thái Đường (Line) | Bảo toàn Nghĩa OHLCV (Nến Nhật) | Vai trò trong Hệ thống |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Uniform Sampling** (lấy mỗi điểm thứ $k$) | $O(M)$ | **Kém** (dễ bỏ sót đỉnh gai nhọn nằm giữa bước nhảy) | **Kém** (bị răng cưa/aliasing) | **Không** | **Loại bỏ** — không đạt chuẩn biểu đồ tài chính. |
| **Min-Max Downsampling** (M4) | $O(N)$ | **Tốt** (luôn giữ min & max mỗi bucket) | Trung bình (gây hiệu ứng dải đặc ziczac khi vẽ line, gấp đôi điểm) | Thiếu `open`, `close`, `volume` | Không dùng trực tiếp; ý tưởng cực trị được kế thừa vào OHLCV bucketing. |
| **`LTTBDecimator`** (3-Buckets Triangle Area) | $\Theta(N)$ | **Rất tốt** (chọn điểm tạo tam giác diện tích lớn nhất) | **Xuất sắc** (được chuẩn hóa bởi Steinarsson, 2013) | **Không** (chỉ trả về `(x, y)` đơn lẻ) | **Dùng cho các đường chỉ báo & Line Series** (SMA, EMA, Close, Bollinger). |
| **`aggregate_ohlcv_buckets`** | $O(V)$ per window | **Tuyệt đối 100%** (`high=max`, `low=min`) | — (dùng cho nến) | **Tuyệt đối 100%** (`O=first, H=max, L=min, C=last, V=sum`) | **Bắt buộc dùng cho Nến Nhật (Candlesticks)** khi $V > \text{max\_candles}$. |

---

## 5. ĐÁNH ĐỔI 4: `QuadTree` VS UNIFORM GRID VS LINEAR SCAN

Cho bài toán tương tác chuột 2D (Crosshair snapping, tooltip hover, và truy vấn vùng chọn hình chữ nhật):

| Tiêu chí | **`QuadTree`** (2D Adaptive Tree) | **Uniform Grid** (Lưới ô đều) | **Linear Scan** (Duyệt tuần tự) |
| :--- | :---: | :---: | :---: |
| **Truy vấn vùng `query_range`** | $O(\log N + k)$ trung bình | $O(1)$ mỗi ô nếu phân bố đều | $O(N)$ |
| **Tìm gần nhất `nearest`** | **$O(\log N)$** nhờ Branch-and-Bound | Phải mở rộng vòng tròn tìm kiếm qua nhiều ô trống nếu dữ liệu thưa | $O(N)$ |
| **Phân bố dữ liệu lệch / Gap giá** | **Thích ứng tốt** (chỉ chia sâu ở vùng dày đặc điểm) | **Thất bại nặng** (hầu hết ô rỗng, một vài ô sideway dồn hàng ngàn điểm!) | Không phụ thuộc phân bố, nhưng luôn chậm $O(N)$ |
| **Tương thích Zoom động** | Tự nhiên trên tọa độ liên tục `(x, y)` | Kích thước ô cố định bị vô hiệu khi tỷ lệ `min_price..max_price` thay đổi mạnh | Tốn $O(N)$ ở mọi mức zoom |

**Tổng kết Đánh đổi:** Trong dữ liệu tài chính, giá thường đi ngang (tụ đặc trong một dải hẹp) rồi nhảy vọt qua khoảng trống (gap) ở vùng khác. **Uniform Grid** sụp đổ trước phân bố không đồng đều này, còn **Linear Scan** không mở rộng được khi số đối tượng 2D tăng lên. **`QuadTree`** tự chia lưới thích ứng theo mật độ thực tế kết hợp Branch-and-Bound pruning mang lại hiệu suất tối ưu và ổn định cho tương tác 2D.
