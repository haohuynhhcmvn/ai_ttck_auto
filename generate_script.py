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
QWEN_MODEL = "qwen/qwen2.5-72b-instruct" # NVIDIA NIM thường dùng bản này ổn định
GEMINI_MODEL = "gemini-1.5-flash"

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
def call_qwen(prompt, retry=2):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": QWEN_MODEL,
        "messages": [
            {"role": "system", "content": "Bạn là MC tài chính TikTok. Viết câu ngắn 5-10 từ. Kết thúc bằng dấu chấm. Không dùng ký tự lạ."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.6,
        "max_tokens": 600
    }
    for i in range(retry):
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=25)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"⚠️ Qwen lỗi: {e}")
            time.sleep(2)
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
Viết script video TikTok tài chính chuyên nghiệp.
YÊU CẦU CỰC NGHIÊM NGẶT:
1. Mỗi câu chỉ từ 5 đến 10 từ.
2. Kết thúc mỗi câu bằng dấu chấm.
3. Không sử dụng dấu phẩy giữa câu (thay bằng dấu chấm nếu cần ngắt).
4. Không dùng hashtag, không dùng biểu tượng cảm xúc.
5. Hook ngay câu đầu về: {topic}.

DỮ LIỆU THỰC TẾ HÔM NAY:
- Top tăng: {gain_text}.
- Top giảm: {lose_text}.

CẤU TRÚC SCRIPT:
- VNINDEX: Tóm tắt xu hướng và tâm lý.
- DÒNG TIỀN: 2-3 ngành hút tiền nhất.
- TOP 5 CỔ PHIẾU: Liệt kê mã và lý do ngắn gọn (ưu tiên nhóm tăng).
- KỸ THUẬT: Tín hiệu bùng nổ hoặc đảo chiều.
- CHIẾN LƯỢC: Lời khuyên nắm giữ hoặc quan sát.

Hãy viết theo phong cách MC tài chính bản tin 60 giây.
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
