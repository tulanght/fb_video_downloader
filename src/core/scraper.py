# file-path: src/core/scraper.py
# version: 2.3
# last-updated: 2025-10-03
# description: Thêm chức năng lấy title/thumbnail cho từng video bằng yt-dlp.

import logging
import re
import time
import json
import traceback
import yt_dlp # Thêm vào đây để dùng trong hàm mới
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

def get_video_details(video_url: str) -> dict:
    """
    Sử dụng yt-dlp để lấy thông tin chi tiết (title, thumbnail) từ một URL video duy nhất.
    """
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
                'thumbnail': info.get('thumbnail'),
            }
    except Exception:
        logging.warning(f"Không thể lấy chi tiết cho URL: {video_url}")
        return {
            'title': 'Lỗi khi lấy tiêu đề',
            'thumbnail': None,
        }

def get_videos_from_page(page_url: str, scroll_count: int = 10, downloader_tab_ref=None) -> list:
    """
    Quy trình đầy đủ: Dùng Selenium lấy links -> Dùng yt-dlp lấy chi tiết.
    """
    logging.info("Khởi tạo trình duyệt Chrome...")
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")
    
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    video_links = set()

    try:
        driver.get("https://www.facebook.com")
        logging.info("Đã mở facebook.com. Đang tải cookie từ file...")
        time.sleep(2)
        with open('facebook_cookies.txt', 'r') as f:
            cookies = json.load(f)
        for cookie in cookies:
            if 'sameSite' in cookie and cookie['sameSite'] not in ["Strict", "Lax", "None"]:
                del cookie['sameSite']
            driver.add_cookie(cookie)
        logging.info("Đã tải cookie thành công.")
        time.sleep(2)
        driver.get(page_url)
        logging.info(f"Đang truy cập URL mục tiêu: {page_url}")
        time.sleep(3)
        logging.info(f"Bắt đầu cuộn trang {scroll_count} lần...")
        body = driver.find_element(By.TAG_NAME, 'body')
        for i in range(scroll_count):
            body.send_keys(Keys.END)
            logging.info(f"  -> Đã cuộn lần {i+1}/{scroll_count}")
            time.sleep(2)
        
        logging.info("Đã cuộn xong. Bắt đầu thu thập links...")
        anchor_tags = driver.find_elements(By.TAG_NAME, 'a')
        for tag in anchor_tags:
            href = tag.get_attribute('href')
            if href and ("/videos/" in href or "/reel/" in href):
                clean_href = href.split('?')[0]
                video_links.add(clean_href)

    except Exception:
        logging.error("Đã xảy ra lỗi trong quá trình điều khiển Selenium:")
        logging.error(traceback.format_exc())
    finally:
        logging.info("Đóng trình duyệt.")
        driver.quit()

    if not video_links:
        logging.warning("Không thu thập được link nào.")
        return []

    logging.info(f"Tìm thấy {len(video_links)} link duy nhất. Bắt đầu lấy thông tin chi tiết...")
    
    # Giai đoạn 2: Dùng yt-dlp để lấy chi tiết cho từng link
    final_video_list = []
    total_videos = len(video_links)
    for i, link in enumerate(video_links):
        if downloader_tab_ref:
            # Gửi tín hiệu cập nhật trạng thái về cho giao diện
            status_message = f"Đang lấy chi tiết video {i+1}/{total_videos}..."
            downloader_tab_ref.after(0, downloader_tab_ref.update_status, status_message)

        standard_url = standardize_facebook_url(link)
        details = get_video_details(standard_url)
        
        video_info = {
            'url': standard_url,
            'title': details['title'],
            'thumbnail': details['thumbnail'],
        }
        final_video_list.append(video_info)
        
    return final_video_list