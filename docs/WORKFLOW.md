# QUY TRÌNH LÀM VIỆC DỰ ÁN (Project Workflow)
# version: 2.0
# last-updated: 2025-10-08
# description: Đại tu quy trình làm việc, giới thiệu "Quy ước Kiến trúc sư" và các quy tắc giao tiếp mới.

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
Sử dụng tiền tố để làm rõ mục đích của commit:
* `feat:` (tính năng mới)
* `fix:` (sửa lỗi)
* `docs:` (cập nhật tài liệu)
* `style:` (thay đổi về định dạng, không ảnh hưởng logic)
* `refactor:` (tái cấu trúc mã nguồn)
* `test:` (thêm hoặc sửa test)
* `chore:` (các công việc khác như cập nhật build script)

### 2.3. Luồng làm việc cơ bản
1.  **Tạo nhánh:** `git checkout -b <ten-nhanh>`
2.  **Làm việc & Commit:**
    * `git add <cac-file-thay-doi>`
    * `git commit -m "<tien-to>: <noi-dung-commit>"`
3.  **Hợp nhất vào main:**
    * `git checkout main`
    * `git merge <ten-nhanh>`
4.  **Xóa nhánh (sau khi đã hợp nhất):**
    * `git branch -d <ten-nhanh>`
5.  **Đẩy lên Repository:**
    * `git push origin main` (và `git push origin --tags` nếu có tạo tag mới)

---
## 3. Quy ước Tương tác với AI (Gemini)

### 3.1. Mô hình Hợp tác
* **Mô hình "Kiến trúc sư & Người triển khai":**
    * **Người dùng (Kiến trúc sư):** Đưa ra yêu cầu, định hình sản phẩm, thiết kế tính năng và phê duyệt hướng đi.
    * **AI (Người triển khai):** Đề xuất giải pháp kỹ thuật, viết mã nguồn theo yêu cầu và tuân thủ nghiêm ngặt quy trình.

### 3.2. Giao tiếp bằng "Bản vá Code" (Code Patch)
* Mọi thay đổi về code sẽ được ưu tiên giao tiếp bằng định dạng **"Bản vá Code"** (Tìm và Thay thế), chỉ rõ file và hàm/dòng cần thay đổi.
* AI chỉ được cung cấp toàn bộ nội dung file khi tạo file mới hoặc khi có sự thay đổi lớn (trên 70%) và đã được Kiến trúc sư phê duyệt trước.

### 3.3. Quy tắc "Module hóa"
* Chủ động chia nhỏ các file dài. Mọi file mới được tạo ra sẽ cố gắng giữ dưới 200 dòng.
* Các file hiện có quá dài sẽ là đối tượng ưu tiên để tái cấu trúc trong các giai đoạn "Dọn dẹp".

### 3.4. Quy tắc "Phê duyệt Thiết kế"
* AI **TUYỆT ĐỐI KHÔNG** được cung cấp bất kỳ mã nguồn nào cho một tính năng mới hoặc thay đổi kiến trúc lớn cho đến khi Kiến trúc sư (Người dùng) đưa ra lời xác nhận rõ ràng (ví dụ: "OK, tôi đồng ý với kế hoạch này", "Hãy bắt đầu triển khai").

### 3.5. Cơ chế An toàn
* **"Làm mới Ngữ cảnh":** Trước mỗi lần cung cấp mã nguồn, AI phải nêu rõ phiên bản file đang được sử dụng làm cơ sở.
* **"CHECK-WORKFLOW":** Từ khóa để người dùng yêu cầu AI dừng lại và rà soát lại quy trình trong file này nếu có sai phạm.
* **Xác minh trước khi khẳng định:** AI phải tự kiểm tra lại mã nguồn/kịch bản được tạo ra so với kế hoạch trước khi khẳng định về kết quả của nó.