# file-path: src/core/scraper.py
# version: 2.3
# last-updated: 2025-10-03
# description: Thêm module traceback để ghi lại log lỗi chi tiết hơn.

import logging
import re
import time
import json
import traceback # <-- THÊM MỚI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# (Hàm standardize_facebook_url không thay đổi)
def standardize_facebook_url(url: str) -> str:
    if not url: return url
    match = re.search(r"/(?:videos|reel)/(\d+)", url)
    if match:
        video_id = match.group(1)
        return f"https://www.facebook.com/watch/?v={video_id}"
    return url

# hotfix - 2025-10-03 - Thêm logic làm sạch cookie để xử lý lỗi 'sameSite' AssertionError.
def get_videos_from_page(page_url: str, scroll_count: int = 10) -> list:
    """
    Sử dụng Selenium, tải cookie từ file để lấy link video/reels.
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

        try:
            with open('facebook_cookies.txt', 'r') as f:
                cookies = json.load(f)
            
            for cookie in cookies:
                # --- LOGIC LÀM SẠCH COOKIE ---
                # Một số cookie có thể có giá trị 'sameSite' không hợp lệ
                if 'sameSite' in cookie and cookie['sameSite'] not in ["Strict", "Lax", "None"]:
                    # Nếu giá trị không hợp lệ, xóa key này đi
                    del cookie['sameSite']
                
                # Chỉ thêm cookie sau khi đã được làm sạch
                driver.add_cookie(cookie)

            logging.info("Đã tải cookie thành công.")
        except FileNotFoundError:
            logging.error("LỖI: Không tìm thấy file 'facebook_cookies.txt'.")
            driver.quit()
            return []
        
        time.sleep(2)

        logging.info(f"Đang truy cập URL mục tiêu: {page_url}")
        driver.get(page_url)
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
        logging.error("Đã xảy ra lỗi không mong muốn. Chi tiết lỗi như sau:")
        logging.error(traceback.format_exc())
    finally:
        logging.info("Đóng trình duyệt.")
        driver.quit()

    if not video_links:
        logging.warning("Không thu thập được link nào.")
        return []

    logging.info(f"Tìm thấy {len(video_links)} link duy nhất. Bắt đầu chuẩn hóa...")
    
    standardized_list = [{'url': standardize_facebook_url(link), 'title': '', 'thumbnail': '', 'upload_date': ''} for link in video_links]
        
    return standardized_list