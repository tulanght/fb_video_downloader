# file-path: src/core/app_path.py
# version: 1.0
# last-updated: 2025-10-04
# description: Cung cấp hàm để lấy đường dẫn gốc của ứng dụng, hoạt động cho cả script và file .exe.

import sys
import os

def get_app_base_path():
    """
    Lấy đường dẫn gốc của ứng dụng.
    Nếu chạy dưới dạng file .exe đã đóng gói, đường dẫn sẽ là thư mục chứa file .exe.
    Nếu chạy dưới dạng script .py, đường dẫn sẽ là thư mục gốc của dự án.
    """
    if getattr(sys, 'frozen', False):
        # Chạy dưới dạng file .exe
        return os.path.dirname(sys.executable)
    else:
        # Chạy dưới dạng script .py
        # Giả định file này nằm trong src/core/, chúng ta cần đi lùi 2 cấp để về thư mục gốc
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))