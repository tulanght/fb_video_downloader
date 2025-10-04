# file-path: src/main_app.py
# version: 1.1
# last-updated: 2025-10-04
# description: Tích hợp module log thông minh vào giao diện chính.

import customtkinter
import logging
from src.ui.downloader_tab import DownloaderTab
from src.core.ui_logger import CTkTextboxHandler

class MainApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- Cấu hình cửa sổ chính ---
        self.title("FB Page Video Downloader")
        self.geometry("800x750") # Tăng chiều cao để chứa log box
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Tab view sẽ co giãn

        # --- Tạo Tab View ---
        self.tab_view = customtkinter.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.tab_view.add("Tải Video")
        self.downloader_tab = DownloaderTab(master=self.tab_view.tab("Tải Video"))
        self.downloader_tab.pack(expand=True, fill="both")

        # --- TẠO MODULE LOG THÔNG MINH ---
        self.log_textbox = customtkinter.CTkTextbox(self, height=120, state="disabled")
        self.log_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        # --- Cấu hình Logger ---
        self._setup_logging()

    def _setup_logging(self):
        # Lấy logger gốc
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)

        # Tạo handler tùy chỉnh và thêm vào logger
        ctk_handler = CTkTextboxHandler(self.log_textbox)
        
        # Định dạng cho log hiển thị trên giao diện
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
        ctk_handler.setFormatter(formatter)
        
        root_logger.addHandler(ctk_handler)

        logging.info("Ứng dụng đã khởi động. Module log sẵn sàng.")