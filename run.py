# file-path: run.py
# version: 1.4
# last-updated: 2025-10-03
# description: Đơn giản hóa kịch bản kiểm thử cho phương án dùng file cookie.

from src.core.scraper import get_videos_from_page

def test_scraper():
    """Hàm để kiểm thử chức năng lấy link video bằng Selenium và file cookie."""
    test_url = "https://www.facebook.com/KenhPhuNuPhamNgoc/reels/"

    print(f"--- Bắt đầu kiểm thử Selenium với URL: {test_url} ---")
    
    # Tăng số lần cuộn để lấy được nhiều video hơn
    videos = get_videos_from_page(test_url, scroll_count=15) 

    if videos:
        print(f"\n>>> Tìm thấy và xử lý thành công: {len(videos)} links.")
        print("--- Danh sách link đã thu thập và chuẩn hóa ---")
        for i, video in enumerate(videos):
            print(f"  {i+1}. {video['url']}")
    else:
        print("\n>>> Không lấy được link video nào. Vui lòng kiểm tra lại file 'facebook_cookies.txt'.")

    print("\n--- Kiểm thử kết thúc ---")

if __name__ == "__main__":
    test_scraper()