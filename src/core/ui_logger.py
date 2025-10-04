# file-path: src/core/ui_logger.py
# version: 1.0
# last-updated: 2025-10-04
# description: Custom logging handler để chuyển hướng log ra CtkTextbox trên giao diện.

import logging
import customtkinter

class CTkTextboxHandler(logging.Handler):
    def __init__(self, textbox: customtkinter.CTkTextbox):
        super().__init__()
        self.textbox = textbox

    def emit(self, record):
        msg = self.format(record)
        
        # Lên lịch cập nhật textbox trên luồng chính để đảm bảo an toàn
        self.textbox.after(0, self.update_textbox, msg)

    def update_textbox(self, msg):
        # Tạm thời bật để ghi, sau đó tắt đi để người dùng không thể gõ vào
        self.textbox.configure(state="normal")
        self.textbox.insert("end", msg + "\n")
        self.textbox.see("end") # Tự động cuộn xuống dòng mới nhất
        self.textbox.configure(state="disabled")