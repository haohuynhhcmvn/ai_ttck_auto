# ==============================
# GENERATE SCRIPT (NO INDEX - QWEN PRIORITY)
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

    gainers = data.get("gainers", [])[:3]
    losers = data.get("losers", [])[:3]

    gain_text = ", ".join([f"{s} {v}%" for s, v in gainers]) if gainers else "Không có dữ liệu"
    lose_text = ", ".join([f"{s} {v}%" for s, v in losers]) if losers else "Không có dữ liệu"

    # ==============================
    # PROMPT (CLEAN - KHÔNG INDEX)
    # ==============================

    prompt = f"""
Bạn là MC bản tin tài chính TikTok.

DỮ LIỆU THỊ TRƯỜNG:

Top tăng: {gain_text}
Top giảm: {lose_text}

YÊU CẦU:

- Hook cực mạnh ngay câu đầu
- Gây cảm giác:
  + Sắp mất tiền
  + Hoặc cơ hội lớn
- Câu rất ngắn (5–10 từ)
- Mỗi câu ngắt bằng dấu ...
- Không ký hiệu đặc biệt
- Không hashtag
- Không bịa số liệu

QUY TẮC TTS:

- Viết để đọc mượt
- Nhịp rõ ràng
- Không câu dài
- Số dễ đọc

ĐỘ DÀI:
50–60 chữ

OUTPUT:
Chỉ nội dung script

CHỦ ĐỀ:
{topic}
"""

    # ==============================
    # 1. QWEN
    # ==============================

    script = call_qwen(prompt)

    if script:
        print("✅ Dùng Qwen")
        return optimize_for_tts(script.strip())

    # ==============================
    # 2. GEMINI FALLBACK
    # ==============================

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    script = call_gemini(payload)

    if script:
        print("⚠️ Fallback Gemini")
        return optimize_for_tts(script.strip())

    # ==============================
    # 3. FALLBACK HARD
    # ==============================

    return fallback_script(topic, gain_text, lose_text)


# ==============================
# FALLBACK
# ==============================

def fallback_script(topic, gain_text, lose_text):
    print("⚠️ Dùng fallback script")

    return f"""
Dòng tiền đang xoay chiều...

Top tăng nổi bật là {gain_text}...

Nhưng phía giảm đang rất nguy hiểm...

{lose_text} đang kéo thị trường xuống...

Nhiều người đang mắc sai lầm...

Vào lệnh sai thời điểm...

Tài khoản có thể bốc hơi nhanh...

Nhưng cơ hội vẫn còn...

Ai nhanh sẽ đi trước...
"""
