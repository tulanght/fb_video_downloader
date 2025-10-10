# file-path: src/ui/components.py
# version: 1.0
# last-updated: 2025-10-09
# description: Chứa các lớp (class) cho các thành phần giao diện phụ như cửa sổ popup.

import customtkinter

class GuidePopup(customtkinter.CTkToplevel):
    def __init__(self, master, title, message, show_checkbox=False, on_close_callback=None):
        super().__init__(master)
        self.title(title)
        self.geometry("700x550")
        self.resizable(True, True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.on_close_callback = on_close_callback
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text=title, label_font=("", 14, "bold"))
        scrollable_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        scrollable_frame.grid_columnconfigure(0, weight=1)

        message_label = customtkinter.CTkLabel(scrollable_frame, text=message, wraplength=650, justify="left", anchor="w")
        message_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        if show_checkbox:
            self.show_again_checkbox = customtkinter.CTkCheckBox(self, text="Không hiển thị lại hướng dẫn này")
            self.show_again_checkbox.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.transient(master)
        self.after(100, self.center_window)

    def center_window(self):
        self.master.update_idletasks()
        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()
        popup_width = self.winfo_width()
        popup_height = self.winfo_height()
        x = master_x + (master_width // 2) - (popup_width // 2)
        y = master_y + (master_height // 2) - (popup_height // 2)
        self.geometry(f"+{x}+{y}")

    def on_closing(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()

class CaptionViewerWindow(customtkinter.CTkToplevel):
    def __init__(self, master, title, caption):
        super().__init__(master)
        self.title("Nội dung Caption")
        self.geometry("600x400")
        self.resizable(True, True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title_label = customtkinter.CTkLabel(self, text=title, font=customtkinter.CTkFont(size=14, weight="bold"))
        title_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        caption_textbox = customtkinter.CTkTextbox(self, wrap="word")
        caption_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        caption_textbox.insert("1.0", caption)
        caption_textbox.configure(state="disabled")
        
        self.transient(master)