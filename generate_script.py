# ==============================
# GENERATE SCRIPT (FINAL PRO - QWEN PRIORITY)
# ==============================

import requests
import os
import time
from datetime import datetime
from market_data import get_market_data

# ==============================
# API KEYS
# ==============================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# ==============================
# CLEAN TEXT FOR TTS
# ==============================

def optimize_for_tts(text):
    text = text.replace("VNINDEX", "VN-Index")
    text = text.replace(",", "...")
    text = text.replace(".", "...")
    return text


# ==============================
# CALL QWEN (PRIORITY)
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
            {
                "role": "system",
                "content": "Bạn là MC tài chính chuyên nghiệp, viết kịch bản video ngắn cực cuốn hút, dễ đọc cho TTS."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 600
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
            time.sleep(2 * (i + 1))

    return None


# ==============================
# CALL GEMINI (FALLBACK)
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
            time.sleep(2 * (i + 1))

    return None


# ==============================
# MAIN GENERATE SCRIPT
# ==============================

def generate_script(topic):
    today = datetime.now().strftime("%d/%m/%Y")

    # 🔥 DATA THẬT
    data = get_market_data()

    vn = data.get("vnindex", {})
    vn30 = data.get("vn30", {})
    gainers = data.get("gainers", [])[:3]
    losers = data.get("losers", [])[:3]

    # ==============================
    # BUILD DATA TEXT
    # ==============================

    if vn.get("close") != "N/A":
        vn_text = f"""
VN-Index: {vn.get('close')} điểm...
Biến động: {vn.get('change')} điểm...
"""
    else:
        vn_text = "Chưa có dữ liệu VN-Index..."

    if vn30.get("close") != "N/A":
        vn30_text = f"VN30: {vn30.get('close')} điểm..."
    else:
        vn30_text = ""

    gain_text = ", ".join([f"{s} {v}%" for s, v in gainers]) if gainers else ""
    lose_text = ", ".join([f"{s} {v}%" for s, v in losers]) if losers else ""

    # ==============================
    # PROMPT
    # ==============================

    prompt = f"""
Bạn là MC bản tin tài chính trên TikTok.

NHIỆM VỤ:
Viết kịch bản video ngắn cực cuốn hút, giữ người xem đến cuối.

DỮ LIỆU THỊ TRƯỜNG:
{vn_text}
{vn30_text}

Top tăng: {gain_text}
Top giảm: {lose_text}

YÊU CẦU BẮT BUỘC:

1. Hook cực mạnh trong câu đầu tiên
2. Tạo cảm giác:
   - Sắp mất tiền
   - Hoặc sắp có cơ hội lớn
3. Câu rất ngắn (5–10 từ)
4. Mỗi câu xuống dòng bằng dấu ba chấm ...
5. Không dùng ký hiệu đặc biệt
6. Không hashtag
7. Không giải thích dài dòng
8. Không bịa số liệu

QUY TẮC TTS (RẤT QUAN TRỌNG):

- Viết để AI đọc mượt, không bị vấp
- Tránh dấu câu phức tạp
- Có nhịp nghỉ tự nhiên
- Không viết câu quá dài
- Số viết dạng dễ đọc:
  ví dụ 1.5 → một phẩy năm

ĐỘ DÀI:
200 đến 250 chữ

FORMAT OUTPUT:

- Chỉ trả về nội dung kịch bản
- Không tiêu đề
- Không giải thích
- Mỗi câu cách nhau bằng ...

CHỦ ĐỀ:
{topic}
"""

    # ==============================
    # 1. ƯU TIÊN QWEN
    # ==============================

    script = call_qwen(prompt)

    if script:
        print("✅ Dùng Qwen")
        return optimize_for_tts(script.strip())

    # ==============================
    # 2. FALLBACK GEMINI
    # ==============================

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    script = call_gemini(payload)

    if script:
        print("⚠️ Fallback Gemini")
        return optimize_for_tts(script.strip())

    # ==============================
    # 3. FALLBACK CỨNG
    # ==============================

    return fallback_script(topic, vn_text)


# ==============================
# FALLBACK (NO AI)
# ==============================

def fallback_script(topic, vn_text):
    print("⚠️ Dùng fallback script")

    return f"""
90% nhà đầu tư đang hiểu sai thị trường...

{vn_text}

Dòng tiền đang dịch chuyển âm thầm...

Top cổ phiếu bắt đầu phân hóa mạnh...

Nếu bạn vào sai nhịp...

Tài khoản sẽ bốc hơi rất nhanh...

Nhưng nếu hiểu đúng dòng tiền...

Cơ hội vẫn còn phía trước...

Ai hiểu sẽ hành động sớm...
"""
