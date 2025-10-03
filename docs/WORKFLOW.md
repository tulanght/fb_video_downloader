# QUY TRÌNH LÀM VIỆC DỰ ÁN (Project Workflow)
# version: 1.2
# last-updated: 2025-10-03
# description: Bổ sung bước xóa nhánh sau khi hợp nhất (merge).

## 1. Triết lý Chung
* **Nguồn sự thật duy nhất:** Nhánh `main` là nền tảng ổn định. Mọi thứ trên `main` phải luôn ở trạng thái chạy được.
* **Làm việc trên nhánh:** Mọi thay đổi (tính năng, sửa lỗi) đều phải được thực hiện trên nhánh riêng.
* **Hợp nhất qua Pull Request (PR):** Mọi thay đổi chỉ được đưa vào `main` thông qua PR để đảm bảo có sự rà soát.
* **AI là Cộng tác viên:** Gemini AI phải tuân thủ nghiêm ngặt toàn bộ quy trình này.

---
## 2. Quy trình làm việc với Git

### 2.1. Đặt tên nhánh
* **Tính năng mới:** `feature/<ten-tinh-nang-ngan-gon>` (ví dụ: `feature/gui-downloader-tab`)
* **Sửa lỗi:** `fix/<ten-loi>` (ví dụ: `fix/video-list-not-updating`)
* **Tài liệu:** `docs/<noi-dung-cap-nhat>` (ví dụ: `docs/update-readme`)
* **Tái cấu trúc:** `refactor/<pham-vi>` (ví dụ: `refactor/database-queries`)

### 2.2. Quy ước Commit Message
* Sử dụng **Conventional Commits** (`<type>(<scope>): <subject>`).
* Ví dụ: `feat(ui): add progress bar to downloader tab` hoặc `fix(scraper): handle private video errors`.

### 2.3. Quy trình Hợp nhất và Dọn dẹp
Sau khi một nhánh `feature` hoặc `fix` đã được kiểm thử và sẵn sàng, quy trình hợp nhất vào `main` sẽ bao gồm các bước sau:
1.  **Cập nhật `main`:**
    ```bash
    git checkout main
    git pull origin main
    ```
2.  **Hợp nhất nhánh:**
    ```bash
    git merge <ten-nhanh-feature>
    ```
3.  **Đẩy `main` lên remote:**
    ```bash
    git push origin main
    ```
4.  **Dọn dẹp (Cleanup):**
    ```bash
    # Xóa nhánh ở máy cục bộ
    git branch -d <ten-nhanh-feature>

    # Xóa nhánh ở trên GitHub (tùy chọn nhưng được khuyến khích)
    git push origin --delete <ten-nhanh-feature>
    ```

---
## 3. Quy trình Cộng tác với Gemini AI (BẮT BUỘC)

### 3.1. Cấu trúc Phản hồi Chuẩn
Mọi phản hồi chính (khi cung cấp kế hoạch hoặc mã nguồn) phải tuân thủ cấu trúc 4 phần:
1.  **Phần 1:** Phân tích & Kế hoạch
2.  **Phần 2:** Gói Cập Nhật Mục Tiêu (Mã nguồn)
3.  **Phần 3:** Hướng dẫn Hành động & Lệnh Git
4.  **Phần 4:** Kết quả Kỳ vọng & Cảnh báo

### 3.2. Quy tắc Cung cấp Mã nguồn
* **Sửa đổi nhỏ (Hotfix):** Khi chỉ sửa đổi bên trong một hàm đã có, AI chỉ cung cấp lại hàm đó, kèm theo một bình luận `# hotfix - YYYY-MM-DD - [Mô tả]` ở phía trên.
* **Thay đổi lớn:** Khi thêm bất kỳ hàm/class mới nào, tái cấu trúc lớn, hoặc khi được yêu cầu, AI **bắt buộc** phải cung cấp lại **toàn bộ nội dung file**.

### 3.3. Luồng làm việc
* **Thay đổi Lớn / Phức tạp:** Tuân thủ quy trình 2 giai đoạn:
    1.  **Giai đoạn 1 - Phân tích & Xin Phê duyệt:** AI trình bày kế hoạch chi tiết và chờ người dùng đồng ý.
    2.  **Giai đoạn 2 - Thực thi:** Sau khi được phê duyệt, AI cung cấp mã nguồn và hướng dẫn.
* **Thay đổi Nhỏ / Sửa lỗi:**
    1.  **Phản hồi #1:** AI cung cấp mã nguồn `hotfix` và lệnh tạo nhánh, sau đó hỏi xác nhận.
    2.  **Phản hồi #2:** Sau khi người dùng xác nhận OK, AI cung cấp các lệnh để hoàn tất (commit, merge).

### 3.4. Cơ chế An toàn
* **"Làm mới Ngữ cảnh":** Trước mỗi lần cung cấp mã nguồn, AI phải nêu rõ phiên bản file đang được sử dụng làm cơ sở.
* **"CHECK-WORKFLOW":** Từ khóa để người dùng yêu cầu AI dừng lại và rà soát lại quy trình trong file này nếu có sai phạm.
* **Xác minh trước khi khẳng định:** AI phải tự kiểm tra lại mã nguồn/kịch bản được tạo ra so với kế hoạch trước khi khẳng định về kết quả của nó.

### 3.5. Môi trường Làm việc & Công cụ (VSCode)
* **Editor chính:** Visual Studio Code.
* **Chất lượng Code (Pylint):** Mã nguồn Python do AI cung cấp phải hướng đến tiêu chuẩn cao, sạch sẽ và tuân thủ PEP 8 để giảm thiểu các lỗi và cảnh báo từ Pylint.
* **Hỗ trợ (GitHub Copilot):** AI nhận biết rằng người dùng sử dụng Copilot để phân tích và hỗ trợ trong quá trình code. Vì vậy, mã nguồn và các giải thích từ AI cần phải rõ ràng, logic, và có cấu trúc tốt để người dùng và Copilot có thể hiểu và phối hợp hiệu quả.