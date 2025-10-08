# Lịch sử thay đổi (Changelog)

## [0.5.4] - 2025-10-09
## [0.5.0] - 2025-10-08
### ✨ Tính năng mới (Features)
- **Thiết kế lại Giao diện:** "Đại tu" toàn bộ giao diện người dùng với theme tối hiện đại, màu sắc có độ tương phản cao và bố cục được sắp xếp lại một cách khoa học, chuyên nghiệp.
- **Tăng tốc Lọc Video (Đa luồng):** Tích hợp kiến trúc đa luồng cho "Bước 2: Lọc", cho phép xử lý nhiều video cùng lúc, giảm đáng kể thời gian chờ đợi.
- **Tùy chọn Đơn luồng:** Thêm một switch trên giao diện để người dùng có máy cấu hình yếu có thể chuyển về chế độ lọc đơn luồng (tuần tự) để đảm bảo tính ổn định.
- **Tự động Quản lý `chromedriver`:** Tích hợp thư viện `webdriver-manager` để tự động tải và cập nhật `chromedriver.exe` tương thích với phiên bản Chrome của người dùng, loại bỏ hoàn toàn việc phải cập nhật thủ công.
- **Hướng dẫn Người dùng Mới:** Xây dựng hệ thống popup thông minh, có thể di chuyển được:
    - Tự động phát hiện và hướng dẫn cài đặt cookie chi tiết cho lần chạy đầu tiên.
    - Hiển thị hướng dẫn sử dụng nhanh với tùy chọn "Không hiển thị lại".
- **Tùy chỉnh Trải nghiệm:** Bổ sung các tùy chọn mới trên giao diện như "Thời gian chờ cuộn" để đối phó với các điều kiện mạng chậm.

### 🐛 Sửa lỗi (Bug Fixes)
- **Sửa lỗi "0 Video":** Khắc phục triệt để lỗi logic cốt lõi khiến chương trình không lọc được video nào, đảm bảo `yt-dlp` hoạt động ổn định.
- **Sửa lỗi Treo Giao diện:** Loại bỏ hoàn toàn hiện tượng giao diện bị "đơ", lag hoặc các nút bị vô hiệu hóa vĩnh viễn sau khi một tác vụ hoàn thành.
- **Cải thiện Trải nghiệm (UX):** Khôi phục lại cơ chế hiển thị kết quả real-time trong quá trình lọc, giúp người dùng không phải nhìn vào một màn hình trống.
- **Sửa lỗi Bố cục & Hiển thị:** Khắc phục hàng loạt lỗi về giao diện như widget bị che khuất, chữ khó đọc, popup bị lỗi vị trí và không thể thay đổi kích thước.

### ♻️ Tái cấu trúc (Refactoring)
- **Chuẩn hóa Đường dẫn:** Tái cấu trúc toàn bộ mã nguồn để sử dụng đường dẫn tuyệt đối, đảm bảo ứng dụng có thể chạy "di động" (portable) từ bất kỳ vị trí nào.
- **Tối ưu hóa Code:** Dọn dẹp, tối ưu và thêm chú thích vào nhiều thành phần code sau quá trình debug kéo dài.

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
