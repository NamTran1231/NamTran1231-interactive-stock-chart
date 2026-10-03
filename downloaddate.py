import os
import pandas as pd
import yfinance as yf

# Định dạng đường dẫn để lưu đúng vào thư mục data của bạn
stocks = {"AAPL": "data/AAPL.csv", "BTC-USD": "data/BTC-USD.csv"}

for ticker, file_path in stocks.items():
    print(f"Đang tải dữ liệu cho {ticker}...")

    # Bỏ tham số end để tự động lấy dữ liệu từ 01/01/2025 đến HIỆN TẠI
    data = yf.download(ticker, start="2025-01-01")

    if not data.empty:
        data.to_csv(file_path)
        print(f"-> Đã cập nhật dữ liệu mới nhất vào file: {file_path}")
    else:
        print(f"-> Lỗi: Không thể lấy dữ liệu cho {ticker}")

print("\nHoàn thành! Dữ liệu đã được cập nhật đến thời điểm hiện tại.")
