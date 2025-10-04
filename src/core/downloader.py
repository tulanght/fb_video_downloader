# file-path: src/core/downloader.py
# version: 1.0
# last-updated: 2025-10-04
# description: Chứa logic tải video sử dụng yt-dlp, hỗ trợ progress hook và tạo thư mục con.

import logging
import os
import re
import yt_dlp
from src.core.app_path import get_app_base_path

def _extract_page_name(url: str) -> str:
    """Trích xuất tên page từ URL để làm tên thư mục."""
    match = re.search(r"facebook\.com/([^/]+)", url)
    if match:
        return match.group(1)
    return "unknown_page"

def download_videos(video_list: list, page_url: str, status_callback, progress_callback):
    if not video_list:
        return

    base_path = get_app_base_path()
    page_name = _extract_page_name(page_url)
    download_dir = os.path.join(base_path, 'downloads', page_name)

    os.makedirs(download_dir, exist_ok=True)
    logging.info(f"Các video sẽ được lưu tại: {download_dir}")

    total_videos = len(video_list)
    for i, video in enumerate(video_list):
        current_video_title = video.get('title', video.get('id', 'video'))
        status_callback(f"Bắt đầu tải video {i+1}/{total_videos}: {current_video_title[:50]}...")

        # --- Progress Hook ---
        def progress_hook(d):
            if d['status'] == 'downloading':
                # Loại bỏ các ký tự ANSI color code
                percent_str = re.sub(r'\x1b\[[0-9;]*m', '', d['_percent_str']).strip()
                progress_callback(percent_str)
            elif d['status'] == 'finished':
                progress_callback("100.0%")

        # --- Cấu hình yt-dlp ---
        ydl_opts = {
            'cookiefile': 'facebook_cookies.txt',
            'outtmpl': os.path.join(download_dir, '%(title)s [%(id)s].%(ext)s'),
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'progress_hooks': [progress_hook],
            'quiet': True,
            'ignoreerrors': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video['url']])
            status_callback(f"Hoàn tất tải video {i+1}/{total_videos}.")
        except Exception as e:
            logging.error(f"Lỗi khi tải video {video['url']}: {e}")
            status_callback(f"Lỗi khi tải video {i+1}/{total_videos}.")