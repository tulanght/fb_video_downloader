# file-path: src/ui/downloader_tab.py
# version: 1.1
# last-updated: 2025-10-03
# description: Cập nhật giao diện để hiển thị tiêu đề và thêm nhãn trạng thái.

import customtkinter
import threading
from src.core.scraper import get_videos_from_page

class DownloaderTab(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) # Tăng row lên 3 để chứa status_label

        # --- Khung nhập liệu ---
        self.input_frame = customtkinter.CTkFrame(self)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(1, weight=1)
        # (Các widget trong input_frame không đổi)
        self.url_label = customtkinter.CTkLabel(self.input_frame, text="URL Facebook Page:")
        self.url_label.grid(row=0, column=0, padx=10, pady=10)
        self.url_entry = customtkinter.CTkEntry(self.input_frame, placeholder_text="Dán link của tab Videos hoặc Reels vào đây...")
        self.url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.scrape_button = customtkinter.CTkButton(self.input_frame, text="Lấy danh sách Video", command=self.start_scraping_thread)
        self.scrape_button.grid(row=0, column=2, padx=10, pady=10)

        # --- Thanh tiến trình & Trạng thái ---
        self.progress_bar = customtkinter.CTkProgressBar(self, indeterminate_speed=1)
        self.progress_bar.grid(row=1, column=0, padx=10, pady=(5, 0), sticky="ew")
        self.progress_bar.set(0)

        self.status_label = customtkinter.CTkLabel(self, text="", text_color="gray")
        self.status_label.grid(row=2, column=0, padx=10, pady=(0, 5), sticky="w")

        # --- Khung hiển thị kết quả ---
        self.result_frame = customtkinter.CTkScrollableFrame(self, label_text="Danh sách Video tìm thấy")
        self.result_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

    def start_scraping_thread(self):
        url = self.url_entry.get()
        if not url: return

        self.scrape_button.configure(state="disabled")
        self.progress_bar.start()
        self.update_status("Đang khởi động trình duyệt và cuộn trang...")
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        thread = threading.Thread(target=self.scrape_links_worker, args=(url,))
        thread.start()

    def scrape_links_worker(self, url):
        # Truyền cả tham chiếu của tab (self) vào để scraper có thể cập nhật trạng thái
        video_list = get_videos_from_page(url, scroll_count=15, downloader_tab_ref=self)
        self.after(100, self.update_ui_with_results, video_list)

    def update_status(self, message):
        """Hàm an toàn để cập nhật nhãn trạng thái từ luồng nền."""
        self.status_label.configure(text=message)

    def update_ui_with_results(self, video_list):
        self.progress_bar.stop()
        self.progress_bar.set(0)
        self.update_status(f"Hoàn tất! Tìm thấy {len(video_list)} video.")

        if video_list:
            for i, video in enumerate(video_list):
                # Hiển thị tiêu đề thay vì URL
                title = video.get('title', 'Không có tiêu đề')
                display_text = f"{i+1}. {title}"
                link_label = customtkinter.CTkLabel(self.result_frame, text=display_text, wraplength=600, justify="left")
                link_label.pack(anchor="w", padx=5, pady=2)
        else:
            error_label = customtkinter.CTkLabel(self.result_frame, text="Không tìm thấy video nào.")
            error_label.pack(anchor="w", padx=5)

        self.scrape_button.configure(state="normal")