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

---
### **Quyết định Kiến trúc #2: Kiến trúc Lai và Thách thức Giao diện Đa luồng**

* **Bối cảnh:** Sau khi `yt-dlp` không thể tự lấy danh sách video từ các trang Facebook hiện đại (do "infinite scroll"), chúng ta buộc phải chuyển sang giải pháp kết hợp Selenium và `yt-dlp`. Quá trình này đã phát sinh nhiều vấn đề kỹ thuật phức tạp.

* **Kiến trúc Cuối cùng:**
    1.  **Lấy URL (Bước 1):** Dùng **Selenium** để điều khiển trình duyệt, mô phỏng thao tác cuộn trang. Giải pháp này vượt qua được "infinite scroll" và trả về một danh sách URL đã được sắp xếp tự nhiên (mới nhất -> cũ nhất).
    2.  **Lấy Chi tiết & Lọc (Bước 2):** Dùng **`yt-dlp`** để lấy thông tin chi tiết (tiêu đề, ngày đăng, caption...) cho từng URL. `yt-dlp` nhanh và hiệu quả hơn Selenium cho tác vụ này.
    3.  **Tải Video (Bước 3):** Tiếp tục dùng **`yt-dlp`** với các cấu hình mạnh mẽ để thực hiện việc tải file.

* **Bài học Kinh nghiệm & Các Vấn đề đã Giải quyết:**
    * **Mất thứ tự Sắp xếp:** Việc sử dụng `set` để loại bỏ trùng lặp đã phá hỏng thứ tự sắp xếp tự nhiên của Selenium. Đã được khắc phục bằng cách dùng một `list` (để giữ thứ tự) và một `set` (chỉ để kiểm tra).
    * **Hiệu năng Real-time:** Thuật toán "chèn có sắp xếp" (`O(N^2)`) gây ra hiện tượng chậm và giật lag. Đã được khắc phục bằng cách quay về thuật toán "chèn vào cuối" (`O(N)`) dựa trên danh sách nguồn đã được sắp xếp sẵn.
    * **Lỗi Giao diện Bị treo ("Ảo giác"):** Nguyên nhân sâu xa là do luồng nền gửi quá nhiều yêu cầu cập nhật (`self.after`) trong một thời gian ngắn, làm "ngập lụt" và chặn vòng lặp sự kiện của giao diện. Đã được khắc phục bằng cách thêm cơ chế "giảm tải" (throttling), chỉ cập nhật trạng thái sau mỗi 5-10 items.

    ---
### **Quyết định Kiến trúc #3: Tự động hóa Quản lý Trình duyệt & Tối ưu Hiệu năng**

* **Bối cảnh:** Quá trình chuẩn bị đóng gói đã bộc lộ hai điểm yếu lớn của kiến trúc ban đầu: sự phụ thuộc vào `chromedriver.exe` thủ công và hiệu năng chậm của quá trình lọc video.

* **Quyết định:**
    1.  **Tích hợp `webdriver-manager`:** Thay thế hoàn toàn cơ chế gọi `chromedriver.exe` tĩnh. Thư viện này sẽ tự động phát hiện phiên bản Chrome, tải về và cache trình điều khiển tương thích. Điều này giúp loại bỏ một bước cài đặt thủ công cho người dùng cuối và giải quyết vấn đề lỗi phiên bản trong tương lai.
    2.  **Triển khai Đa luồng cho Tác vụ Lọc:** Tái cấu trúc lại luồng xử lý của "Bước 2". Thay vì gọi `yt-dlp` tuần tự cho mỗi URL, ứng dụng giờ đây sử dụng một `ThreadPoolExecutor` để tạo ra một nhóm các "worker" chạy song song. Mỗi worker sẽ xử lý một URL, giúp giảm đáng kể tổng thời gian chờ đợi của người dùng. Một tùy chọn đơn luồng vẫn được giữ lại để đảm bảo tính tương thích.

* **Bài học Kinh nghiệm:**
    * **Độ tin cậy của Đường dẫn:** Việc sử dụng đường dẫn tương đối (`'chromedriver.exe'`) đã được chứng minh là không đủ tin cậy cho một ứng dụng đóng gói. Việc chuyển sang kiến trúc đường dẫn tuyệt đối, được quản lý bởi `src/core/app_path.py`, là một bước đi cần thiết.
    * **Cân bằng UX và Hiệu năng:** Giải pháp "Logic Vàng" (thu thập tất cả, hiển thị một lần) tuy tối ưu về mặt thuật toán nhưng lại tạo ra trải nghiệm người dùng tệ. Giải pháp cuối cùng kết hợp cả hai: hiển thị real-time (để người dùng có phản hồi) và chỉ sắp xếp lại một lần duy nhất ở cuối (để đảm bảo hiệu năng).