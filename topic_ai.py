import requests
import os
import time

# ==============================
# API KEYS
# ==============================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")


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
                "content": """
Bạn là chuyên gia sáng tạo nội dung TikTok tài chính.

Nhiệm vụ:
- Tạo topic gây tò mò cực mạnh
- Khiến người xem phải click ngay
- Ngắn gọn, sắc bén
"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.9,
        "max_tokens": 200
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

def call_gemini(prompt, retry=3):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    for i in range(retry):
        try:
            res = requests.post(url, json=payload, timeout=30)

            if res.status_code != 200:
                raise Exception(res.text)

            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

        except Exception as e:
            print(f"⚠️ Gemini lỗi lần {i+1}: {e}")
            time.sleep(2 * (i + 1))

    return None


# ==============================
# CLEAN OUTPUT
# ==============================

def clean_topics(text):
    lines = text.split("\n")

    topics = []
    for line in lines:
        t = line.strip("- ").strip()
        if len(t) > 10:
            topics.append(t)

    return topics[:5]  # giới hạn tối đa 5 topic


# ==============================
# MAIN GENERATE TOPICS
# ==============================

def generate_topics():
    prompt = """
Tạo 5 topic video TikTok về chứng khoán Việt Nam:

YÊU CẦU:
- Hook mạnh
- Gây tò mò
- Có yếu tố sợ mất tiền hoặc cơ hội lớn
- Ngắn gọn dưới 12 từ
- Không ký hiệu đặc biệt

Chỉ trả về danh sách, mỗi dòng 1 topic
"""

    # ==============================
    # 1. ƯU TIÊN QWEN
    # ==============================

    if NVIDIA_API_KEY:
        text = call_qwen(prompt)

        if text:
            print("✅ Topics từ Qwen")
            topics = clean_topics(text)

            if topics:
                return topics

    # ==============================
    # 2. FALLBACK GEMINI
    # ==============================

    if GEMINI_API_KEY:
        text = call_gemini(prompt)

        if text:
            print("⚠️ Topics từ Gemini")
            topics = clean_topics(text)

            if topics:
                return topics

    # ==============================
    # 3. FALLBACK CỨNG
    # ==============================

    print("⚠️ Dùng fallback topics")

    return [
        "VN-Index sắp đảo chiều?",
        "Dòng tiền lớn đang vào đâu?",
        "Sai lầm khiến bạn mất tiền",
        "Cổ phiếu này chuẩn bị bùng nổ?",
        "Cơ hội lớn tuần này"
    ]


# ==============================
# PICK BEST
# ==============================

def pick_best_topic(topics):
    return topics[0] if topics else "Tin nóng thị trường"
