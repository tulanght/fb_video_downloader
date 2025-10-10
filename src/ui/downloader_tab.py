# file-path: src/ui/downloader_tab.py
# version: 31.0 (Final Layout Fix)
# last-updated: 2025-10-08
# description: Sắp xếp lại action_frame bằng grid để sửa lỗi che khuất widget.

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
from concurrent.futures import ThreadPoolExecutor, as_completed
import yt_dlp
from src.core.scraper import scrape_video_urls, get_video_details_yt_dlp, standardize_facebook_url
from src.core.downloader import download_video_session
from src.ui.components import CaptionViewerWindow
from src.core.app_path import get_app_base_path
from src import config

class DownloaderTab(customtkinter.CTkFrame):
    def __init__(self, master, app_ref):
        super().__init__(master, fg_color="transparent")
        self.app = app_ref
        # ... (Các thuộc tính khác)
        self.is_running_task = False
        self.stop_requested = threading.Event()
        self.is_scraping_done = False
        self.video_details_list = []
        self.scraped_links_cache = []
        self.caption_window = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ** Khung 1: Input & Cấu hình cuộn trang **
        self.top_frame = customtkinter.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.top_frame.grid_columnconfigure(1, weight=1)

        customtkinter.CTkLabel(self.top_frame, text="URL Trang Facebook:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.url_entry = customtkinter.CTkEntry(self.top_frame, placeholder_text="https://www.facebook.com/TenPage/reels/")
        self.url_entry.grid(row=0, column=1, padx=(0,10), pady=10, sticky="ew")

        customtkinter.CTkLabel(self.top_frame, text="Số lần cuộn:").grid(row=0, column=2, padx=(10, 5), pady=10)
        self.scroll_count_entry = customtkinter.CTkEntry(self.top_frame, width=60)
        self.scroll_count_entry.insert(0, "5")
        self.scroll_count_entry.grid(row=0, column=3, padx=0, pady=10)
        
        customtkinter.CTkLabel(self.top_frame, text="Chờ (giây):").grid(row=0, column=4, padx=(10, 5), pady=10)
        self.scroll_delay_entry = customtkinter.CTkEntry(self.top_frame, width=60)
        self.scroll_delay_entry.insert(0, "3")
        self.scroll_delay_entry.grid(row=0, column=5, padx=0, pady=10)

        # === SỬA LỖI: Chỉ dùng text_color_disabled ===
        self.scrape_button = customtkinter.CTkButton(self.top_frame, text="Bước 1: Lấy Link", command=self.start_scraping_thread, width=120, text_color_disabled=config.DISABLED_TEXT_COLOR)
        self.scrape_button.grid(row=0, column=6, padx=(20, 10), pady=10)
        self.stop_button = customtkinter.CTkButton(self.top_frame, text="Dừng", command=self.request_stop_task, fg_color="#D32F2F", hover_color="#B71C1C", width=60, text_color_disabled=config.DISABLED_TEXT_COLOR)
        self.stop_button.grid(row=0, column=7, padx=(0, 10), pady=10)

        # ** Khung 2: Lọc và các hành động (ĐƯỢC THIẾT KẾ LẠI) **
        self.action_frame = customtkinter.CTkFrame(self)
        self.action_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        # Sử dụng grid để kiểm soát vị trí chính xác
        self.action_frame.grid_columnconfigure(5, weight=1) # Cột co giãn ở giữa
        
        self.filter_button = customtkinter.CTkButton(self.action_frame, text="Bước 2: Lọc", command=self.start_filtering_thread, text_color_disabled=config.DISABLED_TEXT_COLOR)
        self.filter_button.grid(row=0, column=0, padx=(10,5), pady=10)
        
        customtkinter.CTkLabel(self.action_frame, text="Từ:").grid(row=0, column=1, padx=(10, 5), pady=10)
        self.from_date_entry = DateEntry(self.action_frame, date_pattern='y-mm-dd', width=12)
        self.from_date_entry.grid(row=0, column=2, padx=0, pady=10)
        
        customtkinter.CTkLabel(self.action_frame, text="Đến:").grid(row=0, column=3, padx=(10, 5), pady=10)
        self.to_date_entry = DateEntry(self.action_frame, date_pattern='y-mm-dd', width=12)
        self.to_date_entry.grid(row=0, column=4, padx=0, pady=10)

        # Đặt nhóm đa luồng vào một khung riêng để dễ quản lý
        threading_frame = customtkinter.CTkFrame(self.action_frame, fg_color="transparent")
        threading_frame.grid(row=0, column=5, padx=(20,0), pady=10, sticky="w")
        self.threading_switch = customtkinter.CTkSwitch(threading_frame, text="Đa luồng", onvalue=1, offvalue=0)
        self.threading_switch.select()
        self.threading_switch.pack(side="left")
        self.worker_count_entry = customtkinter.CTkEntry(threading_frame, width=40)
        self.worker_count_entry.insert(0, "5")
        self.worker_count_entry.pack(side="left", padx=5)
        
        # Nhóm các nút phụ về bên phải
        session_frame = customtkinter.CTkFrame(self.action_frame, fg_color="transparent")
        session_frame.grid(row=0, column=6, padx=10, pady=10, sticky="e")

        self.save_session_button = customtkinter.CTkButton(session_frame, text="Lưu", command=self.save_session, width=80, text_color=config.BUTTON_TEXT_COLOR, fg_color=config.BUTTON_FG_COLOR, hover_color=config.BUTTON_HOVER_COLOR, text_color_disabled=config.DISABLED_TEXT_COLOR)
        self.save_session_button.pack(side="left", padx=5)
        self.load_session_button = customtkinter.CTkButton(session_frame, text="Tải", command=self.load_session, width=80, text_color=config.BUTTON_TEXT_COLOR, fg_color=config.BUTTON_FG_COLOR, hover_color=config.BUTTON_HOVER_COLOR, text_color_disabled=config.DISABLED_TEXT_COLOR)
        self.load_session_button.pack(side="left", padx=0)
        self.import_txt_button = customtkinter.CTkButton(session_frame, text="Nhập TXT", command=self.import_from_txt, width=100, text_color=config.BUTTON_TEXT_COLOR, fg_color=config.BUTTON_FG_COLOR, hover_color=config.BUTTON_HOVER_COLOR, text_color_disabled=config.DISABLED_TEXT_COLOR)
        self.import_txt_button.pack(side="left", padx=5)
        
        self.download_button = customtkinter.CTkButton(self.action_frame, text="Bước 3: Tải Video", command=self.start_download_task, fg_color="#4CAF50", hover_color="#388E3C", width=140, text_color_disabled=config.DISABLED_TEXT_COLOR)
        self.download_button.grid(row=0, column=7, padx=(0, 10), pady=10, sticky="e")

        # ** Khung 3: Bảng kết quả **
        tree_frame = customtkinter.CTkFrame(self)
        tree_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        # ... (Cấu hình treeview không đổi)
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
        
        self.status_label = customtkinter.CTkLabel(self, text="Sẵn sàng.", anchor="w", text_color="gray")
        self.status_label.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        self.update_button_states()

    # === TOÀN BỘ CÁC HÀM LOGIC ĐÃ ĐƯỢC KHÔI PHỤC ĐẦY ĐỦ ===
    def update_button_states(self, is_busy=False):
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
        self.status_label.configure(text=message)
        logging.info(message)

    def request_stop_task(self):
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
        
        if self.threading_switch.get() == 1:
            try:
                num_workers = int(self.worker_count_entry.get())
                if num_workers < 1: num_workers = 1
                if num_workers > config.MAX_WORKERS: num_workers = config.MAX_WORKERS
            except ValueError:
                num_workers = config.DEFAULT_WORKER_COUNT
            
            thread = threading.Thread(target=self.get_details_worker_multithread, args=(links_to_process, num_workers))
        else:
            self.update_status("Chạy ở chế độ đơn luồng (chậm)...")
            thread = threading.Thread(target=self.get_details_worker_singlethread, args=(links_to_process,))
            
        self.app.worker_threads = [thread]
        thread.start()

    def get_details_worker_singlethread(self, links_to_process):
        from_date = self.from_date_entry.get_date()
        to_date = self.to_date_entry.get_date()
        try:
            total_links = len(links_to_process)
            for i, url in enumerate(links_to_process):
                if self.stop_requested.is_set(): break
                self.after(0, self.update_status, f"Đơn luồng: Đang xử lý {i+1}/{total_links}...")
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
        self.update_status(f"Đa luồng: Đang chạy với {num_workers} worker...")
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_url = {executor.submit(self._fetch_and_filter_one_video, url): url for url in links_to_process}
            processed_count = 0
            total_links = len(links_to_process)
            for future in as_completed(future_to_url):
                processed_count += 1
                self.after(0, self.update_status, f"Đa luồng: Đang xử lý {processed_count}/{total_links}...")
                if self.stop_requested.is_set():
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                try:
                    video_item = future.result()
                    if video_item:
                        self.video_details_list.append(video_item)
                        self.after(0, self._insert_item_into_tree, video_item)
                except Exception:
                    pass
        self.is_running_task = False
        self.after(0, self._finalize_filtering_and_sort)

    def _fetch_and_filter_one_video(self, url):
        from_date = self.from_date_entry.get_date()
        to_date = self.to_date_entry.get_date()
        details = get_video_details_yt_dlp(url)
        if details and details.get('upload_date'):
            upload_date_dt = datetime.strptime(details['upload_date'], "%Y%m%d").date()
            if (not from_date or upload_date_dt >= from_date) and (not to_date or upload_date_dt <= to_date):
                return self._create_video_item(url, details)
        return None

    def _create_video_item(self, url, details):
        return { "title": details.get("title", "Không có tiêu đề"), "upload_date": datetime.strptime(details['upload_date'], "%Y%m%d").date().strftime("%Y-%m-%d"), "url": standardize_facebook_url(url), "description": details.get("description", "Không có caption.") }
    
    def _insert_item_into_tree(self, item):
        index = len(self.tree.get_children()) + 1
        self.tree.insert("", "end", iid=str(index), values=(index, "☐", item["title"], item["upload_date"], item["url"]))

    def _finalize_filtering_and_sort(self):
        self.video_details_list = sorted(self.video_details_list, key=lambda x: x['upload_date'], reverse=True)
        self.tree.delete(*self.tree.get_children())
        for i, item in enumerate(self.video_details_list):
            self.tree.insert("", "end", iid=str(i+1), values=(i + 1, "☐", item["title"], item["upload_date"], item["url"]))
        self._finalize_filtering()
        
    def _finalize_filtering(self):
        if not self.stop_requested.is_set():
            self.update_status(f"Hoàn tất. Tìm thấy {len(self.video_details_list)} video hợp lệ.")
        else:
            self.update_status("Tác vụ đã bị dừng bởi người dùng.")
        self.update_button_states(is_busy=False)
        
    def on_tree_click(self, event):
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
            
        sessions_dir = os.path.join(get_app_base_path(), config.SESSIONS_DIR)
        os.makedirs(sessions_dir, exist_ok=True)
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Lưu phiên làm việc",
            initialdir=sessions_dir
        )
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f: json.dump(self.video_details_list, f, indent=4, ensure_ascii=False)
            self.update_status(f"Đã lưu phiên thành công vào: {os.path.basename(filepath)}")
        except Exception as e: self.update_status(f"Lỗi: Không thể lưu file: {e}")

    def load_session(self):
        sessions_dir = os.path.join(get_app_base_path(), config.SESSIONS_DIR)
        
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Tải phiên làm việc",
            initialdir=sessions_dir
        )
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f: loaded_data = json.load(f)
            self.video_details_list = loaded_data
            self.scraped_links_cache = [item['url'] for item in loaded_data]
            self.update_button_states(is_busy=True)
            self.tree.delete(*self.tree.get_children())
            self._finalize_filtering_and_sort()
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
                    # SỬA LỖI: Thêm 'master=self.app' và loại bỏ các lệnh gọi thừa
                    self.caption_window = CaptionViewerWindow(
                        master=self.app, 
                        title=found_video.get('title', 'N/A'), 
                        caption=found_video.get('description', 'Không có caption.')
                    )
                else:
                    self.caption_window.focus()
        except (ValueError, IndexError):
            self.update_status("Lỗi khi lấy caption.")