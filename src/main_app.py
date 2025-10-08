# file-path: src/main_app.py
# version: 7.0 (Robust Cookie Validation)
# last-updated: 2025-10-08
# description: Viết lại logic kiểm tra cookie để đảm bảo popup luôn hiển thị nếu cookie rỗng hoặc không hợp lệ.

import customtkinter
import logging
import os
import json
from tkinter import messagebox
from src.ui.downloader_tab import DownloaderTab
from src.core.ui_logger import CTkTextboxHandler
from src.core.app_path import get_app_base_path

APP_VERSION = "0.5.0"

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")
class GuidePopup(customtkinter.CTkToplevel):
    def __init__(self, master, title, message, show_checkbox=False, on_close_callback=None):
        super().__init__(master)
        self.title(title)
        self.geometry("700x550")
        self.resizable(True, True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Lưu lại callback để gọi khi cửa sổ đóng
        self.on_close_callback = on_close_callback
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text=title, label_font=("", 14, "bold"))
        scrollable_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        scrollable_frame.grid_columnconfigure(0, weight=1)

        message_label = customtkinter.CTkLabel(scrollable_frame, text=message, wraplength=650, justify="left", anchor="w")
        message_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Thêm checkbox nếu được yêu cầu
        if show_checkbox:
            self.show_again_checkbox = customtkinter.CTkCheckBox(self, text="Không hiển thị lại hướng dẫn này")
            self.show_again_checkbox.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.transient(master)
        self.after(100, self.center_window)

    def center_window(self):
        self.master.update_idletasks()
        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()
        popup_width = self.winfo_width()
        popup_height = self.winfo_height()
        x = master_x + (master_width // 2) - (popup_width // 2)
        y = master_y + (master_height // 2) - (popup_height // 2)
        self.geometry(f"+{x}+{y}")

    def on_closing(self):
        # Nếu có callback, thực thi nó
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()

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

        self.after(100, self._initialize_user_setup)

        self.tab_view = customtkinter.CTkTabview(self, fg_color="#2B2B2B")
        self.tab_view.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")
        self.tab_view.add("Downloader")
        self.downloader_tab = DownloaderTab(master=self.tab_view.tab("Downloader"), app_ref=self)
        self.downloader_tab.pack(expand=True, fill="both")

        self.worker_threads = []
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _load_settings(self):
        """Đọc file settings.json, trả về dict rỗng nếu không có."""
        settings_path = os.path.join(get_app_base_path(), "settings.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save_settings(self, settings_data):
        """Lưu dict vào file settings.json."""
        settings_path = os.path.join(get_app_base_path(), "settings.json")
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=4)
        except OSError as e:
            logging.error(f"Không thể lưu cài đặt: {e}")
    
    # === HÀM ĐÃ ĐƯỢC VIẾT LẠI HOÀN TOÀN ===
    def _initialize_user_setup(self):
        """Kiểm tra sự tồn tại và tính hợp lệ của cookie, sau đó hiển thị các popup cần thiết."""
        base_path = get_app_base_path()
        json_cookie_path = os.path.join(base_path, "facebook_cookies.json")
        txt_cookie_path = os.path.join(base_path, "facebook_cookies.txt")

        cookie_files_exist = os.path.exists(json_cookie_path) and os.path.exists(txt_cookie_path)
        cookies_are_valid = False

        if cookie_files_exist:
            try:
                # Kiểm tra file JSON có nội dung và là một list không rỗng
                with open(json_cookie_path, 'r', encoding='utf-8') as f:
                    json_content = json.load(f)
                    is_json_valid = isinstance(json_content, list) and len(json_content) > 0
                
                # Kiểm tra file TXT có nội dung (kích thước > 0)
                is_txt_valid = os.path.getsize(txt_cookie_path) > 0

                if is_json_valid and is_txt_valid:
                    cookies_are_valid = True
                else:
                    logging.warning("File cookie tồn tại nhưng rỗng hoặc không hợp lệ.")

            except (json.JSONDecodeError, FileNotFoundError):
                logging.error("Lỗi khi đọc file cookie.")
                cookies_are_valid = False

        # --- Logic hiển thị popup ---
        if not cookies_are_valid:
            # Nếu cookie không hợp lệ (hoặc không tồn tại), tạo lại file và hiển thị hướng dẫn cookie
            try:
                with open(json_cookie_path, 'w', encoding='utf-8') as f: f.write("[]")
                with open(txt_cookie_path, 'w', encoding='utf-8') as f: pass
                
                # Hiển thị hướng dẫn cookie, và đặt hướng dẫn sử dụng làm callback để nó chỉ hiện sau khi cookie đã OK
                self._show_cookie_instructions_popup(on_close_callback=self._check_and_show_usage_guide)
            except OSError as e:
                messagebox.showerror("Lỗi nghiêm trọng", f"Không thể tạo file cookie: {e}")
                self.after(100, self.destroy)
        else:
            # Nếu cookie đã hợp lệ ngay từ đầu, chỉ cần kiểm tra và hiển thị hướng dẫn sử dụng
            self._check_and_show_usage_guide()
    
    def _check_and_show_usage_guide(self):
        """Kiểm tra cài đặt và chỉ hiển thị popup hướng dẫn sử dụng nếu cần."""
        settings = self._load_settings()
        if settings.get("show_usage_guide", True):
            self._show_usage_guide_popup()

    def _show_cookie_instructions_popup(self, on_close_callback=None):
        title = "Chào mừng! Cần Thiết lập Cookie để Bắt đầu"
        message = (
            "Chào mừng bạn đến với FB Page Video Downloader!\n\n"
            "Để ứng dụng có thể hoạt động, bạn cần cung cấp cookie đăng nhập Facebook. Chương trình đã tự động tạo sẵn 2 file `facebook_cookies.json` và `facebook_cookies.txt` trong cùng thư mục.\n\n"
            "Vui lòng làm theo các bước sau:\n\n"
            "1. CÀI ĐẶT \"COOKIE-EDITOR\":\n"
            "   - Mở trình duyệt Chrome/Edge và tìm kiếm \"Cookie-Editor\" trong cửa hàng tiện ích.\n"
            "   - Thêm tiện ích này vào trình duyệt của bạn.\n\n"
            "   - Bấm vào nút ghim tiện ích Cookie-Editor để nó luôn hiển thị trên thanh công cụ.\n\n"
            "2. TRUY CẬP FACEBOOK:\n"
            "   - Mở một tab mới và truy cập trang `www.facebook.com`. Đăng nhập nếu bạn chưa đăng nhập.\n\n"
            "3. XUẤT COOKIE (2 LẦN):\n"
            "   - Nhấp vào biểu tượng \"Cookie-Editor\" trên thanh công cụ.\n"
            "   - Nếu có popup yêu cầu quyền, hãy chấp nhận (chọn All Sites).\n"
            "   - Lần 1 (Định dạng JSON):\n"
            "     - Chọn \"Export\" -> \"Export as JSON\".\n"
            "     - Sao chép TOÀN BỘ nội dung.\n"
            "     - Dán vào file `facebook_cookies.json`.\n"
            "   - Lần 2 (Định dạng Netscape):\n"
            "     - Chọn \"Export\" -> \"Export as Netscape\".\n"
            "     - Sao chép TOÀN BỘ nội dung.\n"
            "     - Dán vào file `facebook_cookies.txt`.\n\n"
            "4. KHỞI ĐỘNG LẠI:\n"
            "   - Sau khi đã lưu cả 2 file, hãy đóng và mở lại ứng dụng này."
        )
        GuidePopup(self, title, message, on_close_callback=on_close_callback)

    def _show_usage_guide_popup(self):
        title = "Hướng dẫn Sử dụng Nhanh"
        message = (
            "Mẹo: Bạn có thể kéo và di chuyển bảng hướng dẫn này sang một bên để vừa đọc vừa thao tác trên giao diện chính của chương trình.\n\n"
            "Bạn có thể kéo dãn chương trình này để hiển thị các nút được đầy đủ.\n\n"
            "---\n\n"
            "BƯỚC 1: LẤY LINK VIDEO\n"
            "   - URL Trang Facebook: Dán link đến trang video hoặc reels của một Page.\n"
            "     * Link hợp lệ thường có dạng `https://www.facebook.com/TenPage/reels/`.\n"
            "   - Số lần cuộn: Nhập số lần bạn muốn chương trình cuộn xuống để lấy video cũ hơn. Mỗi lần cuộn sẽ lấy được khoảng 10-20 video.\n"
            "   - Chờ (giây): Nếu mạng chậm, hãy tăng thời gian chờ (ví dụ: 5-7 giây) để trang có đủ thời gian tải video.\n"
            "   - Nhấn nút \"Bước 1: Lấy Link\".\n\n"
            "BƯỚC 2: LỌC & LẤY CHI TIẾT\n"
            "   - Lọc theo ngày: Chọn khoảng thời gian bạn muốn lọc.\n"
            "   - Đa luồng: Bật để tăng tốc độ lọc (mặc định). Nếu máy yếu, hãy tắt đi.\n"
            "   - Nhấn nút \"Bước 2: Lọc & Lấy Chi Tiết\".\n\n"
            "BƯỚC 3: TẢI VIDEO\n"
            "   - Nhấp vào ô vuông ở cột \"Chọn\" để đánh dấu các video bạn muốn tải.\n"
            "   - Nhấn nút \"Bước 3: Tải Video\". Video sẽ được lưu vào thư mục `downloads`.\n\n"
            "CÁC NÚT KHÁC:\n"
            "   - Lưu/Tải phiên: Lưu lại kết quả đã lọc để làm việc sau.\n"
            "   - Nhập TXT: Nhập danh sách link video từ một file `.txt`."
        )
        
        # Hàm callback sẽ được gọi khi popup hướng dẫn sử dụng đóng lại
        def on_guide_close():
            # Kiểm tra trạng thái của checkbox và lưu cài đặt
            if popup.show_again_checkbox.get() == 1: # 1 là trạng thái "đã check"
                settings = self._load_settings()
                settings["show_usage_guide"] = False
                self._save_settings(settings)
                logging.info("Đã lưu cài đặt: Sẽ không hiển thị lại hướng dẫn sử dụng.")
        
        popup = GuidePopup(self, title, message, show_checkbox=True, on_close_callback=on_guide_close)
    
        
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