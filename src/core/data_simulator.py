import os
import time
import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal
from ring_buffer import RingBuffer


class DataSimulator(QThread):
    # Create a signal to send individual data points to the UI for display
    new_data_signal = pyqtSignal(dict)

    def __init__(self, csv_file_path: str, buffer_size: int = 1000):
        """Initialize the real-time data simulation thread from a CSV file.

        - csv_file_path: Path to the CSV file (e.g., 'data/AAPL.csv')
        - buffer_size: Maximum size for the ring buffer (default 1000 elements)
        """
        super().__init__()
        self.csv_file_path = csv_file_path

        # Initialize the specialized ring buffer programmed in the previous step
        self.buffer = RingBuffer(max_size=buffer_size)

        # Flag variable to control the run/stop state of the thread
        self._is_running = False

    def run(self):
        """Background worker function automatically triggered when calling .start()"""
        # Check if the CSV file exists before reading to avoid errors
        if not os.path.exists(self.csv_file_path):
            print(f"Error: Data file not found at {self.csv_file_path}")
            return

        try:
            # 1. Read data from the CSV file using pandas
            df = pd.read_csv(self.csv_file_path)
            self._is_running = True

            print(
                f"=== Started data streaming simulation from: {self.csv_file_path} ==="
            )

            # 2. Iterate through each row of data in the CSV file
            for _, row in df.iterrows():
                if not self._is_running:
                    break

                # Convert the data row into a clean dictionary
                data_point = {
                    "Date": str(row["Date"]),
                    "Open": float(row["Open"]),
                    "High": float(row["High"]),
                    "Low": float(row["Low"]),
                    "Close": float(row["Close"]),
                    "Volume": float(row["Volume"]),
                }

                # 3. PUSH DATA INTO THE RING BUFFER
                self.buffer.append(data_point)

                # 4. Emit the signal along with data outward (for UI or processing algorithms)
                self.new_data_signal.emit(data_point)

                # Simulate a delay between frames (e.g., 0.1 seconds per new candle)
                # You can make this smaller (e.g., 0.01) for faster streaming
                time.sleep(0.1)

            print(
                f"=== Ended data streaming simulation: {self.csv_file_path} ==="
            )

        except Exception as e:
            print(f"An error occurred during data reading/streaming: {e}")

    def stop(self):
        """Safely stop the simulation thread."""
        self._is_running = False
        self.wait()  # Wait for the thread to fully shut down to avoid memory conflicts