# PHÂN TÍCH ĐỘ PHỨC TẠP THUẬT TOÁN & NGÂN SÁCH KHUNG HÌNH 60 FPS

**Dự án:** Interactive TradingView Stock Chart Engine (DSA Python)  
**Tham số chuẩn đánh giá:** $N$ = tổng số nến lịch sử (tới $100{,}000+$), $K$ = dung lượng `RingBuffer`, $W$ = kích thước cửa sổ chỉ báo, $V$ = số nến trong cửa sổ hiển thị `[start_idx, end_idx)`, $M$ = số nến/điểm tối đa sau decimation theo độ rộng pixel ($M \le 1200$).

---

## 1. BẢNG TỔNG HỢP TIME & SPACE COMPLEXITY

| Cấu trúc Dữ liệu / Thuật toán | Thao tác Chính | Time (Average / Amortized) | Time (Worst Case) | Space Complexity |
| :--- | :--- | :---: | :---: | :---: |
| **`RingBuffer(K)`** | `push(item)` (overwrite) | $O(1)$ | $O(1)$ | $O(K)$ cố định |
| **`RingBuffer(K)`** | `get_all()` | $O(K)$ | $O(K)$ | $O(K)$ |
| **`RingBuffer(K)`** | `latest()`, `__len__()`, `is_full()` | $O(1)$ | $O(1)$ | $O(1)$ |
| **`CircularDeque`** | `push_front`, `push_back` (2x resize) | $O(1)$ amortized | $O(N)$ khi resize | $O(N)$ |
| **`CircularDeque`** | `pop_front`, `pop_back`, `peek_*` | $O(1)$ | $O(1)$ | $O(1)$ |
| **`MonotonicDeque`** | `push(idx, val)`, `evict_before` | $O(1)$ amortized | $O(W)$ ở 1 bước đơn | $O(W)$ |
| **`MonotonicDeque`** | `extrema()` | $O(1)$ | $O(1)$ | $O(1)$ |
| **`SlidingWindowIndicators`** | `rolling_min_max`, `sma`, `ema`, `donchian`, `bollinger` | $O(N)$ toàn chuỗi | $O(N)$ | $O(N)$ output ($O(W)$ phụ) |
| **`CoordinateTransformer`** | `index_to_x`, `price_to_y`, `zoom_at_pixel`, `pan_by_pixels` | $O(1)$ | $O(1)$ | $O(1)$ |
| **`SegmentTree`** | Build từ $N$ nến | $O(N)$ | $O(N)$ | $O(N)$ (`2 * cap <= 4N`) |
| **`SegmentTree`** | `query(left, right)` | $O(\log N)$ | $O(\log N)$ | $O(1)$ phụ |
| **`SegmentTree`** | `update(index, candle)` | $O(\log N)$ | $O(\log N)$ | $O(1)$ phụ |
| **`SegmentTree`** | `append(candle)` (power-of-2 rebuild) | $O(\log N)$ amortized | $O(N)$ khi nhân đôi | $O(N)$ |
| **`LTTBDecimator`** | `downsample(points, M)` | $\Theta(N)$ | $\Theta(N)$ | $\Theta(M)$ output |
| **`aggregate_ohlcv_buckets`** | `aggregate(candles, start, end, M)` | $O(V)$ ($V = \text{end}-\text{start}$) | $O(N)$ (khi zoom hết) | $O(M)$ output |
| **`QuadTree`** | `insert(point)` | $O(\log N)$ | $O(N)$ (cây lệch) | $O(N)$ |
| **`QuadTree`** | `query_range(rect)` | $O(\log N + k)$ ($k$ kq) | $O(N)$ | $O(k)$ |
| **`QuadTree`** | `nearest(x, y, max_dist)` | $O(\log N)$ | $O(N)$ | $O(\log N)$ stack |
| **`EventBus`** | `subscribe` / `unsubscribe` / `publish` | $O(1)$ / $O(S)$ / $O(S)$ | $O(S)$ ($S$ listeners) | $O(S)$ |
| **`CommandHistory(max_size)`** | `execute` / `undo` / `redo` | $O(1)$ | $O(1)$ (hoặc $O(\text{max\_size})$ nếu list pop(0)) | $O(\text{max\_size})$ |

