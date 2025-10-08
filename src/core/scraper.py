# file-path: src/core/scraper.py
# version: 22.0 (Add Scroll Delay)
# last-updated: 2025-10-08
# description: Thêm tham số scroll_delay để người dùng có thể tùy chỉnh thời gian chờ giữa các lần cuộn.

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
            if not info or 'upload_date' not in info:
                return None
            return info
    except Exception:
        return None

# === THAY ĐỔI: Thêm scroll_delay vào chữ ký hàm ===
def scrape_video_urls(page_url, scroll_count, status_callback, stop_requested, scroll_delay):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    service = Service(executable_path="chromedriver.exe")
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
            if stop_requested.is_set():
                status_callback("Đã dừng theo yêu cầu.")
                break
            status_callback(f"Đang cuộn trang... ({i+1}/{scroll_count})")
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            # === THAY ĐỔI: Sử dụng giá trị scroll_delay từ người dùng ===
            time.sleep(scroll_delay)

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
        driver.quit()
        return ordered_video_links