# file-path: src/main_app.py
# version: 1.3
# last-updated: 2025-10-05
# description: Phiên bản ổn định, xử lý đóng cửa sổ an toàn.

import customtkinter
import logging
from src.ui.downloader_tab import DownloaderTab
from src.core.ui_logger import CTkTextboxHandler
APP_VERSION = "0.4.0" # <-- THÊM DÒNG NÀY
class MainApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("FB Page Video Downloader")
        self.geometry("800x750")
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(0, weight=1)

        self.tab_view = customtkinter.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tab_view.add("Tải Video")
        
        self.downloader_tab = DownloaderTab(master=self.tab_view.tab("Tải Video"), app_ref=self)
        self.downloader_tab.pack(expand=True, fill="both")

        self.log_textbox = customtkinter.CTkTextbox(self, height=120, state="disabled")
        self.log_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        self._setup_logging()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.worker_threads = []

    def on_closing(self):
        if self.downloader_tab.is_running_task:
            logging.info("Tác vụ nền đang chạy. Gửi yêu cầu dừng...")
            self.downloader_tab.update_status("Đang yêu cầu dừng tác vụ, vui lòng chờ...")
            self.downloader_tab.request_stop_task()
            self.after(500, self.check_if_threads_are_done)
        else:
            self.destroy()

    def check_if_threads_are_done(self):
        alive_threads = [t for t in self.worker_threads if t.is_alive()]
        if alive_threads:
            self.worker_threads = alive_threads
            self.after(500, self.check_if_threads_are_done)
            return
        self.destroy()

    def _setup_logging(self):
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        ctk_handler = CTkTextboxHandler(self.log_textbox)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%H:%M:%S')
        ctk_handler.setFormatter(formatter)
        if not any(isinstance(h, CTkTextboxHandler) for h in root_logger.handlers):
            root_logger.addHandler(ctk_handler)
        logging.info("Ứng dụng đã khởi động. Module log sẵn sàng.")