---

## 2. CHỨNG MINH $O(1)$ AMORTIZED CHO `CircularDeque` AUTO-RESIZE 2X

Giả sử `CircularDeque` khởi tạo với dung lượng $C_0 \ge 1$ và thực hiện một chuỗi $n$ thao tác thêm phần tử (`push_front` hoặc `push_back`). Khi số phần tử hiện tại đạt dung lượng $C$, thao tác thêm tiếp theo cấp phát mảng mới kích thước $2C$, sao chép $C$ phần tử hiện có theo thứ tự logic, rồi ghi phần tử mới.

### 2.1. Chứng minh bằng Phương pháp Gộp (Aggregate Analysis)

Chi phí thực tế $c_i$ của thao tác thêm thứ $i$ ($1 \le i \le n$) là:
$$c_i = \begin{cases} C + 1 & \text{nếu } i - 1 = C_0 \cdot 2^k \text{ (kích hoạt resize từ } C = C_0 \cdot 2^k \text{ lên } 2C\text{)} \\ 1 & \text{ngược lại} \end{cases}$$

Tổng chi phí của chuỗi $n$ thao tác là:
$$T(n) = \sum_{i=1}^{n} c_i = n + \sum_{k=0}^{\lfloor \log_2((n-1)/C_0) \rfloor} C_0 \cdot 2^k$$

Đây là cấp số nhân công bội 2 có số hạng lớn nhất $C_0 \cdot 2^{k_{\max}} < n$. Do đó:
$$\sum_{k=0}^{k_{\max}} C_0 \cdot 2^k = C_0 (2^{k_{\max}+1} - 1) < 2 \cdot (C_0 \cdot 2^{k_{\max}}) < 2n$$

Suy ra tổng chi phí $T(n) < n + 2n = 3n$, nên chi phí trung bình mỗi thao tác là:
$$\frac{T(n)}{n} < 3 = O(1) \quad \blacksquare$$

### 2.2. Chứng minh bằng Phương pháp Thế năng (Potential Method — Tarjan)

Xét cả chuỗi hỗn hợp `push_*` và `pop_*` (lưu ý `CircularDeque` không thu nhỏ mảng khi `pop` để tránh hiện tượng thrashing). Gọi $s_i = \text{size}_i$ và $m_i = \text{capacity}_i$ sau thao tác thứ $i$. Định nghĩa hàm thế năng $\Phi$:
$$\Phi(D_i) = \max(0,\; 2s_i - m_i)$$
Dễ thấy $\Phi(D_0) = \max(0, 0 - C_0) = 0$ và $\Phi(D_i) \ge 0$ với mọi $i \ge 0$.

Chi phí khấu hao (amortized cost) của thao tác thứ $i$ là $\hat{c}_i = c_i + \Phi(D_i) - \Phi(D_{i-1})$.

- **Trường hợp 1: `push_front` / `push_back` KHÔNG resize ($s_{i-1} < m_{i-1}$):**
  $c_i = 1$, $s_i = s_{i-1} + 1$, $m_i = m_{i-1}$.
  Khi tăng $s$ thêm 1, đại lượng $2s - m$ tăng thêm $2$, nên $\Phi(D_i) - \Phi(D_{i-1}) \le 2$.
  Do đó: $\hat{c}_i \le 1 + 2 = 3 = O(1)$.

- **Trường hợp 2: `push_front` / `push_back` CÓ resize ($s_{i-1} = m_{i-1} = m$):**
  Ta phải sao chép $m$ phần tử và thêm 1 phần tử mới $\implies c_i = m + 1$.
  Sau resize: $m_i = 2m$, $s_i = m + 1$.
  Thế năng trước resize: $\Phi(D_{i-1}) = \max(0, 2m - m) = m$.
  Thế năng sau resize: $\Phi(D_i) = \max(0, 2(m + 1) - 2m) = 2$.
  Suy ra chi phí khấu hao là:
  $$\hat{c}_i = (m + 1) + (2 - m) = 3 = O(1)$$

