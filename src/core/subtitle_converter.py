# file-path: src/core/subtitle_converter.py
# version: 1.1
# last-updated: 2025-10-05
# description: Cải tiến logic để nối các mảnh phụ đề thành câu hoàn chỉnh.

import re
import os
import logging

def convert_srt_to_clean_txt(srt_path: str):
    """
    Đọc một file .srt, loại bỏ timestamp và số thứ tự, sau đó lưu thành file .txt.
    """
    if not srt_path or not os.path.exists(srt_path):
        return None

    txt_path = srt_path.rsplit('.', 1)[0] + ".txt"
    
    try:
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Loại bỏ dòng số và dòng timestamp
        content = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n', '', content, flags=re.MULTILINE)
        # Nối các dòng văn bản lại với nhau, thay thế xuống dòng bằng dấu cách
        content = re.sub(r'\n(?![\n])', ' ', content)
        # Loại bỏ các dòng trống thừa
        clean_text = re.sub(r'\n{2,}', '\n', content).strip()

        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(clean_text)
        
        logging.info(f"Đã chuyển đổi phụ đề thành công: {os.path.basename(txt_path)}")
        return txt_path
    except Exception as e:
        logging.error(f"Lỗi khi chuyển đổi phụ đề {os.path.basename(srt_path)}: {e}")
        return None