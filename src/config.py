# file-path: src/config.py
# version: 1.0
# last-updated: 2025-10-09
# description: Chứa các hằng số và giá trị cấu hình tập trung cho toàn bộ ứng dụng.

# --- App Info ---
APP_VERSION = "0.5.4"

# --- File Names ---
COOKIE_JSON_FILE = "facebook_cookies.json"
COOKIE_TXT_FILE = "facebook_cookies.txt"
SETTINGS_FILE = "settings.json"
CHROMEDRIVER_FILE = "chromedriver.exe"

# --- Directories ---
SESSIONS_DIR = "sessions"

# --- UI Settings ---
DISABLED_TEXT_COLOR = "#BFBFBF"
BUTTON_TEXT_COLOR = "#FFFFFF"
BUTTON_FG_COLOR = "#555555"
BUTTON_HOVER_COLOR = "#444444"

# --- Threading ---
DEFAULT_WORKER_COUNT = 5
MAX_WORKERS = 10