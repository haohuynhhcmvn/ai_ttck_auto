# ==============================
# TEXT UTILITIES (SAVE + DYNAMIC CLEAN PRO)
# ==============================

import os
import re
import unicodedata
from datetime import datetime

# ==============================
# SAVE TEXT (GITHUB ACTIONS COMPATIBLE)
# ==============================
def save_text(text, prefix="script"):
    """
    Lưu script vào thư mục logs. 
    Trên GitHub Actions, bạn cần dùng action/upload-artifact để tải thư mục này về.
    """
    # Tạo cấu trúc folder: logs/2024-05-20/
    today_folder = datetime.now().strftime("%Y-%m-%d")
    log_dir = os.path.join("logs", today_folder)
    
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # File name: script_143005_3fa2.txt (thêm 4 ký tự random tránh trùng nếu chạy nhanh)
    timestamp = datetime.now().strftime("%H%M%S")
    import uuid
    short_id = uuid.uuid4().hex[:4]
    filename = os.path.join(log_dir, f"{prefix}_{timestamp}_{short_id}.txt")

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"💾 [LOG]: Đã lưu nội dung vào {filename}")
    except Exception as e:
        print(f"⚠️ [ERROR]: Không thể lưu file log: {e}")
        
    return filename

# ==============================
# CLEAN TEXT FOR TTS (DYNAMIC PRO)
# ==============================
def clean_text_for_tts(text):
    """
    Tiền xử lý văn bản cực sạch cho tts.py.
    Mục tiêu: Ngắt nghỉ đúng chỗ, đọc đúng thuật ngữ tài chính.
    """
    if not text:
        return ""

    # 1. Chuẩn hóa Unicode & Viết thường (giúp TTS ổn định hơn, trừ mã CK)
    text = unicodedata.normalize("NFC", text)
    
    # 2. Xử lý từ viết tắt & thuật ngữ (Phiên âm hóa để AI đọc chuẩn 100%)
    replacements = {
        # --- Nhóm Chỉ số & Sàn giao dịch ---
        "VN-INDEX": "Vờ ni In đếch",
        "VNINDEX": "Vờ ni In đếch",
        "VNI": "Vờ ni",
        "HNX": "Hà Nội Index",
        "UPCOM": "Up cơm",
        "HOSE": "Hô-se",
        "DOW JONES": "Dao Giôn",
        "NASDAQ": "Nát đắc",
        "S&P 500": "Ét en Pi năm trăm",
        "FED": "Phét",
    
        # --- Nhóm Thuật ngữ Doanh nghiệp & Tài chính ---
        "HĐQT": "Hội đồng quản trị",
        "CP": "Cổ phần",
        "P/E": "P trên E",
        "EPS": "E P S",
        "ETF": "E T Ép",
        "BĐS": "Bất động sản",
        "NH": "Ngân hàng",
        "CK": "Chứng khoán",
        "VNĐ": "Việt Nam Đồng",
        "USD": "Đô la Mỹ",
        "EBITDA": "Ê-bít-đa",
    
        # --- Nhóm Ngân hàng (Đọc tên thương hiệu) ---
        "VCB": "Vietcombank",
        "TCB": "Techcombank",
        "STB": "Sacombank",
        "MBB": "Ngân hàng Quân đội",
        "VPB": "Vi-pi-banh",
        "HDB": "Hát-đê-banh",
        "BID": "Bi-Ai-Đi",
        "CTG": "Viết-tin-banh",
        "Agribank": "A-ghi-banh",
    
        # --- Nhóm Phân tích Kỹ thuật (Ghi rõ số để AI đọc chuẩn) ---
        "MA150": "Mờ A một trăm năm mươi",
        "MA200": "Mờ A hai trăm",
        "RSI": "Rờ Ét i",
        "MACD": "Mờ A xê đê",
        "Fibonacci": "Phi-bô-na-si",
        "Bollinger Bands": "Bô-lin-ger-ben",
    
        # --- Ký hiệu số & Đơn vị (Thêm dấu phẩy để ngắt nghỉ) ---
        "tỷ": "tỷ,",
        "triệu": "triệu,",
        "điểm": "điểm,",
        "%": " phần trăm,",
        "+": "tăng",
        "-": "giảm",
    
        # --- Từ nối & Trạng từ (Tạo nhịp điệu báo chí) ---
        "tăng trưởng": "tăng trưởng,", 
        "giảm điểm": "giảm điểm,",
        "tuy nhiên": "tuy nhiên,",
        "do đó": "do đó,",
        "đặc biệt là": "đặc biệt là,",
        "Đáng chú ý": "Đáng chú ý,",
        "Theo đó": "Theo đó,",
        "Mặt khác": "Mặt khác,",
        "Kết phiên": "Kết phiên,",
        "Dòng tiền": "Dòng tiền,",
        "Áp lực chốt lời": "Áp lực chốt lời,",
    }
    
    # Duyệt và thay thế (Ưu tiên từ dài trước để tránh lỗi thay thế con)
    for old, new in sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True):
        # Dùng regex để chỉ thay thế khi nó là một từ độc lập
        text = re.sub(r'\b' + re.escape(old) + r'\b', new, text, flags=re.IGNORECASE)

    # 3. Xử lý mã cổ phiếu (Ví dụ: SSI -> S S I)
    # Tìm các cụm 3 chữ cái viết hoa đứng độc lập
    text = re.sub(r'\b([A-Z]{3})\b', lambda m: " ".join(list(m.group())), text)

    # 4. Xử lý xuống dòng & Ký tự đặc biệt
    text = text.replace("\n", ". ")
    # Loại bỏ các ký tự rác thường gặp từ AI (dấu sao, gạch đầu dòng, hashtag)
    text = re.sub(r'[\*\#\-\_\>\<\(\)\[\]]', ' ', text)

    # 5. Tối ưu dấu câu cho nhịp nghỉ của MC
    # Biến dấu chấm lửng hoặc nhiều dấu chấm thành một nhịp nghỉ dài
    text = re.sub(r'\.{2,}', '... ', text)
    
    # 6. Quy tắc "Space sau dấu câu" & Clean-up
    text = text.replace(".", ". ").replace(",", ", ").replace("?", "? ").replace("!", "! ")
    
    # Xóa khoảng trắng thừa
    text = re.sub(r'\s+', ' ', text)
    
    # Đảm bảo các con số không bị dính vào chữ (ví dụ: 15điểm -> 15 điểm)
    text = re.sub(r'(\d+)([a-zA-Záàảãạâấầẩẫậăắằẳẵặéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ])', r'\1 \2', text)

    return text.strip()

# ==============================
# SUBTITLE TICKER CLEANER
# ==============================
def clean_for_ticker(text):
    """Làm sạch văn bản để đưa vào dải chữ chạy ngang (Ticker)"""
    # Ticker cần ngắn gọn, VIẾT HOA, ngăn cách bởi dấu chấm tròn hoặc dash
    text = text.replace("\n", " • ")
    text = re.sub(r'\s+', ' ', text)
    return text.upper().strip()

# --- TEST ---
if __name__ == "__main__":
    raw_content = """
    VN-INDEX hôm nay bùng nổ vượt 1200 điểm!!
    Nhóm BĐS và NH dẫn dắt thị trường.
    Mã SSI và HPG tăng mạnh với EPS ấn tượng.
    Thị trường sẽ tiếp tục tăng trưởng trong tuần tới.
    """
    
    cleaned = clean_text_for_tts(raw_content)
    print("--- RAW CONTENT ---")
    print(raw_content)
    print("\n--- CLEANED FOR TTS ---")
    print(cleaned)
    
    # Test save
    save_text(cleaned, prefix="clean_script")
