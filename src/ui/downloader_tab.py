# file-path: src/ui/downloader_tab.py
# version: 3.0
# last-updated: 2025-10-04
# description: Sửa lỗi logic không tìm thấy video đã chọn và thêm debug log.

# (Các import không đổi, chỉ thêm downloader)
import customtkinter, threading, tkinter.ttk as ttk, queue, json
from tkinter import filedialog
from datetime import datetime
from tkcalendar import DateEntry
from src.core.scraper import scrape_video_urls, get_video_details_yt_dlp, standardize_facebook_url
from src.core.downloader import download_videos # <-- THÊM MỚI
import logging # <-- THÊM DÒNG NÀY

class DownloaderTab(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        # (Phần khởi tạo biến và layout không đổi)
        self.scraped_links = []; self.video_details_list = []; self.url_queue = queue.Queue(); self.is_running_task = False
        self.grid_columnconfigure(0, weight=1); self.grid_rowconfigure(2, weight=1)

        # --- Giao diện (thêm nút Tải và thanh tiến trình Tải) ---
        self.options_frame = customtkinter.CTkFrame(self); self.options_frame.grid(row=0, column=0, padx=10, pady=(10,5), sticky="ew") #...
        self.options_frame.grid_columnconfigure(1, weight=1)
        customtkinter.CTkLabel(self.options_frame, text="URL Facebook Page:").grid(row=0, column=0, padx=10, pady=10)
        self.url_entry = customtkinter.CTkEntry(self.options_frame, placeholder_text="Dán link của tab Videos hoặc Reels..."); self.url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.scrape_button = customtkinter.CTkButton(self.options_frame, text="1. Lấy URL Online", command=self.start_scraping_thread); self.scrape_button.grid(row=0, column=2, padx=10, pady=10)
        
        self.filter_frame = customtkinter.CTkFrame(self); self.filter_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew") #...
        self.filter_frame.grid_columnconfigure(8, weight=1)
        customtkinter.CTkLabel(self.filter_frame, text="Lọc:").grid(row=0, column=0, padx=(10,0), pady=10)
        self.start_date_entry = DateEntry(self.filter_frame, date_pattern='y-mm-dd', width=12); self.start_date_entry.grid(row=0, column=1, padx=5, pady=10)
        customtkinter.CTkLabel(self.filter_frame, text="đến").grid(row=0, column=2)
        self.end_date_entry = DateEntry(self.filter_frame, date_pattern='y-mm-dd', width=12); self.end_date_entry.grid(row=0, column=3, padx=5, pady=10)
        self.filter_button = customtkinter.CTkButton(self.filter_frame, text="2. Lọc & Lấy Chi tiết", command=self.start_filtering_thread, state="disabled"); self.filter_button.grid(row=0, column=4, padx=5, pady=10)
        self.import_button = customtkinter.CTkButton(self.filter_frame, text="Nhập TXT", width=100, command=self.import_from_txt); self.import_button.grid(row=0, column=5, padx=(10, 5), pady=10)
        self.load_button = customtkinter.CTkButton(self.filter_frame, text="Tải Phiên", width=100, command=self.load_session_from_json); self.load_button.grid(row=0, column=6, padx=5, pady=10)
        self.save_button = customtkinter.CTkButton(self.filter_frame, text="Lưu Phiên", width=100, command=self.save_session_to_json, state="disabled"); self.save_button.grid(row=0, column=7, padx=5, pady=10)
        self.status_label = customtkinter.CTkLabel(self.filter_frame, text="Sẵn sàng.", text_color="gray"); self.status_label.grid(row=0, column=8, padx=10, pady=10, sticky="w")
        
        self.result_frame = customtkinter.CTkFrame(self); self.result_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew") #...
        self.result_frame.grid_columnconfigure(0, weight=1); self.result_frame.grid_rowconfigure(0, weight=1)
        self._create_treeview()

        self.progress_frame = customtkinter.CTkFrame(self, fg_color="transparent") #...
        self.progress_frame.grid(row=3, column=0, padx=10, pady=(0,5), sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.realtime_status_label = customtkinter.CTkLabel(self.progress_frame, text="", text_color="gray"); self.realtime_status_label.grid(row=0, column=0, sticky="e")

        # --- KHUNG TẢI XUỐNG MỚI ---
        self.download_frame = customtkinter.CTkFrame(self)
        self.download_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        self.download_frame.grid_columnconfigure(1, weight=1)

        self.download_button = customtkinter.CTkButton(self.download_frame, text="3. Tải Video Đã Chọn", command=self.start_download_thread)
        self.download_button.grid(row=0, column=0, padx=10, pady=10)

        self.download_progress_label = customtkinter.CTkLabel(self.download_frame, text="")
        self.download_progress_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        self.download_progressbar = customtkinter.CTkProgressBar(self.download_frame, orientation="horizontal")
        self.download_progressbar.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        self.download_progressbar.set(0)

    def _create_treeview(self):
        self.tree = ttk.Treeview(self.result_frame, columns=('#', 'title', 'date', 'url'), show='headings')
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.tree.heading('#', text='STT')
        self.tree.heading('title', text='Tiêu đề')
        self.tree.heading('date', text='Ngày đăng')
        self.tree.heading('url', text='URL')

        self.tree.column('#', width=40, anchor='center', stretch=False)
        self.tree.column('title', width=400)
        self.tree.column('date', width=100, anchor='center')
        self.tree.column('url', width=300)

        v_scrollbar = customtkinter.CTkScrollbar(self.result_frame, command=self.tree.yview); v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar = customtkinter.CTkScrollbar(self.result_frame, command=self.tree.xview, orientation="horizontal"); h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    
    def _update_button_states(self, is_busy=False):
        # (Không đổi)
        state = "disabled" if is_busy else "normal"
        self.scrape_button.configure(state=state)
        self.import_button.configure(state=state)
        self.load_button.configure(state=state)
        self.filter_button.configure(state="normal" if not is_busy and self.scraped_links else "disabled")
        self.save_button.configure(state="normal" if not is_busy and self.video_details_list else "disabled")

    def start_scraping_thread(self):
        # (Không đổi)
        url = self.url_entry.get()
        if not url: return
        self._update_button_states(is_busy=True)
        self.tree.delete(*self.tree.get_children())
        self.scraped_links = []; self.video_details_list = []
        self.is_running_task = True
        def status_callback(message): self.after(0, self.update_status, message)
        thread = threading.Thread(target=scrape_video_urls, args=(url, 15, status_callback, self.url_queue))
        thread.start()
        self.after(100, self.process_scrape_queue)

    def process_scrape_queue(self):
        try:
            while not self.url_queue.empty():
                url = self.url_queue.get_nowait()
                if url is None: self.is_running_task = False; break
                
                standard_url = standardize_facebook_url(url)
                self.scraped_links.append({'url': standard_url})
                stt = len(self.scraped_links)
                self.tree.insert('', 'end', values=(stt, "Đang chờ lấy chi tiết...", "", standard_url))
                self.realtime_status_label.configure(text=f"Đã lấy được {stt} links...")
            
            if self.is_running_task: self.after(100, self.process_scrape_queue)
            else: self.update_ui_after_scraping()
        except queue.Empty:
            if self.is_running_task: self.after(100, self.process_scrape_queue)
            else: self.update_ui_after_scraping()
                
    def update_ui_after_scraping(self):
        # (Không đổi)
        self.update_status(f"Đã tìm thấy {len(self.scraped_links)} links. Sẵn sàng để lọc.")
        self._update_button_states(is_busy=False)
        if not self.scraped_links: self.update_status("Không tìm thấy link nào.")

    def start_filtering_thread(self, source_links=None):
        # (Không đổi)
        self._update_button_states(is_busy=True)
        self.tree.delete(*self.tree.get_children())
        self.video_details_list = []
        links_to_process = source_links if source_links is not None else self.scraped_links
        start_date = self.start_date_entry.get_date(); end_date = self.end_date_entry.get_date()
        thread = threading.Thread(target=self.filter_and_fetch_worker, args=(links_to_process, start_date, end_date))
        thread.start()

    def filter_and_fetch_worker(self, links_to_process, start_date, end_date):
        final_list = []; total_links = len(links_to_process); found_count = 0
        for i, link_info in enumerate(links_to_process):
            status_msg = f"Đang xử lý {i+1}/{total_links}... (Đã lọc được: {found_count})"
            self.after(0, self.update_status, status_msg)
            
            details = get_video_details_yt_dlp(link_info['url'])
            if not details or not details.get('upload_date'): continue
            
            try:
                video_date = datetime.strptime(details['upload_date'], "%Y%m%d").date()
                if (start_date and video_date < start_date) or \
                   (end_date and video_date > end_date): continue
                
                found_count += 1
                details['url'] = link_info['url']
                details['upload_date_str'] = video_date.strftime("%Y-%m-%d")
                final_list.append(details)
                
                self.after(0, self.add_item_to_tree, details, found_count)
            except (ValueError, TypeError): continue
        self.after(100, self.finalize_filtering, final_list)

        
    def add_item_to_tree(self, item, stt):
        self.tree.insert('', 'end', values=(stt, item['title'], item['upload_date_str'], item['url']))
        self.realtime_status_label.configure(text=f"Đã lọc được {stt} video")

    def finalize_filtering(self, final_list):
        self.video_details_list = sorted(final_list, key=lambda x: x.get('upload_date', '0'), reverse=True)
        self.tree.delete(*self.tree.get_children())
        for i, item in enumerate(self.video_details_list):
            self.tree.insert('', 'end', values=(i+1, item['title'], item['upload_date_str'], item['url']))
        
        self.update_status(f"Hoàn tất! Hiển thị {len(final_list)} video phù hợp.")
        self.realtime_status_label.configure(text="")
        self._update_button_states(is_busy=False)
        
    def save_session_to_json(self):
        # (Không đổi)
        if not self.video_details_list: return
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], title="Lưu phiên làm việc")
        if not filepath: return
        try:
            with open(filepath, 'w', encoding='utf-8') as f: json.dump(self.video_details_list, f, ensure_ascii=False, indent=4)
            self.update_status(f"Đã lưu thành công vào {filepath.split('/')[-1]}")
        except Exception as e: self.update_status(f"Lỗi: Không thể lưu file: {e}")

    def load_session_from_json(self):
        # (Không đổi)
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")], title="Tải phiên làm việc đã lưu")
        if not filepath: return
        try:
            with open(filepath, 'r', encoding='utf-8') as f: loaded_data = json.load(f)
            self.update_status(f"Đang tải {len(loaded_data)} video từ file...")
            self.scraped_links = [{'url': item['url']} for item in loaded_data]
            self.finalize_filtering(loaded_data)
        except Exception as e: self.update_status(f"Lỗi: Không thể đọc file JSON: {e}")

    def import_from_txt(self):
        # (Không đổi)
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")], title="Nhập danh sách URL từ file .txt")
        if not filepath: return
        links_from_file = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    url = line.strip()
                    if url.startswith("http"): links_from_file.append({'url': url})
            self.update_status(f"Đã tải {len(links_from_file)} links. Bắt đầu lấy chi tiết...")
            self.start_filtering_thread(source_links=links_from_file)
        except Exception as e: self.update_status(f"Lỗi: Không thể đọc file TXT: {e}")

    def update_status(self, message):
        # (Không đổi)
        self.status_label.configure(text=message)
        
    # hotfix - 2025-10-04 - Sửa lỗi index và thêm debug log cho chức năng tải video
    def start_download_thread(self):
        selected_items = self.tree.selection()
        if not selected_items:
            self.update_status("Lỗi: Vui lòng chọn ít nhất một video để tải.")
            return

        videos_to_download = []
        for item_id in selected_items:
            # Dữ liệu trên 1 dòng bao gồm: (STT, Tiêu đề, Ngày, URL)
            item_data = self.tree.item(item_id)['values']
            
            # SỬA LỖI: URL nằm ở index 3, không phải 2
            url_from_tree = item_data[3] 

            for video in self.video_details_list:
                if video['url'] == url_from_tree:
                    videos_to_download.append(video)
                    break
        
        if not videos_to_download:
            # THÊM DEBUG LOG
            self.update_status("Lỗi: Không tìm thấy dữ liệu chi tiết cho các video đã chọn.")
            logging.warning("Không thể khớp video được chọn trong Treeview với danh sách video_details_list.")
            return

        self._update_button_states(is_busy=True)
        page_url = self.url_entry.get()
        thread = threading.Thread(target=self.download_worker, args=(videos_to_download, page_url))
        thread.start()

    def download_worker(self, videos_to_download, page_url):
        def status_callback(message):
            self.after(0, self.update_status, message)
        
        def progress_callback(progress_str):
            try:
                # Chuyển đổi chuỗi % (ví dụ ' 25.4%') thành số float (0.254)
                progress_float = float(progress_str.replace('%','').strip()) / 100
                self.after(0, self.update_download_progress, progress_float)
            except (ValueError, TypeError):
                pass

        download_videos(videos_to_download, page_url, status_callback, progress_callback)
        
        # Báo hiệu hoàn tất
        self.after(0, self.finalize_download)

    def update_download_progress(self, value):
        self.download_progressbar.set(value)
        self.download_progress_label.configure(text=f"{value*100:.1f}%")

    def finalize_download(self):
        # (Cập nhật để dùng hàm quản lý trạng thái chung)
        self.update_status("Hoàn tất tất cả các lượt tải!")
        self._update_button_states(is_busy=False)