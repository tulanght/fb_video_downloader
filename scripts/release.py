# file-path: scripts/release.py
# description: Script tự động nâng cấp phiên bản cho dự án fb_video_downloader.

import re
import datetime
from pathlib import Path

def update_main_app_file(file_path, new_version):
    """Cập nhật phiên bản trong file main_app.py."""
    try:
        content = file_path.read_text(encoding='utf-8')
        pattern = re.compile(r"APP_VERSION\s*=\s*['\"].+?['\"]")
        new_content = pattern.sub(f'APP_VERSION = "{new_version}"', content, count=1)
        if new_content != content:
            file_path.write_text(new_content, encoding='utf-8')
            print(f"✅ Đã cập nhật phiên bản trong: {file_path.name}")
        else:
            print(f"⚠️ Không tìm thấy dòng APP_VERSION trong: {file_path.name}")
    except Exception as e:
        print(f"❌ Lỗi khi cập nhật {file_path.name}: {e}")

def update_readme_file(file_path, new_version):
    """Cập nhật phiên bản trong file README.md."""
    try:
        content = file_path.read_text(encoding='utf-8')
        pattern = re.compile(r"(# FB Page Video Downloader v)\d+\.\d+\.\d+")
        new_content = pattern.sub(r"\g<1>" + new_version, content, count=1)
        if new_content != content:
            file_path.write_text(new_content, encoding='utf-8')
            print(f"✅ Đã cập nhật phiên bản trong: {file_path.name}")
        else:
            print(f"⚠️ Không tìm thấy tiêu đề phiên bản trong: {file_path.name}")
    except Exception as e:
        print(f"❌ Lỗi khi cập nhật {file_path.name}: {e}")

def update_changelog_file(file_path, new_version):
    """Chèn một mục phiên bản mới vào đầu file CHANGELOG.md."""
    try:
        today = datetime.date.today().isoformat()
        new_section = f"## [{new_version}] - {today}\n\n"
        
        content = file_path.read_text(encoding='utf-8')
        # Chèn ngay sau dòng tiêu đề chính
        insertion_point = re.search(r"(# Lịch sử thay đổi \(Changelog\)\n)", content)
        if insertion_point:
            position = insertion_point.end()
            new_content = content[:position] + "\n" + new_section + content[position:]
            file_path.write_text(new_content, encoding='utf-8')
            print(f"✅ Đã chèn mục mới cho v{new_version} vào: {file_path.name}")
        else:
            print(f"⚠️ Không tìm thấy điểm chèn trong: {file_path.name}")

    except Exception as e:
        print(f"❌ Lỗi khi cập nhật {file_path.name}: {e}")

def main():
    project_root = Path(__file__).parent.parent
    main_app_file = project_root / "src" / "main_app.py"
    readme_file = project_root / "README.md"
    changelog_file = project_root / "docs" / "CHANGELOG.md"

    # Tìm phiên bản hiện tại từ main_app.py
    try:
        content = main_app_file.read_text(encoding='utf-8')
        current_version_match = re.search(r"APP_VERSION\s*=\s*['\"](.+?)['\"]", content)
        if not current_version_match:
            print("❌ LỖI: Không tìm thấy 'APP_VERSION' trong main_app.py!")
            return
        current_version = current_version_match.group(1)
    except FileNotFoundError:
        print(f"❌ LỖI: Không tìm thấy file {main_app_file}!")
        return

    print(f"Phiên bản hiện tại là: {current_version}")
    new_version = input(f"Nhập phiên bản mới (ví dụ: 0.2.0): ").strip()

    if not re.match(r"^\d+\.\d+\.\d+$", new_version):
        print("Đã hủy. Định dạng phiên bản không hợp lệ.")
        return
    if new_version == current_version:
        print("Đã hủy. Phiên bản mới trùng với phiên bản cũ.")
        return

    print("-" * 30)
    print(f"🚀 Bắt đầu nâng cấp phiên bản từ {current_version} lên {new_version}...")

    update_main_app_file(main_app_file, new_version)
    update_readme_file(readme_file, new_version)
    update_changelog_file(changelog_file, new_version)

    print("-" * 30)
    print("✨ Hoàn tất!")
    print("👉 Hành động tiếp theo: Mở file CHANGELOG.md và điền vào các thay đổi chi tiết.")

if __name__ == "__main__":
    main()