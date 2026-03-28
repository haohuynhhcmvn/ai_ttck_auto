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
            {"role": "system", "content": "Bạn là MC tài chính TikTok. Viết câu ngắn 5-10 từ. Kết thúc bằng dấu chấm."},
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
# ROLE: Bạn là Chuyên gia phân tích chiến lược tại một quỹ đầu tư lớn. 
# NHIỆM VỤ: Viết kịch bản bản tin tài chính TikTok "Deep Dive" dài 180 giây (450-5000 từ) sao cho phù hợp với tốc độ đọc 1.1x.

# THÔNG SỐ KỸ THUẬT (CỰC KỲ NGHIÊM NGẶT):
1. Độ dài câu: Bắt buộc từ 5 đến 15 từ. Không được ngắn hơn, không được dài hơn.
2. Dấu câu: Kết thúc mỗi câu bằng dấu chấm. Tuyệt đối không dùng dấu phẩy, dấu chấm phẩy hay dấu hai chấm.
3. Định dạng: Không hashtag. Không biểu tượng cảm xúc. Chỉ dùng chữ và số.
4. Nhịp điệu: MC cần đọc dứt khoát. Mỗi câu là một thông tin đắt giá.

# DỮ LIỆU ĐẦU VÀO:
- Chủ đề chính: {topic}
- Top tăng trưởng: {gain_text}
- Top sụt giảm: {lose_text}

# CẤU TRÚC KỊCH BẢN (Triển khai logic chuyên sâu):

PHẦN 1: HOOK (3-4 câu)
- Đưa ra một nhận định gây sốc hoặc hưng phấn về {topic}.

PHẦN 2: BỐI CẢNH VNINDEX & VĨ MÔ (Viết dài, chiếm 40% dung lượng)
- Liên kết chặt chẽ giữa chỉ số DXY, lợi suất trái phiếu Mỹ với tỷ giá trong nước.
- Phân tích tâm lý đám đông trước các tin tức kinh tế, lãi suất chính trị, lạm phát hoặc chiến tranh phạm vi toàn cầu và trong nước (dẫn chiếu 3 đến 5 tin tức nổi bật, nóng hổi).
- Diễn giải tác động của dòng vốn ngoại đối với tâm lý khối nội. 
- *Lưu ý: Chia nhỏ các phân tích phức tạp thành nhiều câu đơn 7 từ.*

PHẦN 3: DÒNG TIỀN & NGÀNH (3-4 câu)
- Chỉ tên 2-3 ngành đang là "vịnh tránh bão" hoặc "đầu tàu".
- Giải thích ngắn gọn lý do dòng tiền thông minh chọn các nhóm này.

PHẦN 4: TIÊU ĐIỂM CỔ PHIẾU (Dựa trên {gain_text})
- Chọn lọc 5 mã nổi bật nhất.
- Mỗi mã mô tả bằng 1 câu về giá và 1 câu về tín hiệu kỹ thuật/tin tức.

PHẦN 5: CHIẾN LƯỢC & QUẢN TRỊ (Phần kết, viết sâu)
- Đưa ra kịch bản hành động cụ thể cho vị thế đang cầm tiền và cầm hàng.
- Nhấn mạnh vào quản trị rủi ro và điểm chặn lãi.

# YÊU CẦU VỀ NGÔN NGỮ:
Sử dụng thuật ngữ tài chính chuyên nghiệp như: Lực cầu chủ động, Áp lực chốt lời, Phân kỳ dương, Cản tâm lý, Tích lũy nền chặt.

Hãy bắt đầu viết. Đảm bảo độ dài để MC đọc trong 90 giây.
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