- **Trường hợp 3: `pop_front` / `pop_back`:**
  $c_i = 1$, $s_i = s_{i-1} - 1$, $m_i = m_{i-1} \implies \Phi(D_i) \le \Phi(D_{i-1})$, nên $\hat{c}_i \le 1 = O(1)$.

Vì $\sum_{i=1}^n c_i = \sum_{i=1}^n \hat{c}_i - (\Phi(D_n) - \Phi(D_0)) \le \sum_{i=1}^n \hat{c}_i \le 3n$, mọi thao tác đều đạt **$O(1)$ amortized**. $\blacksquare$

---

## 3. CHỨNG MINH $O(1)$ AMORTIZED CHO `MonotonicDeque`

Xét chuỗi $N$ phần tử được đưa qua `MonotonicDeque`: mỗi phần tử $x_i$ gọi `push(i, x_i)` đúng 1 lần, cùng tối đa $N$ lần kiểm tra hết hạn `evict_before(...)`.

### Chứng minh bằng Phương pháp Kế toán (Accounting Method)

Gán chi phí khấu hao **2 đơn vị (2 credits)** cho mỗi thao tác `push(i, x_i)`:
1. **1 credit** dùng ngay để trả cho thao tác vật lý `CircularDeque.push_back((i, x_i))` (chi phí $O(1)$ amortized đã chứng minh ở Mục 2).
2. **1 credit còn lại** được gắn trực tiếp lên bản ghi `(i, x_i)` đang nằm trong deque làm "quỹ bảo chứng".

Bây giờ xét hai loại thao tác xóa phần tử khỏi deque:
- Xóa từ đuôi (`pop_back()`) bên trong `push()` do vi phạm tính đơn điệu: phần tử bị xóa lấy **1 credit gắn trên chính nó** ra để thanh toán cho thao tác `pop_back()` ($O(1)$).
- Xóa từ đầu (`pop_front()`) bên trong `evict_before(min_valid_index)` do hết hạn cửa sổ: phần tử bị xóa lấy **1 credit gắn trên chính nó** ra để thanh toán cho thao tác `pop_front()` ($O(1)$).

Vì một phần tử chỉ có thể bị xóa khỏi `MonotonicDeque` **tối đa 1 lần** (hoặc qua `pop_back`, hoặc qua `pop_front`, không bao giờ quay lại sau khi bị xóa), số credit tích lũy không bao giờ âm.
Tổng số phép toán vật lý trên toàn chuỗi $N$ phần tử bị chặn trên chặt chẽ bởi $2N$ (`<= N` lần push + `<= N` lần pop). Do đó chi phí mỗi bước là **$O(1)$ amortized** và toàn bộ các chỉ báo trong `SlidingWindowIndicators` chạy trong **$\Theta(N)$**. $\blacksquare$

---

## 4. CHỨNG MINH $O(\log N)$ CỦA `SegmentTree`

Giả sử cây lưu $N$ nến, sử dụng mảng 1-indexed kích thước $2C$ với $C = 2^{\lceil \log_2 N \rceil}$ (nếu $N = 0$ thì $C = 1$). Chiều cao cây là $h = \log_2 C = \lceil \log_2 N \rceil$.

### 4.1. Chứng minh `query(left, right)` mất $O(\log N)$

