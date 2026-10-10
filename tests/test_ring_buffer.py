import os
import sys
import unittest

# Add the root directory to the module search path so Python can find the 'src' directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.ring_buffer import RingBuffer


class TestRingBuffer(unittest.TestCase):

    def setUp(self):
        """Initialize an empty buffer with a maximum of 3 elements before each test."""
        self.buffer = RingBuffer(max_size=3)

    def test_append_and_size(self):
        """Test the append functionality and the .size property for counting elements."""
        self.assertEqual(self.buffer.size, 0)

        # Append the 1st element
        self.buffer.append({"Price": 100})
        self.assertEqual(self.buffer.size, 1)

        # Append the 2nd element
        self.buffer.append({"Price": 105})
        self.assertEqual(self.buffer.size, 2)

    def test_circular_behavior_and_overwrite(self):
        """Test the core feature: automatically overwriting the oldest data when the buffer is full."""
        # Fill the buffer to capacity (max size is 3)
        self.buffer.append({"Price": 100})  # Element 0 (Oldest)
        self.buffer.append({"Price": 105})  # Element 1
        self.buffer.append({"Price": 110})  # Element 2
        self.assertTrue(self.buffer.is_full)  # Test the .is_full property

        # Append the 4th element; the first element (100) should be automatically evicted
        self.buffer.append({"Price": 115})

        # The buffer size must remain 3, not increase to 4
        self.assertEqual(self.buffer.size, 3)

        # Call .get_all() to retrieve the data list for verification
        all_items = self.buffer.get_all()

        # The oldest element (100) must be gone, and the remaining elements shifted up
        self.assertEqual(all_items[0]["Price"], 105)
        self.assertEqual(all_items[1]["Price"], 110)
        self.assertEqual(all_items[2]["Price"], 115)

    def test_clear_buffer(self):
        """Test whether the .clear() method properly wipes all data from the buffer."""
        self.buffer.append({"Price": 100})
        self.assertEqual(self.buffer.size, 1)

        # Call the clear method
        self.buffer.clear()
        self.assertEqual(self.buffer.size, 0)
        self.assertEqual(self.buffer.get_all(), [])


if __name__ == "__main__":
    unittest.main()