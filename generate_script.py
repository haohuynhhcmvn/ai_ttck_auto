# ==============================
# GENERATE SCRIPT PRO MAX (TTS READY)
# ==============================

import requests
import os
import time
import re
from datetime import datetime
from market_data import get_market_data
from num2words import num2words

# ==============================
# CONFIG & API KEYS
# ==============================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# Model names
QWEN_MODEL = "qwen/qwen3.5-122b-a10b"
GEMINI_MODEL = "gemini-2.5-flash"

# ==============================
# NUMBER NORMALIZATION (FIXED)
# ==============================
def read_decimal_or_int(num_str):
    num_str = num_str.replace(",", "") # Xóa dấu phẩy phân cách hàng ngàn nếu có
    try:
        if '.' in num_str:
            integer, decimal = num_str.split(".")
            int_part = num2words(int(integer), lang='vi')
            dec_part = ' '.join([num2words(int(d), lang='vi') for d in decimal])
            return f"{int_part} phẩy {dec_part}"
        else:
            return num2words(int(num_str), lang='vi')
    except:
        return num_str

def normalize_numbers(text):
    # 1. Xử lý phần trăm: 15.5% -> mười lăm phẩy năm phần trăm
    text = re.sub(r'(\d+(\.\d+)?)%', 
                  lambda m: read_decimal_or_int(m.group(1)) + " phần trăm", 
                  text)
    
    # 2. Xử lý số có dấu phẩy hàng ngàn: 1,200 -> một nghìn hai trăm
    text = re.sub(r'(\d{1,3}(?:,\d{3})+)',
                  lambda m: num2words(int(m.group().replace(",", "")), lang='vi'),
                  text)
    
    # 3. Xử lý số thập phân và số nguyên còn lại
    text = re.sub(r'\d+(\.\d+)?', lambda m: read_decimal_or_int(m.group()), text)
    return text

def optimize_for_tts(text):
    # Xóa các tiêu đề mục lục (VNINDEX, DÒNG TIỀN...) nếu bạn không muốn MC đọc to tên mục
    # Nhưng trong TikTok, MC thường đọc tiêu đề để chuyển cảnh, nên tôi giữ lại và làm sạch
    text = re.sub(r'[<>{}\[\]/\\*^$#@~_]', '', text)
    
    # Fix ngắt nghỉ: Dấu chấm/phẩy phải có khoảng trắng đằng sau để TTS nhận diện
    text = text.replace(".", ". ").replace(",", ", ").replace("...", "... ")
    text = re.sub(r'\s+', ' ', text)
    
    # Chuyển các ký hiệu đặc biệt thành chữ
    text = text.replace("%", " phần trăm")
    return text.strip()

