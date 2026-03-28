# ==============================
# GENERATE SCRIPT PRO MAX (TTS READY)
# ==============================

import requests
import os
import time
from datetime import datetime
from market_data import get_market_data
from num2words import num2words
import re

# ==============================
# API KEYS
# ==============================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# ==============================
# NUMBER NORMALIZATION
# ==============================

def normalize_numbers(text):
    # % -> chữ
    text = re.sub(r'(\d+(\.\d+)?)%', 
                  lambda m: read_decimal_or_int(m.group()) + " phần trăm",
                  text)
    # 1,000,000 -> chữ
    text = re.sub(r'(\d{1,3}(?:,\d{3})+)',
                  lambda m: num2words(int(m.group().replace(",", "")), lang='vi'),
                  text)
    # số thường
    text = re.sub(r'\d+(\.\d+)?', lambda m: read_decimal_or_int(m.group()), text)
    return text

def read_decimal_or_int(num_str):
    if '.' in num_str:
        integer, decimal = num_str.split(".")
        int_part = num2words(int(integer), lang='vi')
        dec_part = ' '.join([num2words(int(d), lang='vi') for d in decimal])
        return f"{int_part} phẩy {dec_part}"
    else:
        return num2words(int(num_str), lang='vi')

# ==============================
# CLEAN TEXT (TTS FRIENDLY)
# ==============================

def optimize_for_tts(text):
    text = text.strip()
    # loại bỏ ký tự đặc biệt
    text = re.sub(r'[<>{}\[\]/\\*^$#@~]', '', text)
    # fix nhịp câu
    text = text.replace("...", ". ")
    text = text.replace(",", ", ")
    text = text.replace(".", ". ")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# ==============================
# CALL QWEN
# ==============================

def call_qwen(prompt, retry=3):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen/qwen3.5-122b-a10b",
        "messages": [
            {"role": "system", "content": "Bạn là MC tài chính chuyên nghiệp, viết kịch bản video ngắn cực cuốn hút, dễ đọc cho TTS."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 400
    }
    for i in range(retry):
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            if res.status_code != 200:
                raise Exception(res.text)
            data = res.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"⚠️ Qwen lỗi lần {i+1}: {e}")
            time.sleep(2 * (i+1))
    return None

# ==============================
# CALL GEMINI FALLBACK
# ==============================

def call_gemini(payload, retry=3):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    for i in range(retry):
        try:
            res = requests.post(url, json=payload, timeout=30)
            if res.status_code != 200:
                raise Exception(res.text)
            data = res.json()
            if "candidates" not in data:
                raise Exception(data)
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"⚠️ Gemini lỗi lần {i+1}: {e}")
            time.sleep(2 * (i+1))
    return None

# ==============================
# FALLBACK SCRIPT
# ==============================

def fallback_script(topic, gain_text, lose_text):
    return f"""
Dòng tiền đang xoay chiều.
Top tăng nổi bật là {gain_text}.
Nhưng phía giảm đang rất nguy hiểm.
{lose_text} đang kéo thị trường xuống.
Nhiều người đang mắc sai lầm.
Vào lệnh sai thời điểm.
Tài khoản có thể bốc hơi nhanh.
Nhưng cơ hội vẫn còn.
Ai nhanh sẽ đi trước.
"""

# ==============================
# GENERATE SCRIPT MAIN
# ==============================

def generate_script(topic):
    today = datetime.now().strftime("%d/%m/%Y")
    data = get_market_data()

    gainers = data.get("gainers", [])[:3]
    losers = data.get("losers", [])[:3]

    gain_text = ", ".join([f"{s} {v}%" for s,v in gainers]) if gainers else "Không có dữ liệu"
    lose_text = ", ".join([f"{s} {v}%" for s,v in losers]) if losers else "Không có dữ liệu"

    # ==============================
    # PROMPT OPTIMIZED
    # ==============================

    prompt = f"""
Bạn là MC bản tin tài chính TikTok.
Viết script, mỗi câu ngắn 5–10 từ.
Nhịp rõ ràng, dễ đọc cho TTS.
Mỗi câu kết thúc bằng dấu chấm.
Hook cực mạnh ngay câu đầu: cơ hội hoặc rủi ro.
Không ký tự đặc biệt, không hashtag.
Số liệu đọc dễ: 
Top tăng: {gain_text}.
Top giảm: {lose_text}.
Chủ đề: {topic}.
Nhiệm vụ của bạn là tạo bản tin thị trường cuối ngày gồm 5 phần:
1. TỔNG QUAN VNINDEX
Phân tích nhanh diễn biến chỉ số:
- Xu hướng thị trường (tăng / tích lũy / điều chỉnh)
- Độ rộng thị trường
- Thanh khoản
- Tâm lý nhà đầu tư
Giới hạn: dưới 80 từ.
2. DÒNG TIỀN THỊ TRƯỜNG
Xác định các nhóm ngành hút tiền hôm nay như:
- Ngân hàng
- Chứng khoán
- Thép
- Dầu khí
- Bất động sản
- Bán lẻ
- Công nghệ
Nêu tối đa 3 nhóm ngành nổi bật.
3. TOP 5 CỔ PHIẾU ĐÁNG CHÚ Ý
Chọn 5 cổ phiếu trong VN30 dựa trên:
- % tăng nổi bật
- khối lượng giao dịch cao
- vai trò kéo chỉ số
- tín hiệu kỹ thuật tích cực
Chỉ chọn cổ phiếu có:
- % thay đổi > 0
- thanh khoản cao
4. TÍN HIỆU KỸ THUẬT ĐÁNG CHÚ Ý
Nếu dữ liệu cho thấy:
- breakout
- tăng mạnh thanh khoản
- đảo chiều
hãy nêu ngắn gọn.
5. CHIẾN LƯỢC CHO PHIÊN TỚI
Đưa ra gợi ý chiến lược:
- nắm giữ
- quan sát
- mua khi điều chỉnh
- chốt lời
Không đưa khuyến nghị mua bán cụ thể.
Yêu cầu:
- Văn phong giống bản tin công ty chứng khoán
- Ngắn gọn, chuyên nghiệp
- Tối thiểu 200 từ tối đa không quá 250 từ tổng bài
- Không giải thích dài dòng
Định dạng output:
BẢN TIN THỊ TRƯỜNG CHỨNG KHOÁN
VNINDEX
<phân tích ngắn>
DÒNG TIỀN
<liệt kê 2–3 ngành>
TOP CỔ PHIẾU
1. Mã – lý do
2. Mã – lý do
3. Mã – lý do
4. Mã – lý do
5. Mã – lý do
TÍN HIỆU KỸ THUẬT
<ngắn>
CHIẾN LƯỢC
<ngắn>
"""

    # ==============================
    # 1. QWEN
    # ==============================

    script = call_qwen(prompt)
    if script:
        print("✅ Dùng Qwen")
        script = normalize_numbers(script)
        script = optimize_for_tts(script)
        return script

    # ==============================
    # 2. GEMINI FALLBACK
    # ==============================

    payload = {"contents":[{"parts":[{"text": prompt}]}]}
    script = call_gemini(payload)
    if script:
        print("⚠️ Fallback Gemini")
        script = normalize_numbers(script)
        script = optimize_for_tts(script)
        return script

    # ==============================
    # 3. FALLBACK HARD
    # ==============================

    print("⚠️ Dùng fallback script")
    return fallback_script(topic, gain_text, lose_text)
