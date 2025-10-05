# file-path: src/core/scraper.py
# version: 6.0 (Stable)
# last-updated: 2025-10-05
# description: Phiên bản ổn định, trả về danh sách trực tiếp, không dùng queue.

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

def get_video_details_yt_dlp(video_url: str) -> dict:
    ydl_opts = {'quiet': True, 'ignoreerrors': True, 'cookiefile': 'facebook_cookies.txt'}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return {'id': info.get('id'), 'title': info.get('title', 'N/A'), 'description': info.get('description'),
                    'thumbnail': info.get('thumbnail'), 'upload_date': info.get('upload_date'), 'uploader': info.get('uploader')}
    except Exception:
        return {'title': 'Lỗi', 'upload_date': None, 'description': None, 'id': None, 'thumbnail': None, 'uploader': None}

def scrape_video_urls(page_url: str, scroll_count: int, status_callback):
    """Sử dụng Selenium để cuộn trang và trả về một danh sách các URL video thô."""
    status_callback("Khởi tạo trình duyệt...")
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    video_links = set()
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
                video_links.add(clean_href)
    except Exception:
        logging.error(traceback.format_exc())
    finally:
        status_callback("Đóng trình duyệt...")
        driver.quit()

    if not video_links:
        return []
    
    return [{'url': standardize_facebook_url(link)} for link in video_links]