# ==============================
# LLM CALLS (QWEN & GEMINI)
# ==============================
def call_qwen(prompt, retry=3): # Tăng lên 3 lần thử cho chắc chắn
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}", 
        "Content-Type": "application/json"
    }
    payload = {
        "model": QWEN_MODEL,
        "messages": [
            {"role": "system", "content": "Bạn là biên tập viên tài chính TikTok chuyên nghiệp. Viết câu ngắn 5-15 từ, kết thúc bằng dấu chấm. Tuyệt đối không dùng từ ngữ cam kết lợi nhuận hoặc lôi kéo đầu tư trực tiếp để đảm bảo an toàn chính sách cộng đồng."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.6,
        "max_tokens": 800 # Tăng nhẹ để tránh bị cắt cụt kịch bản
    }

    for i in range(retry):
        try:
            print(f"📡 Đang gọi Qwen (Lần thử {i+1})...")
            # Tăng timeout lên 60 giây vì Model 122B phản hồi rất chậm
            res = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            
            elif res.status_code == 429:
                print("⏳ Chạm giới hạn (Rate Limit). Chờ 10s...")
                time.sleep(10)
            else:
                print(f"⚠️ Qwen trả lỗi HTTP {res.status_code}: {res.text}")
                
        except requests.exceptions.Timeout:
            print(f"🕒 Lần {i+1}: Quá thời gian phản hồi (Timeout).")
        except Exception as e:
            print(f"❌ Lần {i+1} lỗi hệ thống: {e}")
        
        # Chờ lâu hơn sau mỗi lần thất bại (2s, 4s, 8s)
        time.sleep(2 ** (i + 1))
        
    return None

def call_gemini(prompt, retry=2):
    # URL cho Gemini 1.5 Flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    for i in range(retry):
        try:
            res = requests.post(url, json=payload, timeout=25)
            if res.status_code == 200:
                return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"⚠️ Gemini lỗi: {e}")
            time.sleep(2)
    return None

# ==============================
# GENERATE SCRIPT MAIN
# ==============================
def generate_script(topic, market_data=None):
    """
    Nhận topic và dữ liệu thị trường thực tế để viết script.
    """
    if not market_data:
        market_data = get_market_data()

    gain_text = market_data.get("gain_text", "Đang cập nhật")
    lose_text = market_data.get("lose_text", "Đang cập nhật")

    prompt = f"""
# ROLE: Bạn là Chuyên gia phân tích chiến lược am hiểu thuật toán kiểm duyệt nội dung tài chính trên TikTok.
# NHIỆM VỤ: Viết kịch bản bản tin "Deep Dive" 180 giây (450-500 từ).

# QUY TẮC AN TOÀN NỘI DUNG (BẮT BUỘC):
- KHÔNG dùng: "Làm giàu", "Kiếm tiền", "Cam kết", "Chắc chắn", "Múc/Xúc/Phím", "Lãi XX%".
- KHÔNG đưa ra lời khuyên đầu tư trực tiếp kiểu "Bạn nên mua...".
- TẬP TRUNG vào: Cảnh báo bẫy tâm lý, phân tích dữ liệu vĩ mô, chia sẻ kinh nghiệm quản trị rủi ro.

# THÔNG SỐ KỸ THUẬT:
1. Độ dài câu: Từ 5 đến 15 từ. Kết thúc bằng dấu chấm.
2. Tuyệt đối không dùng dấu phẩy, dấu hai chấm, hashtag hay emoji.
3. Chỉ dùng chữ tiếng Việt và số.

# DỮ LIỆU ĐẦU VÀO:
- Chủ đề: {topic}
- Tăng: {gain_text} | Giảm: {lose_text}

# CẤU TRÚC:
PHẦN 1: HOOK (3-4 câu)
- Đưa ra một câu hỏi hoặc sự thật ngầm hiểu gây tò mò về {topic}. 
- Ví dụ: "Bạn đã bao giờ tự hỏi tại sao đám đông thường sai ở vùng đỉnh chưa."

PHẦN 2: VĨ MÔ & TÂM LÝ (40%)
- Phân tích liên kết DXY, lợi suất trái phiếu và tỷ giá. 
- Chỉ ra 3-5 tin tức nóng hổi ảnh hưởng đến dòng tiền.

PHẦN 3: DÒNG TIỀN & PHẦN 4: TIÊU ĐIỂM
- Phân tích vận động của {gain_text} dưới góc độ kỹ thuật (Lực cầu, nền giá).

PHẦN 5: CHIẾN LƯỢC (Viết sâu)
- Tập trung vào tư duy quản trị vốn và các kịch bản thị trường có thể xảy ra.
- Kết thúc bằng một câu hỏi mở để tăng tương tác.
"""

    print("🤖 Đang khởi tạo AI viết kịch bản...")
    script = call_qwen(prompt) or call_gemini(prompt)

    if not script:
        print("⚠️ Cả 2 AI đều lỗi, dùng kịch bản dự phòng.")
        script = f"Thị trường hôm nay có biến động lớn. Nhóm tăng nổi bật gồm {gain_text}. Tuy nhiên áp lực bán vẫn hiện hữu tại {lose_text}. Nhà đầu tư cần hết sức cẩn trọng. Hãy theo dõi sát vùng hỗ trợ."

    # Xử lý hậu kỳ cho TTS
    script = normalize_numbers(script)
    script = optimize_for_tts(script)

    return script

# --- TEST ---
if __name__ == "__main__":
    test_topic = "Thị trường bùng nổ sau chuỗi ngày giảm"
    print(generate_script(test_topic))
