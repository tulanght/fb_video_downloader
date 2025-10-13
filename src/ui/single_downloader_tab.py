# file-path: src/ui/single_downloader_tab.py
# version: 1.0
# last-updated: 2025-10-10
# description: Giao diện và logic cho tính năng tải video đơn lẻ.

import customtkinter
import threading
import logging
from datetime import datetime

# Tái sử dụng các hàm cốt lõi đã có
from src.core.scraper import get_video_details_yt_dlp, standardize_facebook_url
from src.core.downloader import download_video_session

class SingleDownloaderTab(customtkinter.CTkFrame):
    def __init__(self, master, app_ref):
        super().__init__(master, fg_color="transparent")
        self.app = app_ref
        self.is_running_task = False

        self.grid_columnconfigure(0, weight=1)

        # --- Khung Giao diện ---
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(padx=10, pady=20, fill="x")
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Ô nhập URL
        customtkinter.CTkLabel(self.main_frame, text="URL Video/Reel:").grid(row=0, column=0, padx=10, pady=15, sticky="w")
        self.url_entry = customtkinter.CTkEntry(self.main_frame, placeholder_text="Dán link một video hoặc reel Facebook vào đây...")
        self.url_entry.grid(row=0, column=1, padx=10, pady=15, sticky="ew")

        # Các tùy chọn
        self.subtitle_checkbox = customtkinter.CTkCheckBox(self.main_frame, text="Tải phụ đề (nếu có)")
        self.subtitle_checkbox.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Nút Tải
        self.download_button = customtkinter.CTkButton(self.main_frame, text="Tải Ngay", command=self.start_download_task, height=40)
        self.download_button.grid(row=2, column=0, columnspan=2, padx=10, pady=20, sticky="ew")

        # Trạng thái
        self.status_label = customtkinter.CTkLabel(self, text="Sẵn sàng để tải.", text_color="gray")
        self.status_label.pack(padx=10, pady=10, fill="x")

    def update_status(self, message, is_error=False):
        """Cập nhật dòng trạng thái với màu sắc phù hợp."""
        color = "#D32F2F" if is_error else "gray"
        self.status_label.configure(text=message, text_color=color)
        if is_error:
            logging.error(message)
        else:
            logging.info(message)

    def start_download_task(self):
        """Bắt đầu luồng tải video."""
        video_url = self.url_entry.get()
        if not video_url:
            self.update_status("Lỗi: Vui lòng nhập URL của video.", is_error=True)
            return

        if self.is_running_task:
            self.update_status("Lỗi: Một tác vụ khác đang chạy.", is_error=True)
            return

        self.is_running_task = True
        self.download_button.configure(state="disabled", text="Đang xử lý...")
        
        should_download_subtitles = bool(self.subtitle_checkbox.get())

        thread = threading.Thread(target=self.download_worker, args=(video_url, should_download_subtitles))
        self.app.worker_threads.append(thread)
        thread.start()

    def download_worker(self, video_url, download_subtitles):
        """Worker chạy trong luồng riêng để tải video."""
        try:
            self.after(0, self.update_status, "Đang lấy thông tin video...")
            
            # 1. Lấy chi tiết video để có tiêu đề và các thông tin khác
            details = get_video_details_yt_dlp(video_url)
            if not details:
                raise Exception("Không thể lấy thông tin từ URL. Link có thể bị sai hoặc video ở chế độ riêng tư.")

            video_item = {
                "title": details.get("title", "Không có tiêu đề"),
                "upload_date": details.get("upload_date", ""),
                "url": standardize_facebook_url(video_url),
                "description": details.get("description", ""),
                # Thêm cờ `has_subtitle` dựa trên việc có muốn tải hay không
                "has_subtitle": download_subtitles 
            }

            # 2. Bắt đầu phiên tải với chỉ một video
            session_id = f"single_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Hàm callback để cập nhật giao diện
            def status_callback(message):
                self.after(0, self.update_status, message)
            
            # Bắt đầu tải
            download_generator = download_video_session(
                video_list=[video_item],
                identifier=session_id,
                status_callback=status_callback,
                progress_callback=None # Không cần progress bar cho tải đơn
            )
            
            # Chạy generator để thực hiện việc tải
            for result in download_generator:
                if result['status'] == 'success':
                    self.after(0, self.update_status, f"Tải thành công: {video_item['title']}")
                else:
                    raise Exception(f"Tải thất bại cho URL: {video_url}")

        except Exception as e:
            self.after(0, self.update_status, f"Lỗi: {e}")
        finally:
            self.is_running_task = False
            self.after(0, self.download_button.configure, {"state": "normal", "text": "Tải Ngay"})