# file-path: src/ui/downloader_tab.py
# version: 8.1 (Synced & Stable)
# last-updated: 2025-10-05
# description: Phiên bản ổn định, đồng bộ với scraper.py v6.0.

import customtkinter
import threading
import tkinter.ttk as ttk
import json
import logging
import traceback
from tkinter import filedialog
from datetime import datetime
from tkcalendar import DateEntry
from src.core.scraper import scrape_video_urls, get_video_details_yt_dlp
from src.core.downloader import download_video_session
class DownloaderTab(customtkinter.CTkFrame):
    def __init__(self, master, app_ref):
        super().__init__(master)
        
        self.app = app_ref
        self.stop_requested = threading.Event()
        self.scraped_links = []
        self.video_details_list = []
        self.is_running_task = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Giao diện ---
        self.options_frame = customtkinter.CTkFrame(self)
        self.options_frame.grid(row=0, column=0, padx=10, pady=(10,5), sticky="ew")
        self.options_frame.grid_columnconfigure(1, weight=1)
        
        customtkinter.CTkLabel(self.options_frame, text="URL Facebook Page:").grid(row=0, column=0, padx=10, pady=10)
        self.url_entry = customtkinter.CTkEntry(self.options_frame, placeholder_text="Dán link của tab Videos hoặc Reels...")
        self.url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.scrape_button = customtkinter.CTkButton(self.options_frame, text="1. Lấy URL Online", command=self.start_scraping_thread)
        self.scrape_button.grid(row=0, column=2, padx=10, pady=10)
        
        self.filter_frame = customtkinter.CTkFrame(self)
        self.filter_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.filter_frame.grid_columnconfigure(8, weight=1)
        
        customtkinter.CTkLabel(self.filter_frame, text="Lọc:").grid(row=0, column=0, padx=(10,0), pady=10)
        self.start_date_entry = DateEntry(self.filter_frame, date_pattern='y-mm-dd', width=12)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=10)
        customtkinter.CTkLabel(self.filter_frame, text="đến").grid(row=0, column=2)
        self.end_date_entry = DateEntry(self.filter_frame, date_pattern='y-mm-dd', width=12)
        self.end_date_entry.grid(row=0, column=3, padx=5, pady=10)
        self.filter_button = customtkinter.CTkButton(self.filter_frame, text="2. Lọc & Lấy Chi tiết", command=self.start_filtering_thread, state="disabled")
        self.filter_button.grid(row=0, column=4, padx=5, pady=10)
        
        self.import_button = customtkinter.CTkButton(self.filter_frame, text="Nhập TXT", width=100, command=self.import_from_txt)
        self.import_button.grid(row=0, column=5, padx=(10, 5), pady=10)
        self.load_button = customtkinter.CTkButton(self.filter_frame, text="Tải Phiên", width=100, command=self.load_session_from_json)
        self.load_button.grid(row=0, column=6, padx=5, pady=10)
        self.save_button = customtkinter.CTkButton(self.filter_frame, text="Lưu Phiên", width=100, command=self.save_session_to_json, state="disabled")
        self.save_button.grid(row=0, column=7, padx=5, pady=10)
        
        self.status_label = customtkinter.CTkLabel(self.filter_frame, text="Sẵn sàng.", text_color="gray")
        self.status_label.grid(row=0, column=8, padx=10, pady=10, sticky="w")
        
        self.result_frame = customtkinter.CTkFrame(self)
        self.result_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.result_frame.grid_columnconfigure(0, weight=1)
        self.result_frame.grid_rowconfigure(0, weight=1)
        self._create_treeview()

        self.progress_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.progress_frame.grid(row=3, column=0, padx=10, pady=(0,5), sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.realtime_status_label = customtkinter.CTkLabel(self.progress_frame, text="", text_color="gray")
        self.realtime_status_label.grid(row=0, column=0, sticky="e")
        
        self.download_frame = customtkinter.CTkFrame(self)
        self.download_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        self.download_frame.grid_columnconfigure(2, weight=1)
        
        self.download_button = customtkinter.CTkButton(self.download_frame, text="3. Tải Video Đã Chọn", command=self.start_download_thread, state="disabled")
        self.download_button.grid(row=0, column=0, padx=10, pady=10)
        self.download_progress_label = customtkinter.CTkLabel(self.download_frame, text="")
        self.download_progress_label.grid(row=0, column=1, padx=10, pady=10)
        self.download_progressbar = customtkinter.CTkProgressBar(self.download_frame, orientation="horizontal")
        self.download_progressbar.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        self.download_progressbar.set(0)

    def _create_treeview(self):
        self.tree = ttk.Treeview(self.result_frame, columns=('#', 'title', 'date', 'subtitle', 'url'), show='headings')
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.tag_configure('success', background='#D4EDDA')
        self.tree.tag_configure('fail', background='#FFF3CD')
        self.tree.heading('#', text='STT')
        self.tree.heading('title', text='Tiêu đề')
        self.tree.heading('date', text='Ngày đăng')
        self.tree.heading('subtitle', text='Phụ đề')
        self.tree.heading('url', text='URL')
        self.tree.column('#', width=40, anchor='center', stretch=False)
        self.tree.column('title', width=400)
        self.tree.column('date', width=100, anchor='center')
        self.tree.column('subtitle', width=60, anchor='center')
        self.tree.column('url', width=250)
        v_scrollbar = customtkinter.CTkScrollbar(self.result_frame, command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar = customtkinter.CTkScrollbar(self.result_frame, command=self.tree.xview, orientation="horizontal")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    def _update_button_states(self, is_busy=False):
        state = "disabled" if is_busy else "normal"
        self.scrape_button.configure(state=state)
        self.import_button.configure(state=state)
        self.load_button.configure(state=state)
        self.filter_button.configure(state="normal" if not is_busy and self.scraped_links else "disabled")
        self.save_button.configure(state="normal" if not is_busy and self.video_details_list else "disabled")
        self.download_button.configure(state="normal" if not is_busy and self.video_details_list else "disabled")
    
    def request_stop_task(self):
        self.stop_requested.set()

    def update_status(self, message):
        self.status_label.configure(text=message)

    # --- LUỒNG 1: LẤY URL (Kiến trúc ổn định) ---
    def start_scraping_thread(self):
        url = self.url_entry.get()
        if not url: return
        
        self._update_button_states(is_busy=True)
        self.tree.delete(*self.tree.get_children())
        self.scraped_links = []; self.video_details_list = []
        self.stop_requested.clear()
        self.is_running_task = True
        
        thread = threading.Thread(target=self.scrape_links_worker, args=(url,))
        self.app.worker_threads = [thread]
        thread.start()

    def scrape_links_worker(self, url):
        links = []
        try:
            # Gọi hàm scraper và truyền hàm callback cho status
            links = scrape_video_urls(url, scroll_count=15, status_callback=lambda msg: self.after(0, self.update_status, msg))
        finally:
            self.is_running_task = False
            # Gửi toàn bộ danh sách `links` về hàm update_ui_after_scraping
            self.after(0, self.update_ui_after_scraping, links)

    def update_ui_after_scraping(self, links):
        self.scraped_links = links
        if self.scraped_links:
            for i, link_info in enumerate(self.scraped_links):
                self.tree.insert('', 'end', values=(i + 1, "Đang chờ lấy chi tiết...", "", "", link_info['url']), iid=link_info['url'])
            self.update_status(f"Đã tìm thấy {len(self.scraped_links)} links. Sẵn sàng để lọc.")
        else:
            self.update_status("Không tìm thấy link nào.")
        self._update_button_states(is_busy=False)

    # --- LUỒNG 2: LỌC & LẤY CHI TIẾT (Logic real-time mà bạn nhớ) ---
    def start_filtering_thread(self, source_links=None):
        self._update_button_states(is_busy=True)
        self.tree.delete(*self.tree.get_children())
        self.video_details_list = []
        self.stop_requested.clear()
        self.is_running_task = True
        links_to_process = source_links if source_links is not None else self.scraped_links
        start_date = self.start_date_entry.get_date()
        end_date = self.end_date_entry.get_date()
        thread = threading.Thread(target=self.filter_and_fetch_worker, args=(links_to_process, start_date, end_date))
        self.app.worker_threads = [thread]
        thread.start()

    def filter_and_fetch_worker(self, links_to_process, start_date, end_date):
        try:
            total_links = len(links_to_process)
            found_count = 0
            for i, link_info in enumerate(links_to_process):
                if self.stop_requested.is_set(): break
                status_msg = f"Đang kiểm tra {i+1}/{total_links}... (Tìm thấy: {found_count})"
                self.after(0, self.update_status, status_msg)
                
                details = get_video_details_yt_dlp(link_info['url'])
                if not details or not details.get('upload_date'): continue
                
                try:
                    video_date = datetime.strptime(details['upload_date'], "%Y%m%d").date()
                    if (start_date and video_date < start_date) or (end_date and video_date > end_date): continue
                    
                    found_count += 1
                    details['stt'] = found_count
                    details['url'] = link_info['url']
                    details['upload_date_str'] = video_date.strftime("%Y-%m-%d")
                    details['status'] = 'pending'
                    self.video_details_list.append(details)
                    self.after(0, self.add_item_to_tree, details)
                except (ValueError, TypeError): continue
        finally:
            self.is_running_task = False
            self.after(0, self.finalize_filtering)
        
    def add_item_to_tree(self, item):
        subtitle_check = "✓" if item.get('subtitle_path') else ""
        self.tree.insert('', 'end', values=(item['stt'], item['title'], item['upload_date_str'], subtitle_check, item['url']), iid=item['url'])
        self.realtime_status_label.configure(text=f"Đã lọc được {item['stt']} video")

    def finalize_filtering(self):
        self.video_details_list.sort(key=lambda x: x.get('upload_date_str', '0'), reverse=True)
        self.tree.delete(*self.tree.get_children())
        for i, item in enumerate(self.video_details_list):
            item['stt'] = i + 1
            tags = (item.get('status', 'pending'),)
            subtitle_check = "✓" if item.get('subtitle_path') else ""
            self.tree.insert('', 'end', values=(item['stt'], item['title'], item['upload_date_str'], subtitle_check, item['url']), tags=tags, iid=item['url'])
        self.update_status(f"Hoàn tất! Hiển thị {len(self.video_details_list)} video phù hợp.")
        self._update_button_states(is_busy=False)

    def start_download_thread(self):
        selected_items = self.tree.selection()
        if not selected_items:
            self.update_status("Lỗi: Vui lòng chọn ít nhất một video để tải."); return
        videos_to_download = []
        for item_id in selected_items:
            url_from_tree = self.tree.item(item_id)['values'][4]
            for video in self.video_details_list:
                if video['url'] == url_from_tree: videos_to_download.append(video); break
        if not videos_to_download:
            self.update_status("Lỗi: Không tìm thấy dữ liệu cho video đã chọn."); return
            
        self._update_button_states(is_busy=True)
        self.is_running_task = True
        self.stop_requested.clear()
        page_identifier = self.url_entry.get() or "downloaded_session"
        thread = threading.Thread(target=self.download_worker, args=(videos_to_download, page_identifier))
        self.app.worker_threads = [thread]
        thread.start()

    def download_worker(self, videos_to_download, page_identifier):
        success_count = 0; fail_count = 0
        try:
            for result in download_video_session(videos_to_download, page_identifier, lambda msg: self.after(0, self.update_status, msg), self.update_download_progress):
                if self.stop_requested.is_set(): break
                if result.get('status') == 'success': success_count += 1
                else: fail_count += 1
                self.after(0, self.update_row_status, result)
        finally:
            self.is_running_task = False
            summary = f"Tải hoàn tất. Thành công: {success_count}/{len(videos_to_download)}. Thất bại: {fail_count}."
            self.after(0, self.finalize_download, summary)

    def update_download_progress(self, progress_str):
        try:
            progress_float = float(progress_str.replace('%','').strip()) / 100
            self.download_progressbar.set(progress_float)
            self.download_progress_label.configure(text=f"{progress_float*100:.1f}%")
        except (ValueError, TypeError): pass

    def update_row_status(self, result: dict):
        url = result.get('url'); status = result.get('status')
        if not url or not status or not self.tree.exists(url): return
        self.tree.item(url, tags=(status,))
        if result.get('subtitle_path'): self.tree.set(url, 'subtitle', '✓')
        for video in self.video_details_list:
            if video['url'] == url:
                video['status'] = status; video['subtitle_path'] = result.get('subtitle_path')
                break

    def finalize_download(self, summary_message: str):
        self.update_status(summary_message)
        self._update_button_states(is_busy=False)

    def save_session_to_json(self):
        if not self.video_details_list: return
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], title="Lưu phiên làm việc")
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f: json.dump(self.video_details_list, f, ensure_ascii=False, indent=4)
            self.update_status(f"Đã lưu thành công vào {filepath.split('/')[-1]}")
        except Exception as e: self.update_status(f"Lỗi: Không thể lưu file: {e}")

    def load_session_from_json(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f: loaded_data = json.load(f)
            self.scraped_links = [{'url': item['url']} for item in loaded_data]
            self.finalize_filtering(loaded_data)
        except Exception as e: self.update_status(f"Lỗi: {e}")

    def import_from_txt(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                links_from_file = [{'url': line.strip()} for line in f if line.strip().startswith("http")]
            self.start_filtering_thread(source_links=links_from_file)
        except Exception as e: self.update_status(f"Lỗi: {e}")