Trong cài đặt lặp (iterative) cho đoạn nửa mở `[left, right)`, hai con trỏ bắt đầu tại tầng lá: $l = \text{left} + C$, $r = \text{right} + C$. Tại mỗi vòng lặp khi $l < r$:
- Nếu $l$ lẻ, nút $l$ là con phải của cha nên cha của nó chứa phần tử bên trái ngoài khoảng $\implies$ cộng gộp `tree[l]` và dịch $l \leftarrow l + 1$.
- Nếu $r$ lẻ, nút $r - 1$ là con trái của nút biên phải $\implies$ dịch $r \leftarrow r - 1$ và cộng gộp `tree[r]`.
- Sau bước điều chỉnh biên, cả $l$ và $r$ đều chẵn; ta dịch cả hai lên tầng cha: $l \leftarrow \lfloor l / 2 \rfloor$, $r \leftarrow \lfloor r / 2 \rfloor$.

**Bổ đề:** Ở mỗi tầng của cây, vòng lặp thực hiện **tối đa 2 phép `combine`** (tối đa 1 cho biên trái $l$ và 1 cho biên phải $r$), sau đó $l$ và $r$ cùng chia đôi.  
Số tầng từ lá lên gốc là $\log_2 C + 1 = \lceil \log_2 N \rceil + 1$.  
Vì ở mỗi tầng chỉ có tối đa 2 nút được hợp nhất và khoảng $r - l$ giảm ít nhất một nửa mỗi tầng, tổng số nút được truy cập tối đa là $2 \lceil \log_2 N \rceil = O(\log N)$. $\blacksquare$

### 4.2. Chứng minh `update(index, candle)` & `append(candle)`

- **`update(index, candle)`:** Gán `tree[index + C] = RangeStats(...)`, sau đó cập nhật ngược lên gốc qua `idx //= 2` đến `idx == 1`. Số bước lặp đúng bằng chiều cao cây $\log_2 C = O(\log N)$.
- **`append(candle)` với Dynamic Power-of-2 Rebuild:**
  - Nếu `size < C`: chỉ là một phép `update(size, candle)` tại chỗ $\implies O(\log N)$ worst-case.
  - Nếu `size == C` (chỉ xảy ra tại $C \in \{1, 2, 4, 8, \dots\}$): cấp phát mảng mới $4C$, chép lại $C$ lá cũ, build lại phần nội bộ trong $\Theta(C)$ thao tác.
  - Theo chứng minh Aggregate Analysis tương tự Mục 2.1, tổng chi phí rebuild cho $N$ lần `append` liên tiếp là $\sum_{2^k < N} 2 \cdot 2^k < 4N$, tức chi phí rebuild phân bổ cho mỗi lần `append` chỉ là $O(1)$ amortized. Cộng với $O(\log N)$ cập nhật đường lên gốc, `append` đạt **$O(\log N)$ amortized**. $\blacksquare$

---

## 5. PHÂN TÍCH ĐỘ PHỨC TẠP `LTTBDecimator` & `aggregate_ohlcv_buckets`

### 5.1. `LTTBDecimator.downsample(points, threshold)`

Đặt $N = \text{len}(\text{points})$ và $M = \text{threshold}$. Khi $2 < M < N$:
- Số lượng buckets ở giữa là $B = M - 2$, mỗi bucket có kích thước trung bình $s = \frac{N - 2}{M - 2}$.
- Với mỗi bucket $i \in \{0, \dots, B - 1\}$:
  - Tính trung bình $(\bar{x}_{i+1}, \bar{y}_{i+1})$ trên bucket $i+1$: quét $|B_{i+1}|$ điểm.
  - Tính diện tích tam giác và tìm cực đại trên bucket $i$: quét $|B_i|$ điểm.
- Tổng số điểm được truy cập qua toàn bộ thuật toán là:
  $$1 + 1 + \sum_{i=0}^{B-1} (|B_i| + |B_{i+1}|) \le 2 + 2(N - 2) = 2N - 2 = \Theta(N)$$
- Bộ nhớ phụ chỉ gồm mảng kết quả kích thước $M$: $\Theta(M)$.

### 5.2. `aggregate_ohlcv_buckets(candles, start_idx, end_idx, max_candles)`

