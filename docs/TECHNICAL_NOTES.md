# Ghi chú Kỹ thuật - FB Page Video Downloader
# Last Updated: 2025-10-02

Tài liệu này ghi lại những quyết định kiến trúc quan trọng, các vấn đề kỹ thuật hóc búa đã gặp phải, và các rủi ro đã được lường trước trong quá trình phát triển.

---
### **Quyết định Kiến trúc #1: Lựa chọn và Rủi ro của phương pháp Lấy dữ liệu (Scraping)**

* **Bối cảnh:** Chức năng cốt lõi của ứng dụng là lấy được thông tin video từ một Facebook Page. Đây là một nền tảng đóng và không cung cấp API công khai dễ dàng cho mục đích này.

* **Quyết định:**
    1.  **Phương án chính:** Sử dụng thư viện **`yt-dlp`**. Đây là một công cụ mạnh mẽ, được cộng đồng bảo trì tích cực, có khả năng phân tích cấu trúc trang của nhiều website (bao gồm Facebook) để trích xuất link media và metadata.
    2.  **Phương án dự phòng:** Sử dụng **`Selenium`**. Trong trường hợp `yt-dlp` thất bại hoặc không lấy được đủ thông tin do Facebook thay đổi, `Selenium` có thể được dùng để giả lập một trình duyệt web, cuộn trang và tự phân tích mã HTML.

* **Phân tích Rủi ro (Rất quan trọng):**
    * **Mức độ Rủi ro:** **CAO**. Toàn bộ ứng dụng phụ thuộc vào khả năng lấy dữ liệu từ một nền tảng của bên thứ ba không có sự cho phép chính thức qua API.
    * **Bản chất Rủi ro:** Facebook thường xuyên cập nhật giao diện và cấu trúc mã nguồn để cải thiện trải nghiệm người dùng và chống lại việc lấy dữ liệu tự động. Bất kỳ thay đổi nào, dù là nhỏ nhất, cũng có khả năng **làm hỏng hoàn toàn** chức năng lấy dữ liệu của `yt-dlp` hoặc `Selenium`.
    * **Hệ quả:** Ứng dụng có thể **ngừng hoạt động bất cứ lúc nào** mà không có cảnh báo trước. Việc sửa chữa sẽ đòi hỏi phải cập nhật `yt-dlp` (nếu cộng đồng đã có bản vá) hoặc viết lại hoàn toàn logic scraping (nếu dùng `Selenium`).

* **Kết luận:** Chấp nhận rủi ro này và ưu tiên xây dựng cấu trúc module linh hoạt (`scraper.py`) để có thể dễ dàng cập nhật hoặc thay thế phương pháp lấy dữ liệu trong tương lai.