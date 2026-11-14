# Complexity và kế hoạch benchmark

**Chưa có kết quả đo.** Các chi phí dưới đây là target/lập luận dự kiến, phải đối chiếu implementation khi có code.

N = indexed candles; K = buffer/window size; W = query width; V = visible candles; G = groups drawn.

| Thao tác | Thời gian dự kiến | Lưu ý |
| --- | --- | --- |
| CSV load/validate ordered input | O(N) | O(N) history; không sort che lỗi |
| Buffer push | O(1) | O(capacity) slots; object vẫn allocation |
| Buffer snapshot/clear | O(K) | Snapshot tạo list, clear bỏ references |
| Tree build | O(N) | O(N) storage, merge mỗi node hằng lần |
| Tree query/point update | O(log N) | Interval phân rã theo chiều cao cây |
| Tree append | O(log N) thường/amortized | Expansion rebuild O(N), không worst-case O(log N) mọi lần |
| Scan query | O(W) | Oracle/baseline |
| Timestamp binary search | O(log N) | Không cần Quadtree baseline |
| Gom visible candles trực tiếp | O(V) | O(G) output; grouping có chi phí |
| Vẽ prepared groups | O(G) primitives | Native/Qt memory đo riêng |
| Optional monotonic deque | O(1) amortized/update | O(K); mỗi index vào/ra tối đa một lần |

Big-O là lập luận thuật toán; benchmark hỗ trợ thực nghiệm, không chứng minh asymptotic complexity.

## Protocol M5

1. Synthetic datasets seed xác định: 1k, 10k, 100k, 300k nếu máy đủ RAM; ghi count thực và nhãn synthetic.
2. Ghi CPU/RAM/OS/Python/PyQt, commit, cấu hình. Tách generation, loading/validation, build, query, update/append và rendering.
3. So tree với scan trước timing; cùng query distribution và interval widths; không tính generation vào query loop.
4. Warmup/repeated runs với `time.perf_counter`; ghi sample count, median và p95 khi đủ mẫu; không hardcode machine-dependent thresholds trong unit tests.
5. Memory: `tracemalloc` đo Python allocations, không toàn bộ Qt/native. Process RSS là metric khác; ghi method, baseline và peak, không trộn metric.
6. UI đo viewport size, visible count, grouping factor, frame/interaction time. So clipping/grouping với baseline cùng input/viewport; tính cả chuẩn bị nhóm. Cache sau khi profiler cho thấy lợi ích.

## Verification và kết quả

Test CSV errors/empty/single-row, random range equivalence, point updates/expansion, repeated wraparound, timestamp rules, OHLCV preservation, coordinate round trips. Manual GUI checklist cho tình huống không đáng dùng framework nặng.

Chưa đo runtime/memory/FPS/300k rendering. M5 sẽ thêm bảng có command/script thực, môi trường, commit, count, widths, samples và raw output. Query nhanh không đồng nghĩa chart mượt.