Đặt $V = \text{end\_idx} - \text{start\_idx}$ là số nến nằm trong khung nhìn hiện tại:
- Nếu $V \le \text{max\_candles}$: sao chép lát cắt có kích thước $V \implies O(V) = O(\text{max\_candles})$.
- Nếu $V > \text{max\_candles}$: phân hoạch $V$ phần tử vào $M = \text{max\_candles}$ bucket rời nhau. Mỗi cây nến trong đoạn $[ \text{start\_idx}, \text{end\_idx} )$ được đọc **đúng 1 lần** để lấy `max(high)`, `min(low)`, `sum(volume)` $\implies$ độ phức tạp thời gian là **$\Theta(V)$ per window** (khi zoom toàn bộ dữ liệu $V = N$ thì là $\Theta(N)$; khi zoom cục bộ $V \ll N$ thì nhanh tỷ lệ thuận với $V$). Không gian đầu ra luôn bị chặn bởi $\Theta(\text{max\_candles})$.

---

## 6. PHÂN TÍCH `QuadTree` 2D (AVERAGE CASE VS WORST CASE)

Giả sử `QuadTree` quản lý $N$ điểm 2D `SpatialPoint` trong khung `Bounds` có kích thước $W \times H$ với dung lượng lá `capacity = c` (mặc định `4`):

- **Không gian (Space Complexity):**
  - *Average Case:* Cây cân bằng tương đối với chiều sâu $O(\log N)$, tổng số nút bị chặn bởi $O(N / c) = O(N)$.
  - *Worst Case:* Nếu các điểm tụ đặc rất gần nhau tại một góc phần tư duy nhất, số nút nội bộ sinh ra bị chặn bởi giới hạn chiều sâu $D_{\max}$, không gian tối đa $O(N \cdot D_{\max})$ (hoặc $O(N)$ với $D_{\max}$ hằng số).
- **Thời gian `insert(point)`:**
  - *Average Case:* Điểm đi xuống theo một đường đơn từ gốc tới lá ở độ sâu $O(\log N)$.
  - *Worst Case:* $O(D_{\max})$ hoặc $O(N)$ nếu cây suy biến lệch hoàn toàn.
- **Thời gian `query_range(rect)`:**
  - *Average Case:* Các nút con không giao `rect` bị cắt tỉa ngay. Số nút giao biên của hình chữ nhật truy vấn và chứa $k$ điểm kết quả là $O(\sqrt{N} + k)$ trong trường hợp tệ trên lưới tổng quát và **$O(\log N + k)$** đối với vùng truy vấn nhỏ trên phân bố đều.
  - *Worst Case:* $O(N)$ khi `rect` bao trùm toàn bộ không gian `Bounds`.
- **Thời gian `nearest(x, y, max_dist)` (Branch-and-Bound):**
  - *Average Case:* Nhờ ưu tiên duyệt nút con gần điểm truy vấn nhất trước (`min_dist_to_bounds` nhỏ nhất), `best_dist` nhanh chóng co lại quanh hàng xóm thực sự và cắt tỉa đa số nhánh còn lại $\implies$ **$O(\log N)$**.
  - *Worst Case:* **$O(N)$** nếu tất cả $N$ điểm nằm cách đều tâm `(x, y)` trên một cung tròn bán kính $r \le \text{max\_dist}$, buộc thuật toán kiểm tra tất cả các nhánh lá giao đường tròn.
- **Tác động thực tế trong Chart Engine:** Vì `QuadTree` được dựng lại cho khung hình hiện tại trên tập nến/điểm đã qua bước `aggregate_ohlcv_buckets` ($N_{\text{vis}} \le 400$ điểm trên màn hình $1600\text{ px}$), ngay cả worst-case của $400$ điểm cũng dưới $0.15\text{ ms}$!

---

## 7. PHÂN TÍCH NGÂN SÁCH KHUNG HÌNH 60 FPS ($\le 16.67\text{ ms}$ / FRAME)

