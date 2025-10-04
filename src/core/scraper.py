# file-path: src/core/scraper.py
# version: 3.3
# last-updated: 2025-10-04
# description: Siết chặt bộ lọc URL để sửa lỗi Unsupported URL và tích hợp queue cho real-time UI.

import logging
import re
import time
import json
import traceback
import yt_dlp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def standardize_facebook_url(url: str) -> str:
    if not url: return url
    match = re.search(r"/(?:videos|reel)/(\d+)", url)
    if match:
        video_id = match.group(1)
        return f"https://www.facebook.com/watch/?v={video_id}"
    return url

def get_video_details_yt_dlp(video_url: str) -> dict:
    ydl_opts = {
        'quiet': True,
        'ignoreerrors': True,
        'cookiefile': 'facebook_cookies.txt',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return {
                'title': info.get('title', 'Không có tiêu đề'),
                'upload_date': info.get('upload_date'),
            }
    except Exception:
        return {'title': 'Lỗi khi lấy chi tiết', 'upload_date': None}

def scrape_video_urls(page_url: str, scroll_count: int, status_callback, queue):
    status_callback("Khởi tạo trình duyệt...")
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    found_urls = set()

    try:
        driver.get("https://www.facebook.com")
        status_callback("Đang tải cookie (JSON)...")
        time.sleep(1)
        with open('facebook_cookies.json', 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        for cookie in cookies:
            if 'sameSite' in cookie and cookie['sameSite'] not in ["Strict", "Lax", "None"]:
                del cookie['sameSite']
            driver.add_cookie(cookie)
        
        driver.get(page_url)
        time.sleep(3)

        for i in range(scroll_count):
            status_callback(f"Đang cuộn trang... ({i+1}/{scroll_count})")
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(2)

        anchor_tags = driver.find_elements(By.TAG_NAME, 'a')
        for tag in anchor_tags:
            href = tag.get_attribute('href')
            # --- BỘ LỌC MỚI (SỬA LỖI UNSUPPORTED URL) ---
            # Chỉ chấp nhận link có dạng /videos/ID hoặc /reel/ID
            if href and re.search(r"/(?:videos|reel)/\d+", href):
                clean_href = href.split('?')[0]
                if clean_href not in found_urls:
                    found_urls.add(clean_href)
                    # Gửi URL về giao diện ngay lập tức qua queue
                    queue.put(clean_href)

    except Exception:
        logging.error(traceback.format_exc())
    finally:
        driver.quit()
    
    # Báo hiệu cho giao diện biết luồng đã kết thúc
    queue.put(None)