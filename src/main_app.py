# file-path: src/main_app.py
# version: 4.0 (Movable Popups & Full User Guide)
# last-updated: 2025-10-08
# description: Tích hợp popup hướng dẫn có thể di chuyển được và logic hiển thị cho người dùng mới.

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

# === LỚP CỬA SỔ POPUP TÙY CHỈNH, CÓ THỂ DI CHUYỂN ===
class GuidePopup(customtkinter.CTkToplevel):
    def __init__(self, master, title, message):
        super().__init__(master)
        self.title(title)
        self.geometry("600x450")
        self.resizable(False, False)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        textbox = customtkinter.CTkTextbox(self, wrap="word", corner_radius=0)
        textbox.grid(row=0, column=0, sticky="nsew")
        textbox.insert("1.0", message)
        textbox.configure(state="disabled")

        # Giữ cho cửa sổ này luôn ở trên cửa sổ chính
        self.transient(master)
        self.grab_set()

class MainApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        # ... (Phần cấu hình cửa sổ chính không đổi)
        self.title(f"FB Page Video Downloader v{APP_VERSION}")
        self.geometry("950x750")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) 
        self.log_textbox = customtkinter.CTkTextbox(self, height=120, state="disabled")
        self.log_textbox.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="nsew")
        self._setup_logging()

        self._initialize_user_setup()

        self.tab_view = customtkinter.CTkTabview(self, fg_color="#2B2B2B")
        self.tab_view.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="nsew")
        self.tab_view.add("Downloader")
        self.downloader_tab = DownloaderTab(master=self.tab_view.tab("Downloader"), app_ref=self)
        self.downloader_tab.pack(expand=True, fill="both")

        self.worker_threads = []
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _initialize_user_setup(self):
        """Kiểm tra file cookie và hiển thị các popup hướng dẫn khi cần thiết."""
        base_path = get_app_base_path()
        json_cookie_path = os.path.join(base_path, "facebook_cookies.json")
        txt_cookie_path = os.path.join(base_path, "facebook_cookies.txt")
        
        # Biến cờ để quyết định có hiển thị hướng dẫn sử dụng hay không
        show_usage_guide = False

        if not os.path.exists(json_cookie_path) or not os.path.exists(txt_cookie_path):
            logging.info("Không tìm thấy file cookie. Đang tạo file mới và hiển thị hướng dẫn.")
            try:
                with open(json_cookie_path, 'w', encoding='utf-8') as f: f.write("[]")
                with open(txt_cookie_path, 'w', encoding='utf-8') as f: pass
                
                # Hiển thị hướng dẫn cookie và đánh dấu để hiển thị tiếp hướng dẫn sử dụng
                self._show_cookie_instructions_popup()
                show_usage_guide = True

            except OSError as e:
                messagebox.showerror("Lỗi nghiêm trọng", f"Không thể tạo file cookie tại: {base_path}\nLỗi: {e}")
                self.after(100, self.destroy)
                return
        else:
            # Nếu file cookie đã có, vẫn hiển thị hướng dẫn sử dụng một lần
            show_usage_guide = True
        
        # Chỉ hiển thị hướng dẫn sử dụng MỘT LẦN mỗi phiên chạy
        if show_usage_guide:
            # Dùng `after` để đảm bảo popup này hiện ra sau khi cửa sổ chính đã sẵn sàng
            self.after(200, self._show_usage_guide_popup)

    def _show_cookie_instructions_popup(self):
        title = "Chào mừng! Cần Thiết lập Cookie để Bắt đầu"
        message = (
            "Chào mừng bạn đến với FB Page Video Downloader!\n\n"
            "Để ứng dụng có thể hoạt động, bạn cần cung cấp cookie đăng nhập Facebook. Chương trình đã tự động tạo sẵn 2 file `facebook_cookies.json` và `facebook_cookies.txt` trong cùng thư mục.\n\n"
            "Vui lòng làm theo các bước sau:\n\n"
            "1. CÀI ĐẶT \"COOKIE-EDITOR\":\n"
            "   - Mở trình duyệt Chrome/Edge và tìm kiếm \"Cookie-Editor\" trong cửa hàng tiện ích.\n"
            "   - Thêm tiện ích này vào trình duyệt của bạn.\n\n"
            "2. TRUY CẬP FACEBOOK:\n"
            "   - Mở một tab mới và truy cập trang `www.facebook.com`. Đăng nhập nếu bạn chưa đăng nhập.\n\n"
            "3. XUẤT COOKIE (2 LẦN):\n"
            "   - Nhấp vào biểu tượng \"Cookie-Editor\" trên thanh công cụ.\n"
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
        GuidePopup(self, title, message)

    def _show_usage_guide_popup(self):
        title = "Hướng dẫn Sử dụng Nhanh"
        message = (
            "Mẹo: Bạn có thể kéo và di chuyển bảng hướng dẫn này sang một bên để vừa đọc vừa thao tác trên giao diện chính của chương trình.\n\n"
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
        GuidePopup(self, title, message)

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