Để mắt người cảm nhận chuyển động pan/zoom/replay hoàn toàn mượt mà ở tốc độ **60 khung hình/giây**, tổng thời gian từ lúc nhận sự kiện đầu vào đến khi `QPainter` vẽ xong lên màn hình không được vượt quá:
$$T_{\text{budget}} = \frac{1000\text{ ms}}{60} \approx 16.67\text{ ms}$$

Trong môi trường CPython (có chi phí thông dịch bytecode và Garbage Collector định kỳ), ta thiết kế hệ thống sao cho thời gian trung bình (p50) nằm quanh $3\text{–}5\text{ ms}$ và phân vị 99% (p99) luôn nằm dưới $16.67\text{ ms}$.

### Phân bổ Ngân sách Thời gian (Kịch bản $N = 100{,}000$ nến, Viewport $1280 \times 720\text{ px}$, `max_candles = 300`)

| Giai đoạn Pipeline | Module thực thi | Độ phức tạp | Thời gian dự kiến (CPython 3.14) | Biện pháp bảo vệ Ngân sách |
| :--- | :--- | :---: | :---: | :--- |
| 1. Auto-Fit Trục Y | `SegmentTree.query(L, R)` | $O(\log N)$ | $\approx 0.01\text{ ms}$ | Truy vấn iterative không đệ quy, tránh hoàn toàn $O(N)$ scan. |
| 2. Gộp Nến OHLCV | `aggregate_ohlcv_buckets(...)` | $O(V)$ | $0.2\text{ ms}$ (zoom gần) – $4.5\text{ ms}$ (zoom 100k nến) | Chỉ gộp nến trong `[start, end)`; tránh tạo object thừa, dùng `slots=True` trên `Candle`. |
| 3. Chỉ báo & LTTB | `SlidingWindowIndicators` + `LTTBDecimator` | $O(V)$ / $O(M)$ | $\approx 0.8 - 2.0\text{ ms}$ | Tính indicator trên series đã cắt/cache khi dữ liệu không đổi, rồi LTTB xuống $\le 600$ điểm. |
| 4. Biến đổi Tọa độ | `CoordinateTransformer` | $O(M)$ | $\approx 0.2\text{ ms}$ | Tính toán thuần số thực trên tối đa $M \le 300$ nến và $600$ điểm line. |
| 5. Spatial Indexing | `QuadTree` build trên $M$ nến | $O(M \log M)$ | $\approx 0.3\text{ ms}$ | Dựng `QuadTree` chỉ trên tập $M \le 300$ nến hiển thị thay vì $100{,}000$ nến gốc! |
| 6. Đổ Đồ họa Native | `QPainter` trong `paintEvent` | $O(M)$ draw calls | $\approx 1.5 - 3.5\text{ ms}$ | Nhờ bước (2) & (3), `QPainter` chỉ vẽ $\le 300$ hình chữ nhật thay vì $100{,}000$! |
| **Tổng thời gian Frame** | **End-to-End Frame** | — | **$\approx 3.0\text{ ms} - 10.5\text{ ms}$** | **Dư biên độ an toàn $6+\text{ ms}$ so với trần $16.67\text{ ms}$ (60 FPS)!** |

### Kết luận Hiệu năng
1. **Không bao giờ để `QPainter` nhận $O(N)$ nguyên thủy:** Chi phí vẽ C++/Qt trên $100{,}000$ nến trực tiếp sẽ vượt $150\text{ ms}$ ($< 7\text{ FPS}$). Chính bộ ba `SegmentTree` + `aggregate_ohlcv_buckets` + `LTTBDecimator` là rào chắn quyết định giữ số lượng lệnh vẽ `QPainter` ở hằng số $O(\text{width\_px})$.
2. **Đo kiểm định lượng bằng `--benchmark`:** Mọi sự suy giảm hiệu năng (regression) trong quá trình phát triển sẽ bị phát hiện ngay lập tức qua `time.perf_counter()` (kiểm tra p50, p95, p99) và `tracemalloc` (kiểm tra bộ nhớ ổn định của `RingBuffer`).
