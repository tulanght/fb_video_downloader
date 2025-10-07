# Lịch sử thay đổi (Changelog)

## [0.4.0] - 2025-10-07
### ✨ Tính năng mới (Features)
- **Tích hợp Luồng Tải Video:** Triển khai chức năng tải video, thumbnail từ `yt-dlp`.
- **Tổ chức File Tải về:** Tự động tạo thư mục con theo Tên Page và đánh số thứ tự cho file video, thumbnail.
- **Xem Caption:** Cho phép xem đầy đủ caption của video bằng cách nhấp đúp chuột vào một dòng trong bảng kết quả.
- **Xử lý Tên Page Thông minh:** Tự động tìm tên Page chính xác khi tải từ file JSON/TXT để tạo thư mục, với cơ chế fallback an toàn.
- **Hỗ trợ Phụ đề (Nền tảng):** Xây dựng module `subtitle_converter.py` với logic làm sạch và chuyển đổi phụ đề từ `.srt` sang `.txt`.

### ♻️ Thay đổi & Tối ưu hóa (Changed & Optimized)
- **Tối ưu Hiệu năng Lọc:** Thay thế thuật toán sắp xếp real-time `O(N^2)` bằng thuật toán "Logic Vàng" `O(N)`, giúp quá trình lọc và hiển thị nhanh và mượt mà hơn đáng kể.
- **Kiến trúc Xử lý Luồng:** Tái cấu trúc và ổn định hóa hoàn toàn kiến trúc đa luồng, loại bỏ các lỗi "đứng im", "ảo giác" và `RuntimeError` khi đóng ứng dụng.
- **Nâng cấp Script Phát hành:** Cải tiến `release.py` để tương thích với cấu trúc dự án mới và hoạt động ổn định hơn.

### 🐛 Sửa lỗi (Fixed)
- Sửa lỗi nghiêm trọng khiến danh sách URL từ Selenium bị mất thứ tự sắp xếp ban đầu.

## [0.3.0] - 2025-10-04

### ✨ Tính năng mới (Features)
- **Xây dựng Giao diện Người dùng (GUI):** Xây dựng cửa sổ ứng dụng chính và Tab "Tải Video" bằng CustomTkinter.
- **Tích hợp Scraper Động:** Tích hợp Selenium để điều khiển trình duyệt, xử lý "infinite scroll" và lấy danh sách URL từ các trang Facebook Videos/Reels.
- **Xử lý Xác thực:** Triển khai giải pháp sử dụng file cookie (JSON) để Selenium có thể hoạt động với các trang yêu cầu đăng nhập.
- **Lấy Thông tin Chi tiết:** Tích hợp `yt-dlp` để lấy Tiêu đề và Ngày đăng cho từng video một cách nhanh chóng, sử dụng file cookie (Netscape).
- **Bộ lọc Ngày tháng:** Thêm bộ lọc theo khoảng ngày tháng với giao diện lịch chọn ngày (`tkcalendar`).
- **Hiển thị Dữ liệu Nâng cao:** Nâng cấp danh sách kết quả sang dạng bảng (`ttk.Treeview`) với các cột STT, Tiêu đề, Ngày đăng, URL và thanh cuộn.
- **Lưu & Tải Phiên làm việc:** Thêm chức năng lưu kết quả đã lọc ra file JSON và tải lại tức thì.
- **Nhập từ File TXT:** Thêm chức năng nhập danh sách link thô từ file `.txt` để xử lý.
- **Module Log Thông minh:** Xây dựng module log tích hợp vào giao diện, tự động hiển thị các bước hoạt động của chương trình.
- **Cập nhật Giao diện Real-time:** Giao diện được cập nhật "sống", hiển thị kết quả ngay khi được tìm thấy ở cả hai bước lấy link và lọc.

### 🐛 Sửa lỗi (Bug Fixes)
- Xử lý hàng loạt lỗi liên quan đến việc lấy dữ liệu từ Facebook (`Unsupported URL`, lỗi cookie `DPAPI`, `sameSite`).
- Sửa lỗi logic `off-by-one` khi chọn video để tải.
- Sửa nhiều lỗi về quản lý trạng thái nút bấm trên giao diện.
- Sửa các lỗi `AttributeError` và thiếu `import` do Pylint phát hiện.

### ♻️ Tái cấu trúc (Refactoring)
- Tái cấu trúc kiến trúc thành mô hình lai (Hybrid): Selenium chuyên lấy link, `yt-dlp` chuyên lấy chi tiết, giải quyết xung đột định dạng cookie.
- Tái cấu trúc logic quản lý trạng thái các nút bấm trên giao diện vào một hàm tập trung, giúp code ổn định hơn.
