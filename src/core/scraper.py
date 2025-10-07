# file-path: src/core/scraper.py
# version: 6.1 (Stable & Ordered)
# last-updated: 2025-10-06
# description: Sửa lỗi dùng set làm mất thứ tự, đảm bảo list URL trả về luôn được sắp xếp.

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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def standardize_facebook_url(url: str) -> str:
    if not url: return url
    match = re.search(r"/(?:videos|reel)/(\d+)", url)
    if match:
        video_id = match.group(1)
        return f"https://www.facebook.com/watch/?v={video_id}"
    return url

# file-path: src/core/scraper.py
# (Chỉ cập nhật hàm get_video_details_yt_dlp, các hàm khác không đổi)

def get_video_details_yt_dlp(video_url: str) -> dict:
    """
    Sử dụng yt-dlp để lấy thông tin chi tiết (bao gồm cả description) từ một URL.
    """
    ydl_opts = {'quiet': True, 'ignoreerrors': True, 'cookiefile': 'facebook_cookies.txt'}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return {
                'id': info.get('id'),
                'title': info.get('title', 'Không có tiêu đề'),
                'description': info.get('description'), # Đảm bảo lấy description
                'thumbnail': info.get('thumbnail'),
                'upload_date': info.get('upload_date'),
                'uploader': info.get('uploader'),
            }
    except Exception:
        logging.error(f"Lỗi khi dùng yt-dlp lấy chi tiết cho: {video_url}")
        logging.error(traceback.format_exc())
        return {'title': 'Lỗi khi lấy chi tiết', 'upload_date': None, 'description': None, 'id': None, 'thumbnail': None, 'uploader': None}

def scrape_video_urls(page_url: str, scroll_count: int, status_callback):
    """Sử dụng Selenium để cuộn trang và trả về một danh sách URL đã giữ nguyên thứ tự."""
    status_callback("Khởi tạo trình duyệt...")
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    ordered_video_links = []
    seen_urls = set()

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
            if href and re.search(r"/(?:videos|reel)/\d+", href):
                clean_href = href.split('?')[0]
                if clean_href not in seen_urls:
                    seen_urls.add(clean_href)
                    ordered_video_links.append(clean_href)

    except Exception:
        logging.error(traceback.format_exc())
    finally:
        status_callback("Đóng trình duyệt...")
        driver.quit()

    if not ordered_video_links:
        return []
    
    return [{'url': standardize_facebook_url(link)} for link in ordered_video_links]