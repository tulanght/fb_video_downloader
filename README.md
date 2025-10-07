# FB Page Video Downloader v0.4.0

Một công cụ desktop mạnh mẽ được xây dựng bằng Python, giúp tự động hóa việc tải toàn bộ video từ một trang Facebook (Facebook Page) một cách hiệu quả và có tổ chức.

## Tính năng Chính
- **Nhập URL Page:** Chỉ cần dán URL của một Facebook Page để bắt đầu.
- **Lấy Dữ liệu Toàn diện:** Tự động lấy danh sách tất cả video công khai, kèm theo thumbnail và ngày đăng.
- **Xem trước & Tùy chỉnh:** Hiển thị danh sách video sắp tải một cách trực quan, cho phép người dùng loại bỏ những video không cần thiết.
- **Tải về Hàng loạt:** Tải hàng loạt video và thumbnail tương ứng về máy tính.
- **Tự động Tổ chức:** Tự động đặt tên và đánh số thứ tự cho các file được tải về (`video_01.mp4`, `video_01.jpg`...).
- **Lưu trữ Lịch sử:** Ghi lại lịch sử các video đã tải vào một cơ sở dữ liệu SQLite cục bộ để dễ dàng tra cứu.
- **Trích xuất Dữ liệu:** Cho phép xuất thông tin từ lịch sử tải ra các định dạng file phổ biến.

## Công nghệ Sử dụng
- **Ngôn ngữ:** Python 3.9+
- **Giao diện Người dùng (GUI):** CustomTkinter
- **Lấy dữ liệu Video:** yt-dlp
- **Cơ sở dữ liệu:** SQLite

## Hướng dẫn Cài đặt (Dành cho Lập trình viên)
1.  **Clone repository:**
    ```bash
    git clone [URL-repository-cua-ban]
    cd fb_video_downloader
    ```
2.  **Kích hoạt Môi trường ảo:**
    (File `setup_project.bat` đã tạo sẵn môi trường `venv`)
    ```bash
    .\venv\Scripts\activate
    ```
3.  **Cài đặt các Thư viện:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Lưu ý: File requirements.txt sẽ được cập nhật trong quá trình phát triển)*

4.  **Chạy Ứng dụng:**
    ```bash
    python run.py
    ```