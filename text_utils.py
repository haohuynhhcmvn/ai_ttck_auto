# ==============================
# TEXT UTILITIES (SAVE + CLEAN PRO)
# ==============================

import os
import re
import unicodedata
from datetime import datetime

# ==============================
# SAVE TEXT
# ==============================
def save_text(text, prefix="script"):
    """Lưu script vào thư mục logs với cấu trúc thư mục theo ngày"""
    # Tạo folder theo ngày để dễ quản lý file log
    today_folder = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join("logs", today_folder)
    os.makedirs(log_path, exist_ok=True)

    timestamp = datetime.now().strftime("%H%M%S")
    filename = os.path.join(log_path, f"{prefix}_{timestamp}.txt")

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"💾 Saved: {filename}")
    except Exception as e:
        print(f"⚠️ Lỗi lưu file: {e}")
        
    return filename

# ==============================
# CLEAN TEXT FOR TTS (ADVANCED)
# ==============================
def clean_text_for_tts(text):
    """Làm sạch văn bản thô, tối ưu nhịp nghỉ cho MC AI"""
    if not text:
        return ""

    # 1. Chuẩn hóa Unicode (NFC) - Tránh lỗi font tiếng Việt khi TTS đọc
    text = unicodedata.normalize("NFC", text)
    
    # 2. Xử lý các cụm từ chuyên ngành để TTS đọc tự nhiên hơn
    # Thay vì đọc 'vê nờ in đếch', AI sẽ đọc rõ hơn nếu ta xử lý nhẹ
    replacements = {
        "VN-INDEX": "Vờ ni In đéc",
        "VNINDEX": "Vờ ni In đéc",
        "HĐQT": "Hội đồng quản trị",
        "CP": "Cổ phần",
        "với": "với,", # Thêm phẩy nhẹ để AI ngắt nghỉ tự nhiên
        "nhưng": "nhưng,", 
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)

    # 3. Xử lý dấu xuống dòng (Thông minh hơn)
    # Thay xuống dòng bằng dấu chấm, sau đó thu gọn các dấu chấm thừa
    text = text.replace("\n", ". ")
    
    # 4. Loại bỏ ký tự đặc biệt, chỉ giữ lại chữ, số và các dấu ngắt nghỉ cơ bản
    # Giữ lại: % . , ! ? - + (để tts.py xử lý số liệu sau)
    text = re.sub(r'[^\w\s\d.,%?!\-\+]', '', text)

    # 5. Dọn dẹp khoảng trắng và dấu câu trùng lặp
    text = re.sub(r'\.{2,}', '. ', text)  # .. -> .
    text = re.sub(r',{2,}', ', ', text)   # ,, -> ,
    text = re.sub(r'\s+', ' ', text)      # Khoảng trắng thừa
    
    # 6. Quy tắc "Dấu cách sau dấu câu"
    # Đảm bảo sau dấu chấm/phẩy luôn có khoảng trắng để TTS nhận diện nhịp nghỉ
    text = text.replace(".", ". ").replace(",", ", ")
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

# --- TEST ---
if __name__ == "__main__":
    raw = """
    VN-INDEX hôm nay bùng nổ!!
    Dòng tiền vào CP Thép rất mạnh.
    Thị trường tăng +15 điểm...
    """
    print("--- RAW ---")
    print(raw)
    print("--- CLEANED ---")
    print(clean_text_for_tts(raw))
