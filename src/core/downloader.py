# file-path: src/core/downloader.py
# version: 2.1
# last-updated: 2025-10-05
# description: Logic tải xuống hoàn chỉnh, thông minh và linh hoạt.

import logging
import os
import re
import yt_dlp
import datetime
from src.core.app_path import get_app_base_path
from src.core.subtitle_converter import convert_srt_to_clean_txt
from src.core.scraper import get_video_details_yt_dlp

def download_video_session(video_list: list, status_callback, progress_callback):
    if not video_list:
        status_callback("Lỗi: Không có video nào trong danh sách để tải.")
        return

    # --- Lấy Tên Page một cách thông minh ---
    status_callback("Đang xác định tên Page...")
    first_video_details = get_video_details_yt_dlp(video_list[0]['url'])
    page_name = first_video_details.get('uploader')
    if not page_name:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        page_name = f"unknown_page_{timestamp}"
        logging.warning(f"Không xác định được tên page, sử dụng tên fallback: {page_name}")
    
    base_path = get_app_base_path()
    download_dir = os.path.join(base_path, 'downloads', page_name)
    os.makedirs(download_dir, exist_ok=True)
    logging.info(f"Các file sẽ được lưu tại: {download_dir}")

    total_videos = len(video_list)
    for i, video in enumerate(video_list):
        current_video_title = video.get('title', video.get('id', 'video_khong_tieu_de'))
        status_callback(f"Bắt đầu tải video {i+1}/{total_videos}: {current_video_title[:40]}...")
        progress_callback("0.0%") # Reset progress bar

        def progress_hook(d):
            if d['status'] == 'downloading':
                percent_str = re.sub(r'\x1b\[[0-9;]*m', '', d.get('_percent_str', '0.0%')).strip()
                progress_callback(percent_str)
            elif d['status'] == 'finished':
                progress_callback("100.0%")

        stt = video.get('stt', i + 1)
        ydl_opts = {
            'cookiefile': 'facebook_cookies.txt',
            'outtmpl': os.path.join(download_dir, f'{stt:03d} - %(title)s [%(id)s].%(ext)s'),
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'writethumbnail': True,
            'writeautomaticsub': True,
            'subformat': 'srt',
            'progress_hooks': [progress_hook],
            'quiet': True,
            'ignoreerrors': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video['url'], download=True)
                if info is None: raise Exception("Không thể lấy thông tin video.")

                filename = ydl.prepare_filename(info)
                base_filename, _ = os.path.splitext(filename)
                
                # Tìm file srt với các hậu tố ngôn ngữ có thể có
                subtitle_path = None
                for lang_code in ['en', 'vi', '']: # Thêm các mã ngôn ngữ khác nếu cần
                    potential_srt_path = f"{base_filename}.{lang_code}.srt" if lang_code else f"{base_filename}.srt"
                    if os.path.exists(potential_srt_path):
                        subtitle_path = convert_srt_to_clean_txt(potential_srt_path)
                        break
                
                yield {'url': video['url'], 'status': 'success', 'subtitle_path': subtitle_path}
        except Exception as e:
            logging.error(f"Lỗi khi tải video {video['url']}: {e}")
            yield {'url': video['url'], 'status': 'fail'}