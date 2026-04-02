# ============================== 
# TTS PRO DYNAMIC (AI-VOICE OPTIMIZED)
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

# Danh sách giọng đọc đa dạng để tránh trùng lặp
VOICES = [
    "vi-VN-HoaiMyNeural", # Nữ - Truyền cảm
    "vi-VN-NamMinhNeural"  # Nam - Chững chạc
]

# Tốc độ và âm lượng tối ưu cho Video ngắn (9:16)
RATE = "+12%"  # Đọc nhanh hơn một chút để giữ nhịp TikTok
PITCH = "+0Hz" 
VOLUME = "+0%"

_loop = None

# ==============================
# EVENT LOOP (GITHUB SAFE)
# ==============================
def get_loop():
    global _loop
    if _loop is None:
        try:
            _loop = asyncio.get_event_loop()
        except RuntimeError:
            _loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_loop)
    return _loop

# ==============================
# NUMBER NORMALIZATION
# ==============================
def read_decimal(num_str):
    if "." not in num_str:
        return num2words(int(num_str), lang="vi")
    integer, decimal = num_str.split(".")
    int_part = num2words(int(integer), lang="vi")
    dec_part = " phẩy " + " ".join(num2words(int(d), lang="vi") for d in decimal)
    return f"{int_part}{dec_part}"

def normalize_numbers(text):
    # 1. Xử lý phần trăm (vd: 5.5% -> năm phẩy năm phần trăm)
    text = re.sub(r'(\d+(\.\d+)?)%', lambda m: read_decimal(m.group(1)) + " phần trăm", text)
    
    # 2. Xử lý số hàng ngàn (1,200 -> một nghìn hai trăm)
    text = re.sub(r'(\d{1,3}(,\d{3})+)', lambda m: num2words(int(m.group().replace(",", "")), lang="vi"), text)
    
    # 3. Xử lý số thập phân và số nguyên lẻ
    text = re.sub(r'\d+(\.\d+)?', lambda m: read_decimal(m.group()), text)
    
    return text

# ==============================
# CLEAN TEXT (DYNAMIC PROSODY)
# ==============================
def clean_text_for_tts(text):
    # Chuyển chữ hoa thành chữ thường để tránh AI đọc rời rạc từng chữ (trừ mã CK)
    # Tuy nhiên, mã chứng khoán cần đọc rời (SSI -> S S I)
    text = re.sub(r'\b([A-Z]{3})\b', lambda m: " ".join(list(m.group())), text)

    # Chuẩn hóa tên chỉ số tài chính (viết kiểu phiên âm cho AI đọc chuẩn)
    dict_fix = {
        "VN-Index": "vi en in đếch",
        "HNX-Index": "hát en xờ in đếch",
        "UPCOM": "úp com",
        "VN30": "vi en ba mươi",
        "DXY": "đê ích i",
        "Fed": "phét",
        "FOMO": "phô mô",
        "CEO": "xê ê ô",
        "VND": "vi en đề"
    }
    for word, fix in dict_fix.items():
        text = text.replace(word, fix)

    # Xử lý số liệu
    text = normalize_numbers(text)

    # 🔥 TẠO NHỊP ĐIỆU (Đây là phần quan trọng nhất)
    # Thay dấu phẩy bằng dấu chấm lửng để AI nghỉ 1 nhịp ngắn
    text = text.replace(",", "... ")
    
    # Thêm dấu chấm vào cuối các câu ngắn nếu thiếu
    if not text.endswith(('.', '!', '?')):
        text += "."

    # Loại bỏ các ký tự đặc biệt gây lỗi giọng đọc
    text = re.sub(r'[\\/*+:;<=>@\[\]^_`{|}~]', '', text)
    
    # Xóa khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

# ==============================
# TTS CORE
# ==============================
async def tts_async(text, filename, voice):
    # Cấu hình ngắt nghỉ tự nhiên bằng cách điều chỉnh Rate/Pitch linh hoạt nếu cần
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
    """
    Hàm chính để gọi từ Pipeline.
    Trả về: đường dẫn file mp3 đã tạo.
    """
    # 1. Làm sạch và tạo nhịp điệu
    processed_text = clean_text_for_tts(text)

    # 2. Chọn giọng (Xoay vòng giọng Nam/Nữ để kênh không bị một màu)
    if not voice:
        voice = random.choice(VOICES)

    # 3. Tạo file (Dùng thư mục tạm hoặc uuid để tránh xung đột trên GitHub Actions)
    filename = f"voice_{uuid.uuid4().hex[:8]}.mp3"

    # 4. Thực thi
    try:
        loop = get_loop()
        loop.run_until_complete(tts_async(processed_text, filename, voice))
        print(f"✅ TTS Success: {filename} (Voice: {voice})")
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        return None

    return filename

# --- TEST ---
if __name__ == "__main__":
    test_script = "VN-Index hôm nay tăng 15.5 điểm. SSI bùng nổ thanh khoản, đạt 1,200 tỷ đồng."
    file = text_to_speech(test_script)
    print(f"File output: {file}")
