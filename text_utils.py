# ==============================
# TEXT UTILITIES (SAVE + CLEAN)
# ==============================

import os
import re
from datetime import datetime


# ==============================
# SAVE TEXT
# ==============================
def save_text(text, prefix="script"):
    """Lưu script vào thư mục logs để đối chiếu sau này"""
    os.makedirs("logs", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs/{prefix}_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"💾 Saved: {filename}")
    return filename


# ==============================
# CLEAN TEXT FOR TTS (PRO)
# ==============================
def clean_text_for_tts(text):
    """Làm sạch văn bản thô trước khi đưa vào bộ chuẩn hóa số liệu"""
    
    # 1. Chuẩn hóa khoảng trắng và Unicode
    text = text.strip()
    
    # 2. Xử lý các ký tự đặc biệt gây lỗi giọng đọc
    # Không thay thế dấu chấm bằng 'phẩy' ở đây vì sẽ làm hỏng logic đọc số thập phân của tts.py
    # Chỉ xử lý các ký hiệu toán học/biểu cảm
    text = text.replace("+", " tăng ")
    text = text.replace("-", " giảm ")
    
    # 3. Fix lỗi xuống dòng thừa hoặc dấu cách thừa
    text = re.sub(r"\n+", ". ", text) # Chuyển xuống dòng thành dấu chấm để ngắt câu
    text = re.sub(r"\s+", " ", text)

    # 4. Loại bỏ các ký tự icon/emoji nếu có (tránh TTS đọc mã icon)
    text = re.sub(r'[^\w\s\d.,%?!\-\+]', '', text)

    # 5. Fix ngắt câu cho tự nhiên
    text = text.replace("...", ". ")
    text = text.replace("..", ". ")
    
    # Lưu ý: % và số thập phân sẽ để cho hàm normalize_numbers trong tts.py xử lý 
    # để đảm bảo đọc đúng ngữ pháp (ví dụ: 1.5% -> một phẩy năm phần trăm)

    return text.strip()
