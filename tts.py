# ============================== 
# TTS PRO STABLE FIXED (NO COMMA BUG)
# ==============================

import edge_tts
import asyncio
import uuid
import re
import random
from num2words import num2words

# ==============================
# CONFIG
# ==============================

VOICES = {
    "female": "vi-VN-HoaiMyNeural",
    "male": "vi-VN-NamMinhNeural"
}

RATE = "+10%"
PITCH = "-5Hz"
VOLUME = "+30%"   # âm lượng rõ

_loop = None

# ==============================
# EVENT LOOP (GITHUB SAFE)
# ==============================

def get_loop():
    global _loop
    if _loop is None:
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop

# ==============================
# NUMBER NORMALIZATION
# ==============================

def read_decimal(num_str):
    integer, decimal = num_str.split(".")
    int_part = num2words(int(integer), lang="vi")
    # Đọc từng chữ số sau dấu phẩy (vd: 05 -> không năm)
    dec_part = " ".join(num2words(int(d), lang="vi") for d in decimal)
    return f"{int_part} phẩy {dec_part}"

def process_number_str(num_str):
    """Hàm lõi để xử lý chuỗi số thuần túy"""
    try:
        if "." in num_str:
            return read_decimal(num_str)
        return num2words(int(num_str), lang="vi")
    except Exception:
        return num_str

def convert_number(match):
    """Wrapper cho regex sub"""
    return process_number_str(match.group())

def normalize_numbers(text):
    # 1. Xử lý phần trăm (chỉ lấy phần số ở group 1 để convert, sau đó thêm chữ 'phần trăm')
    text = re.sub(r'(\d+(\.\d+)?)%', lambda m: process_number_str(m.group(1)) + " phần trăm", text)
    
    # 2. Xử lý số hàng ngàn có dấu phẩy (vd: 1,000,000)
    text = re.sub(r'(\d{1,3}(,\d{3})+)', lambda m: num2words(int(m.group().replace(",", "")), lang="vi"), text)
    
    # 3. Xử lý các số thường & thập phân còn lại
    text = re.sub(r'\d+(\.\d+)?', convert_number, text)
    
    return text

# ==============================
# CLEAN TEXT (TTS FRIENDLY)
# ==============================

def clean_text(text):
    # Xử lý số liệu trước
    text = normalize_numbers(text)

    # Tên chỉ số tài chính
    text = text.replace("VN-Index", "vi en index")
    text = text.replace("HNX-Index", "hát en xờ index")
    text = text.replace("UPCOM", "úp com")
    text = text.replace("VN30", "vi en ba mươi")

    # Loại bỏ ký tự nguy hiểm cho TTS
    text = re.sub(r'[<>{}]', '', text)

    # 🔥 Chuyển dấu phẩy và chấm thành pause tự nhiên
    text = text.replace(",", "... ")   # KHÔNG đọc "comma"
    text = text.replace(".", ". ")     # pause dài hơn cho chấm
    text = text.replace("...", "... ") # fix triple-dot nếu bị trùng

    # Fix spacing (xóa khoảng trắng thừa)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

# ==============================
# TTS CORE
# ==============================

async def tts_async(text, filename, voice):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=RATE,
        pitch=PITCH,
        volume=VOLUME
    )
    await communicate.save(filename)

# ==============================
# MAIN FUNCTION
# ==============================

def text_to_speech(text, voice=None):
    # Làm sạch văn bản và chuẩn hóa số liệu
    text = clean_text(text)

    # Chọn giọng random nếu chưa chỉ định
    if not voice:
        voice = random.choice(list(VOICES.values()))

    # Tạo tên file random để không bị ghi đè
    filename = f"voice_{uuid.uuid4().hex}.mp3"

    # Chạy event loop an toàn
    loop = get_loop()
    loop.run_until_complete(tts_async(text, filename, voice))

    return filename
