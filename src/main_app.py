# file-path: src/main_app.py
# version: 1.0
# last-updated: 2025-10-03
# description: Lớp ứng dụng chính, tạo cửa sổ và quản lý các tab giao diện.

import customtkinter
from src.ui.downloader_tab import DownloaderTab

class MainApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- Cấu hình cửa sổ chính ---
        self.title("FB Page Video Downloader")
        self.geometry("800x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Tạo Tab View ---
        self.tab_view = customtkinter.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # --- Thêm các tab vào Tab View ---
        self.tab_view.add("Tải Video")
        # Thêm các tab khác ở đây trong tương lai
        # self.tab_view.add("Lịch sử")
        # self.tab_view.add("Cài đặt")

        # --- Gắn giao diện của từng tab ---
        self.downloader_tab = DownloaderTab(master=self.tab_view.tab("Tải Video"))
        self.downloader_tab.pack(expand=True, fill="both")