import os
import time
import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal
from ring_buffer import RingBuffer


class DataSimulator(QThread):
    # Tạo một tín hiệu (Signal) để gửi từng điểm dữ liệu sang giao diện UI hiển thị
    new_data_signal = pyqtSignal(dict)

    def __init__(self, csv_file_path: str, buffer_size: int = 1000):
        """Khởi tạo luồng mô phỏng dữ liệu thời gian thực từ file CSV.

        - csv_file_path: Đường dẫn tới file CSV (ví dụ: 'data/AAPL.csv')
        - buffer_size: Kích thước tối đa cho bộ đệm vòng (mặc định 1000 phần tử)
        """
        super().__init__()
        self.csv_file_path = csv_file_path

        # Khởi tạo bộ đệm vòng chuyên dụng đã lập trình ở bước trước
        self.buffer = RingBuffer(max_size=buffer_size)

        # Biến cờ để kiểm soát trạng thái chạy/dừng của luồng
        self._is_running = False

    def run(self):
        """Hàm chạy ngầm tự động kích hoạt khi gọi lệnh .start()"""
        # Kiểm tra xem file CSV có tồn tại không trước khi đọc để tránh báo lỗi
        if not os.path.exists(self.csv_file_path):
            print(f"Lỗi: Không tìm thấy file dữ liệu tại {self.csv_file_path}")
            return

        try:
            # 1. Đọc dữ liệu từ file CSV lên bằng pandas
            df = pd.read_csv(self.csv_file_path)
            self._is_running = True

            print(
                f"=== Bắt đầu mô phỏng truyền dữ liệu từ: {self.csv_file_path} ==="
            )

            # 2. Duyệt qua từng dòng dữ liệu trong file CSV
            for _, row in df.iterrows():
                if not self._is_running:
                    break

                # Chuyển dòng dữ liệu thành một dictionary sạch sẽ
                data_point = {
                    "Date": str(row["Date"]),
                    "Open": float(row["Open"]),
                    "High": float(row["High"]),
                    "Low": float(row["Low"]),
                    "Close": float(row["Close"]),
                    "Volume": float(row["Volume"]),
                }

                # 3. CHÍNH THỨC TRUYỀN DỮ LIỆU VÀO BỘ ĐỆM VÒNG (RingBuffer)
                self.buffer.append(data_point)

                # 4. Phát tín hiệu kèm dữ liệu ra ngoài (cho UI hoặc thuật toán xử lý tiếp)
                self.new_data_signal.emit(data_point)

                # Giả lập khoảng thời gian chờ giữa các phiên (ví dụ: 0.1 giây xuất hiện 1 nến mới)
                # Bạn có thể chỉnh số này nhỏ hơn (ví dụ: 0.01) để dữ liệu chạy nhanh hơn
                time.sleep(0.1)

            print(
                f"=== Kết thúc mô phỏng truyền dữ liệu: {self.csv_file_path} ==="
            )

        except Exception as e:
            print(f"Có lỗi xảy ra trong quá trình đọc/truyền dữ liệu: {e}")

    def stop(self):
        """Hàm dừng luồng mô phỏng một cách an toàn."""
        self._is_running = False
        self.wait()  # Chờ luồng tắt hẳn để tránh xung đột bộ nhớ
