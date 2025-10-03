# file-path: run.py
# version: 2.0
# last-updated: 2025-10-03
# description: Điểm khởi đầu để khởi chạy ứng dụng giao diện đồ họa (GUI).

from src.main_app import MainApp

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()