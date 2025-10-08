# file-path: src/ui/downloader_tab.py
# version: 26.0 (Multi-threading Implementation)
# last-updated: 2025-10-08
# description: Tích hợp kiến trúc đa luồng cho bước lọc để tăng tốc độ, kèm tùy chọn đơn luồng.

import customtkinter
import threading
import tkinter.ttk as ttk
import json
import logging
import traceback
import os
from tkinter import filedialog
from datetime import datetime
from tkcalendar import DateEntry
# === THÊM IMPORT MỚI CHO ĐA LUỒNG ===
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.core.scraper import scrape_video_urls, get_video_details_yt_dlp, standardize_facebook_url
from src.core.downloader import download_video_session
from customtkinter import CTkToplevel

class CaptionViewerWindow(CTkToplevel):
    # ... (Nội dung lớp không đổi)
    def __init__(self, title, caption):
        super().__init__()
        self.title("Nội dung Caption")
        self.geometry("600x400")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        title_label = customtkinter.CTkLabel(self, text=title, font=customtkinter.CTkFont(size=14, weight="bold"))
        title_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        caption_textbox = customtkinter.CTkTextbox(self, wrap="word")
        caption_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        caption_textbox.insert("1.0", caption)
        caption_textbox.configure(state="disabled")

class DownloaderTab(customtkinter.CTkFrame):
    def __init__(self, master, app_ref):
        super().__init__(master)
        self.app = app_ref
        self.is_running_task = False
        self.stop_requested = threading.Event()
        self.is_scraping_done = False
        self.video_details_list = []
        self.scraped_links_cache = []
        self.caption_window = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # --- GIAO DIỆN ĐƯỢC BỐ CỤC LẠI ---
        
        # ** Khung 1: Input chính **
        self.top_frame = customtkinter.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.top_frame.grid_columnconfigure(1, weight=1)
        customtkinter.CTkLabel(self.top_frame, text="URL Trang Facebook:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.url_entry = customtkinter.CTkEntry(self.top_frame)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # ** Khung 2: Tùy chọn và các nút hành động chính **
        self.options_frame = customtkinter.CTkFrame(self)
        self.options_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.options_frame.grid_columnconfigure(4, weight=1)

        customtkinter.CTkLabel(self.options_frame, text="Số lần cuộn:").grid(row=0, column=0, padx=(10, 5), pady=10)
        self.scroll_count_entry = customtkinter.CTkEntry(self.options_frame, width=60)
        self.scroll_count_entry.insert(0, "5")
        self.scroll_count_entry.grid(row=0, column=1, padx=0, pady=10)
        
        customtkinter.CTkLabel(self.options_frame, text="Chờ (giây):").grid(row=0, column=2, padx=(15, 5), pady=10)
        self.scroll_delay_entry = customtkinter.CTkEntry(self.options_frame, width=60)
        self.scroll_delay_entry.insert(0, "3")
        self.scroll_delay_entry.grid(row=0, column=3, padx=0, pady=10)

        self.scrape_button = customtkinter.CTkButton(self.options_frame, text="Bước 1: Lấy Link", command=self.start_scraping_thread)
        self.scrape_button.grid(row=0, column=5, padx=10, pady=10)
        self.stop_button = customtkinter.CTkButton(self.options_frame, text="Dừng", command=self.request_stop_task, fg_color="darkred")
        self.stop_button.grid(row=0, column=6, padx=10, pady=10)

        # ** Khung 3: Lọc và các hành động phụ **
        self.action_frame = customtkinter.CTkFrame(self)
        self.action_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.filter_button = customtkinter.CTkButton(self.action_frame, text="Bước 2: Lọc", command=self.start_filtering_thread)
        self.filter_button.pack(side="left", padx=(10,5), pady=10)
        
        customtkinter.CTkLabel(self.action_frame, text="Từ:").pack(side="left", padx=(10, 5), pady=10)
        self.from_date_entry = DateEntry(self.action_frame, date_pattern='y-mm-dd', width=12)
        self.from_date_entry.pack(side="left", padx=0, pady=10)
        
        customtkinter.CTkLabel(self.action_frame, text="Đến:").pack(side="left", padx=(10, 5), pady=10)
        self.to_date_entry = DateEntry(self.action_frame, date_pattern='y-mm-dd', width=12)
        self.to_date_entry.pack(side="left", padx=0, pady=10)

        # === GIAO DIỆN ĐA LUỒNG MỚI ===
        self.threading_switch = customtkinter.CTkSwitch(self.action_frame, text="Đa luồng", onvalue=1, offvalue=0)
        self.threading_switch.select() # Mặc định bật
        self.threading_switch.pack(side="left", padx=(15, 5), pady=10)
        self.worker_count_entry = customtkinter.CTkEntry(self.action_frame, width=40)
        self.worker_count_entry.insert(0, "5") # Mặc định 5 luồng
        self.worker_count_entry.pack(side="left", padx=0, pady=10)
        
        self.download_button = customtkinter.CTkButton(self.action_frame, text="Bước 3: Tải video", command=self.start_download_task, fg_color="green")
        self.download_button.pack(side="right", padx=10, pady=10)
        
        # ... (các nút còn lại giữ nguyên)
        self.load_session_button = customtkinter.CTkButton(self.action_frame, text="Tải phiên", command=self.load_session)
        self.load_session_button.pack(side="right", padx=0, pady=10)
        self.save_session_button = customtkinter.CTkButton(self.action_frame, text="Lưu phiên", command=self.save_session)
        self.save_session_button.pack(side="right", padx=10, pady=10)
        self.import_txt_button = customtkinter.CTkButton(self.action_frame, text="Nhập TXT", command=self.import_from_txt)
        self.import_txt_button.pack(side="right", padx=0, pady=10)

        # ** Khung 4: Bảng kết quả **
        tree_frame = customtkinter.CTkFrame(self)
        tree_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        # ... (cấu hình Treeview không đổi)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        columns = ("#", "selected", "title", "date", "url")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.heading("#", text="STT")
        self.tree.heading("selected", text="Chọn")
        self.tree.heading("title", text="Tiêu đề")
        self.tree.heading("date", text="Ngày đăng")
        self.tree.heading("url", text="URL")
        self.tree.column("#", width=50, stretch=False, anchor="center")
        self.tree.column("selected", width=50, stretch=False, anchor="center")
        self.tree.column("title", width=350)
        self.tree.column("date", width=100, anchor="center")
        self.tree.column("url", width=200)
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<Double-1>", self.show_caption_for_selected_item)
        self.tree.bind("<Button-1>", self.on_tree_click)
        scrollbar = customtkinter.CTkScrollbar(tree_frame, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.status_label = customtkinter.CTkLabel(self, text="Sẵn sàng.", anchor="w")
        self.status_label.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        self.update_button_states()
        
    def update_button_states(self, is_busy=False):
        # ... (Nội dung hàm không đổi)
        has_results_in_tree = bool(self.tree.get_children())
        is_ready_to_filter = bool(self.scraped_links_cache)
        self.scrape_button.configure(state="disabled" if is_busy else "normal")
        self.filter_button.configure(state="disabled" if is_busy or not is_ready_to_filter else "normal")
        self.stop_button.configure(state="normal" if is_busy else "disabled")
        self.load_session_button.configure(state="disabled" if is_busy else "normal")
        self.import_txt_button.configure(state="disabled" if is_busy else "normal")
        self.save_session_button.configure(state="disabled" if is_busy or not has_results_in_tree else "normal")
        self.download_button.configure(state="disabled" if is_busy or not has_results_in_tree else "normal")

    def update_status(self, message):
        # ... (Nội dung hàm không đổi)
        self.status_label.configure(text=message)
        logging.info(message)

    def request_stop_task(self):
        # ... (Nội dung hàm không đổi)
        if self.is_running_task:
            self.stop_requested.set()
            self.update_status("Đã yêu cầu dừng, vui lòng chờ tác vụ hiện tại hoàn tất...")

    def start_scraping_thread(self):
        page_url = self.url_entry.get()
        if not page_url:
            self.update_status("Lỗi: Vui lòng nhập URL.")
            return
        try:
            scroll_count = int(self.scroll_count_entry.get())
            scroll_delay = float(self.scroll_delay_entry.get())
            if scroll_delay < 1: scroll_delay = 1
        except ValueError:
            self.update_status("Lỗi: 'Số lần cuộn' và 'Thời gian chờ' phải là số.")
            return
        
        self.update_button_states(is_busy=True)
        self.tree.delete(*self.tree.get_children())
        self.video_details_list = []
        self.scraped_links_cache = []
        self.stop_requested.clear()
        self.is_running_task = True
        
        thread = threading.Thread(target=self.scrape_worker, args=(page_url, scroll_count, scroll_delay))
        self.app.worker_threads = [thread]
        thread.start()

    def scrape_worker(self, page_url, scroll_count, scroll_delay):
        try:
            self.scraped_links_cache = scrape_video_urls(page_url, scroll_count, self.update_status, self.stop_requested, scroll_delay)
            if not self.stop_requested.is_set():
                self.after(0, self.update_status, f"Hoàn tất. Tìm thấy {len(self.scraped_links_cache)} link thô. Sẵn sàng để lọc.")
        except Exception:
            self.after(0, self.update_status, f"Lỗi nghiêm trọng khi lấy link:\n{traceback.format_exc()}")
        finally:
            self.is_running_task = False
            self.is_scraping_done = True
            self.after(0, self.update_button_states, False)
        
    def start_filtering_thread(self, source_links=None):
        links_to_process = source_links if source_links is not None else self.scraped_links_cache
        if not links_to_process:
            self.update_status("Không có link nào để lọc.")
            return
        
        self.update_button_states(is_busy=True)
        self.tree.delete(*self.tree.get_children())
        self.video_details_list = []
        self.stop_requested.clear()
        self.is_running_task = True
        
        # === LOGIC CHUYỂN ĐỔI LUỒNG ===
        if self.threading_switch.get() == 1:
            try:
                num_workers = int(self.worker_count_entry.get())
                if num_workers < 1: num_workers = 1
                if num_workers > 10: num_workers = 10 # Giới hạn 10 luồng để tránh quá tải
            except ValueError:
                num_workers = 5 # Mặc định nếu người dùng nhập sai
            
            thread = threading.Thread(target=self.get_details_worker_multithread, args=(links_to_process, num_workers))
        else:
            self.update_status("Chạy ở chế độ đơn luồng (chậm)...")
            thread = threading.Thread(target=self.get_details_worker_singlethread, args=(links_to_process,))
            
        self.app.worker_threads = [thread]
        thread.start()
        
    def get_details_worker_singlethread(self, links_to_process):
        # Đây là logic đơn luồng cũ
        from_date = self.from_date_entry.get_date()
        to_date = self.to_date_entry.get_date()
        try:
            total_links = len(links_to_process)
            for i, url in enumerate(links_to_process):
                if self.stop_requested.is_set(): break
                self.after(0, self.update_status, f"Đang lấy chi tiết video {i+1}/{total_links}...")
                details = get_video_details_yt_dlp(url)
                if details and details.get('upload_date'):
                    upload_date_dt = datetime.strptime(details['upload_date'], "%Y%m%d").date()
                    if (not from_date or upload_date_dt >= from_date) and (not to_date or upload_date_dt <= to_date):
                        video_item = self._create_video_item(url, details)
                        self.video_details_list.append(video_item)
                        self.after(0, self._insert_item_into_tree, video_item)
        finally:
            self.is_running_task = False
            self.after(0, self._finalize_filtering)
    
    def get_details_worker_multithread(self, links_to_process, num_workers):
        self.update_status(f"Đang chạy đa luồng với {num_workers} worker...")
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_url = {executor.submit(self._fetch_and_filter_one_video, url): url for url in links_to_process}
            
            for future in as_completed(future_to_url):
                if self.stop_requested.is_set():
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                try:
                    video_item = future.result()
                    if video_item:
                        self.video_details_list.append(video_item)
                        self.after(0, self._insert_item_into_tree, video_item)
                except Exception:
                    pass # Lỗi đã được log bên trong _fetch_and_filter_one_video
        
        self.is_running_task = False
        self.after(0, self._finalize_filtering_and_sort)

    
    def _fetch_and_filter_one_video(self, url):
        """Hàm nhỏ được mỗi luồng worker thực thi."""
        from_date = self.from_date_entry.get_date()
        to_date = self.to_date_entry.get_date()
        
        details = get_video_details_yt_dlp(url)
        if details and details.get('upload_date'):
            upload_date_dt = datetime.strptime(details['upload_date'], "%Y%m%d").date()
            if (not from_date or upload_date_dt >= from_date) and (not to_date or upload_date_dt <= to_date):
                return self._create_video_item(url, details)
        return None

    def _create_video_item(self, url, details):
        """Tạo dictionary video_item từ dữ liệu thô."""
        return {
            "title": details.get("title", "Không có tiêu đề"),
            "upload_date": datetime.strptime(details['upload_date'], "%Y%m%d").date().strftime("%Y-%m-%d"),
            "url": standardize_facebook_url(url),
            "description": details.get("description", "Không có caption.")
        }
    def _finalize_filtering_and_sort(self):
        """Hàm finalize cho đa luồng, cần sắp xếp lại vì kết quả trả về không theo thứ tự."""
        self.video_details_list = sorted(self.video_details_list, key=lambda x: x['upload_date'], reverse=True)
        self.tree.delete(*self.tree.get_children())
        for item in self.video_details_list:
            self._insert_item_into_tree(item)
        self._finalize_filtering()
        
    
    def _insert_item_into_tree(self, item):
        """Chèn một video item vào cuối Treeview."""
        index = len(self.tree.get_children()) + 1
        self.tree.insert("", "end", iid=str(index), values=(index, "☐", item["title"], item["upload_date"], item["url"]))

    def _finalize_filtering(self):
        """Chỉ cập nhật trạng thái và nút bấm, không sắp xếp hay vẽ lại."""
        if not self.stop_requested.is_set():
            self.update_status(f"Hoàn tất. Tìm thấy {len(self.video_details_list)} video hợp lệ.")
        else:
            self.update_status("Tác vụ đã bị dừng bởi người dùng.")
        self.update_button_states(is_busy=False)

    def on_tree_click(self, event):
        # ... (Nội dung hàm không đổi)
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell": return
        column_id = self.tree.identify_column(event.x)
        if column_id == "#2":
            item_id = self.tree.identify_row(event.y)
            if not item_id: return
            current_values = list(self.tree.item(item_id, 'values'))
            new_state = "☑" if current_values[1] == "☐" else "☐"
            current_values[1] = new_state
            self.tree.item(item_id, values=tuple(current_values))
    
    # ... (Các hàm còn lại không đổi)
    def start_download_task(self):
        selected_items = [i for i, item_id in enumerate(self.tree.get_children()) if self.tree.item(item_id)['values'][1] == "☑"]
        if not selected_items:
            self.update_status("Lỗi: Vui lòng chọn ít nhất một video để tải.")
            return
        videos_to_download = [self.video_details_list[i] for i in selected_items]
        self.update_button_states(is_busy=True)
        self.stop_requested.clear()
        self.is_running_task = True
        thread = threading.Thread(target=self.download_worker, args=(videos_to_download,))
        self.app.worker_threads = [thread]
        thread.start()

    def download_worker(self, videos_to_download):
        try:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            def status_callback(message): self.after(0, self.update_status, message)
            def progress_callback(_):
                if self.stop_requested.is_set(): raise yt_dlp.utils.DownloadError("Download cancelled by user.")
            download_generator = download_video_session(video_list=videos_to_download, identifier=session_id, status_callback=status_callback, progress_callback=progress_callback)
            for _ in download_generator:
                 if self.stop_requested.is_set():
                    self.after(0, self.update_status, "Đã dừng quá trình tải.")
                    break
            else: self.after(0, self.update_status, "Hoàn tất tải tất cả video đã chọn!")
        except Exception:
            self.after(0, self.update_status, f"Lỗi trong quá trình tải: {traceback.format_exc()}")
        finally:
            self.is_running_task = False
            self.after(0, self.update_button_states, False)

    def save_session(self):
        if not self.video_details_list:
            self.update_status("Không có dữ liệu để lưu.")
            return
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], title="Lưu phiên làm việc")
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f: json.dump(self.video_details_list, f, indent=4, ensure_ascii=False)
            self.update_status(f"Đã lưu phiên thành công vào: {os.path.basename(filepath)}")
        except Exception as e: self.update_status(f"Lỗi: Không thể lưu file: {e}")

    def load_session(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], title="Tải phiên làm việc")
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f: loaded_data = json.load(f)
            self.video_details_list = loaded_data # Nạp dữ liệu
            self.scraped_links_cache = [item['url'] for item in loaded_data]
            self.update_button_states(is_busy=True)
            self.tree.delete(*self.tree.get_children())
            # Hiển thị lại cây từ dữ liệu đã nạp
            for item in self.video_details_list:
                self._insert_item_into_tree(item)
            self.update_status(f"Đã tải thành công {len(self.video_details_list)} video từ phiên.")
            self.update_button_states(is_busy=False)
        except Exception as e:
            self.update_status(f"Lỗi: Không thể đọc file JSON: {e}")
            self.update_button_states(is_busy=False)

    def import_from_txt(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")], title="Nhập danh sách URL từ file .txt")
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f: links_from_file = [line.strip() for line in f if line.strip().startswith("http")]
            self.start_filtering_thread(source_links=links_from_file)
        except Exception as e: self.update_status(f"Lỗi: {e}")
    
    def show_caption_for_selected_item(self, event):
        selected_items = self.tree.selection()
        if not selected_items: return
        item_id = selected_items[0]
        try:
            # Lấy index từ STT của dòng được chọn
            item_index = int(self.tree.item(item_id)['values'][0]) - 1
            if 0 <= item_index < len(self.video_details_list):
                found_video = self.video_details_list[item_index]
                if self.caption_window is None or not self.caption_window.winfo_exists():
                    self.caption_window = CaptionViewerWindow(title=found_video.get('title', 'N/A'), caption=found_video.get('description', 'Không có caption.'))
                    self.caption_window.transient(self.app)
                    self.caption_window.grab_set()
                else: self.caption_window.focus()
        except (ValueError, IndexError):
            self.update_status("Lỗi khi lấy caption.")