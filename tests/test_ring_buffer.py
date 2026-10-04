import os
import sys
import unittest

# Thêm thư mục gốc vào hệ thống tìm kiếm module để Python hiểu được thư mục 'src'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.ring_buffer import RingBuffer


class TestRingBuffer(unittest.TestCase):

    def setUp(self):
        """Khởi tạo một bộ đệm trống với tối đa 3 phần tử trước mỗi bài test."""
        self.buffer = RingBuffer(max_size=3)

    def test_append_and_size(self):
        """Kiểm tra tính năng thêm dữ liệu và thuộc tính .size để đếm số lượng."""
        self.assertEqual(self.buffer.size, 0)

        # Thêm phần tử thứ 1
        self.buffer.append({"Price": 100})
        self.assertEqual(self.buffer.size, 1)

        # Thêm phần tử thứ 2
        self.buffer.append({"Price": 105})
        self.assertEqual(self.buffer.size, 2)

    def test_circular_behavior_and_overwrite(self):
        """Kiểm tra tính năng cốt lõi: Tự động ghi đè dữ liệu cũ nhất khi bộ
        đệm đầy."""
        # Nạp đầy bộ đệm (kích thước tối đa là 3)
        self.buffer.append({"Price": 100})  # Phần tử 0 (Cũ nhất)
        self.buffer.append({"Price": 105})  # Phần tử 1
        self.buffer.append({"Price": 110})  # Phần tử 2
        self.assertTrue(self.buffer.is_full)  # Kiểm tra thuộc tính .is_full

        # Thêm phần tử thứ 4, phần tử đầu tiên (100) phải tự động bị xóa bỏ
        self.buffer.append({"Price": 115})

        # Kích thước bộ đệm vẫn phải giữ nguyên là 3, không được tăng lên 4
        self.assertEqual(self.buffer.size, 3)

        # Gọi hàm .get_all() để lấy danh sách dữ liệu ra kiểm tra
        all_items = self.buffer.get_all()

        # Phần tử cũ nhất (100) phải biến mất, các phần tử còn lại dịch lên đầu
        self.assertEqual(all_items[0]["Price"], 105)
        self.assertEqual(all_items[1]["Price"], 110)
        self.assertEqual(all_items[2]["Price"], 115)

    def test_clear_buffer(self):
        """Kiểm tra hàm .clear() xem có xóa sạch dữ liệu trong bộ đệm không."""
        self.buffer.append({"Price": 100})
        self.assertEqual(self.buffer.size, 1)

        # Gọi hàm xóa sạch bộ đệm
        self.buffer.clear()
        self.assertEqual(self.buffer.size, 0)
        self.assertEqual(self.buffer.get_all(), [])


if __name__ == "__main__":
    unittest.main()
