# Lộ trình Phát triển (Roadmap) - FB Page Video Downloader
# version: 1.0
# last-updated: 2025-10-02

## Tầm nhìn Dự án
Trở thành một công cụ desktop đáng tin cậy, dễ sử dụng, giúp người dùng nhanh chóng lưu trữ và quản lý kho video từ các trang Facebook.

---
## Giai đoạn 1: Xây dựng Lõi Chức năng (Core Engine)
Mục tiêu: Xây dựng và kiểm thử các chức năng nền tảng mà không cần giao diện đồ họa.

- [ ] Tích hợp `yt-dlp` để lấy danh sách URL video, thumbnail, ngày đăng từ một Facebook Page.
- [ ] Xây dựng module `downloader.py` để tải video và thumbnail từ URL.
- [ ] Xây dựng logic tự động đặt tên và đánh số file.
- [ ] Tạo một phiên bản kịch bản dòng lệnh (`CLI`) đơn giản để kiểm thử toàn bộ luồng hoạt động.

## Giai đoạn 2: Giao diện Người dùng (GUI)
Mục tiêu: Xây dựng một giao diện trực quan để người dùng tương tác với các chức năng cốt lõi.

- [ ] Tích hợp thư viện `CustomTkinter` làm nền tảng GUI.
- [ ] Xây dựng giao diện Tab "Tải Video" (`downloader_tab.py`) với các thành phần: ô nhập URL, danh sách video (dạng cây hoặc bảng), các nút chức năng.
- [ ] Liên kết các sự kiện trên giao diện (nhấn nút, chọn video) với các hàm logic ở `core`.
- [ ] Thêm thanh tiến trình và khu vực hiển thị log/trạng thái.

## Giai đoạn 3: Tích hợp Cơ sở dữ liệu
Mục tiêu: Thêm khả năng lưu trữ và tra cứu lịch sử làm việc.

- [ ] Thiết kế cấu trúc bảng trong `SQLite` để lưu thông tin video đã tải.
- [ ] Xây dựng module `database.py` với các hàm CRUD (Create, Read, Update, Delete).
- [ ] Xây dựng giao diện Tab "Lịch sử" (`history_tab.py`) để hiển thị dữ liệu từ CSDL.
- [ ] Thêm chức năng tìm kiếm/lọc và trích xuất dữ liệu ra file CSV.

## Giai đoạn 4: Hoàn thiện & Đóng gói
Mục tiêu: Tối ưu hóa ứng dụng và tạo phiên bản phát hành cho người dùng cuối.

- [ ] Xây dựng Tab "Cài đặt" (`settings_tab.py`) cho phép người dùng chọn thư mục lưu file.
- [ ] Tối ưu hóa hiệu năng, đặc biệt với các trang có số lượng video lớn.
- [ ] Xử lý các trường hợp lỗi (mất mạng, URL không hợp lệ, video riêng tư...).
- [ ] Đóng gói ứng dụng thành file `.exe` bằng `PyInstaller`.