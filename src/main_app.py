# file-path: src/main_app.py
# version: 3.1 (AttributeError Hotfix)
# last-updated: 2025-10-08
# description: Sửa lỗi AttributeError do thiếu hàm _initialize_user_setup.

import customtkinter
import logging
import os
import json
from tkinter import messagebox
from src.ui.downloader_tab import DownloaderTab
from src.core.ui_logger import CTkTextboxHandler
# === QUAN TRỌNG: Chúng ta sẽ dùng app_path ở đây ===
from src.core.app_path import get_app_base_path

APP_VERSION = "0.5.0" # Nâng phiên bản cho giao diện mới

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

class MainApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"FB Page Video Downloader v{APP_VERSION}")
        self.geometry("950x750")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) 

        self.log_textbox = customtkinter.CTkTextbox(self, height=120, state="disabled")
        self.log_textbox.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="nsew")
        self._setup_logging()

        # === PHẦN BỊ THIẾU ĐÃ ĐƯỢC THÊM LẠI Ở DƯỚI ===
        self._initialize_user_setup()

        self.tab_view = customtkinter.CTkTabview(self, fg_color="#2B2B2B")
        self.tab_view.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")
        self.tab_view.add("Downloader")
        
        self.downloader_tab = DownloaderTab(master=self.tab_view.tab("Downloader"), app_ref=self)
        self.downloader_tab.pack(expand=True, fill="both")

        self.worker_threads = []
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # === HÀM BỊ THIẾU GÂY LỖI ĐÃ ĐƯỢC BỔ SUNG ===
    def _initialize_user_setup(self):
        """Kiểm tra và tạo các file cookie cần thiết nếu chúng không tồn tại."""
        base_path = get_app_base_path()
        json_cookie_path = os.path.join(base_path, "facebook_cookies.json")
        txt_cookie_path = os.path.join(base_path, "facebook_cookies.txt")
        
        show_instructions = False
        if not os.path.exists(json_cookie_path) or not os.path.exists(txt_cookie_path):
            logging.info("Không tìm thấy file cookie. Đang tạo file mới...")
            try:
                with open(json_cookie_path, 'w', encoding='utf-8') as f:
                    f.write("[]")
                with open(txt_cookie_path, 'w', encoding='utf-8') as f:
                    pass
                show_instructions = True
            except OSError as e:
                messagebox.showerror("Lỗi nghiêm trọng", f"Không thể tạo file cookie tại: {base_path}\nLỗi: {e}")
                self.after(100, self.destroy)
                return

        if show_instructions:
            self._show_cookie_instructions_popup()

    def _show_cookie_instructions_popup(self):
        """Hiển thị hộp thoại hướng dẫn người dùng cách lấy cookie."""
        instructions = "Chào mừng bạn! Để ứng dụng hoạt động, bạn cần cung cấp cookie...\n\n(Nội dung hướng dẫn chi tiết)" # Giữ ngắn gọn cho ví dụ
        messagebox.showinfo("Hướng dẫn Thiết lập Cookie", instructions)
    # === KẾT THÚC PHẦN BỔ SUNG ===
    
    def on_closing(self):
        if self.downloader_tab.is_running_task:
            logging.info("Tác vụ nền đang chạy. Gửi yêu cầu dừng...")
            self.downloader_tab.request_stop_task()
            self.after(500, self.check_if_threads_are_done) 
        else:
            self.destroy()

    def check_if_threads_are_done(self):
        alive_threads = [t for t in self.worker_threads if t.is_alive()]
        if alive_threads:
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