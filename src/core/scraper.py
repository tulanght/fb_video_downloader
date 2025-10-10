# file-path: src/core/scraper.py
# version: 22.0 (Auto-update Chromedriver)
# last-updated: 2025-10-08
# description: Tích hợp webdriver-manager để tự động tải và quản lý chromedriver.

import logging, os
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
from src.core.app_path import get_app_base_path
from src import config
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def standardize_facebook_url(url: str) -> str:
    if not url: return url
    match = re.search(r"/(?:videos|reel)/(\d+)", url)
    if match:
        video_id = match.group(1)
        return f"https://www.facebook.com/watch/?v={video_id}"
    return url

def get_video_details_yt_dlp(video_url: str) -> dict:
    cookie_file = os.path.join(get_app_base_path(), config.COOKIE_TXT_FILE)
    ydl_opts = {'quiet': True, 'ignoreerrors': True, 'cookiefile': cookie_file}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            if not info or 'upload_date' not in info:
                return None
            return info
    except Exception:
        return None

def scrape_video_urls(page_url, scroll_count, status_callback, stop_requested, scroll_delay):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    chromedriver_path = os.path.join(get_app_base_path(), config.CHROMEDRIVER_FILE)
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    ordered_video_links = []
    seen_urls = set()

    try:
        driver.get("https://www.facebook.com")
        status_callback("Đang tải cookie (JSON)...")
        time.sleep(1)
        
        json_cookie_path = os.path.join(get_app_base_path(), config.COOKIE_JSON_FILE)
        with open(json_cookie_path, 'r', encoding='utf-8') as f:
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
            time.sleep(scroll_delay)

        status_callback("Đang thu thập các link video...")
        anchor_tags = driver.find_elements(By.TAG_NAME, 'a')
        
        for tag in anchor_tags:
            href = tag.get_attribute('href')
            if href:
                if re.search(r"/(?:videos|reel)/\d+", href):
                    clean_href = href.split('?')[0]
                    if clean_href not in seen_urls:
                        seen_urls.add(clean_href)
                        ordered_video_links.append(clean_href)

    except Exception:
        logging.error(traceback.format_exc())
    finally:
        if driver:
            driver.quit()
        return ordered_video_links