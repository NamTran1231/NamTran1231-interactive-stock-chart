from collections import deque
import threading


class RingBuffer:

    def __init__(self, max_size: int):
        """Khởi tạo bộ đệm vòng với kích thước tối đa cố định.

        - max_size: Số lượng phần tử tối đa mà bộ đệm có thể chứa.
        """
        self.max_size = max_size

        # Sử dụng deque với thuộc tính maxlen.
        # Khi bộ đệm đầy, phần tử cũ nhất ở đầu sẽ tự động bị xóa khi thêm
        # phần tử mới vào cuối.
        self._buffer = deque(maxlen=max_size)

        # Tạo Lock để bảo vệ dữ liệu khi chạy đa luồng (Thread-safe)
        self._lock = threading.Lock()

    def append(self, item) -> None:
        """Thêm một phần tử mới vào cuối bộ đệm (Tự động ghi đè nếu đầy)."""
        with self._lock:
            self._buffer.append(item)

    def get_all(self) -> list:
        """Lấy toàn bộ dữ liệu hiện tại trong bộ đệm dưới dạng một danh sách
        (list)."""
        with self._lock:
            return list(self._buffer)

    def clear(self) -> None:
        """Xóa sạch toàn bộ dữ liệu trong bộ đệm."""
        with self._lock:
            self._buffer.clear()

    @property
    def size(self) -> int:
        """Trả về số lượng phần tử hiện tại đang có trong bộ đệm."""
        with self._lock:
            return len(self._buffer)

    @property
    def is_full(self) -> bool:
        """Kiểm tra xem bộ đệm đã đầy (đạt kích thước tối đa) hay chưa."""
        with self._lock:
            return len(self._buffer) == self.max_size
