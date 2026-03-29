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
Bạn là chuyên gia sáng tạo nội dung TikTok tài chính chuyên nghiệp, am hiểu thuật toán kiểm duyệt.
Nhiệm vụ: 
- Tạo topic dựa trên 'Insight' (Sự thật ngầm hiểu) và 'Cảnh báo rủi ro'.
- Tuyệt đối không dùng từ hứa hẹn lợi nhuận, cam kết, hoặc lôi kéo đầu tư.
- Tập trung vào: Bẫy tâm lý, sai lầm phổ biến, kinh nghiệm quản trị vốn.
- Ngôn ngữ: Sắc bén, ngắn gọn, gây tò mò nhưng an toàn chính sách.
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
Nhiệm vụ: Tạo 5 topic video TikTok về chứng khoán Việt Nam.

CHIẾN THUẬT NÉ VI PHẠM (QUAN TRỌNG):
- KHÔNG dùng từ: Cam kết, chắc chắn, làm giàu, kiếm tiền nhanh, phím kèo, múc, xúc, lãi XX%.
- DÙNG các hướng: Cảnh báo rủi ro, bẫy tâm lý, bài học xương máu, sự thật ngầm hiểu, tư duy ngược.
- Thay vì "Kiếm tiền", hãy dùng "Quản trị vốn" hoặc "Tối ưu hiệu suất".

YÊU CẦU ĐỊNH DẠNG:
- Hook cực mạnh, đánh vào sự tò mò hoặc nỗi sợ mất tiền.
- Ngắn gọn dưới 12 từ.
- Không dùng ký hiệu đặc biệt (như @, #, $, %).
- Chỉ trả về danh sách, mỗi dòng 1 topic, không đánh số.

VÍ DỤ MẪU:
- Tại sao 90% nhà đầu tư mất tiền tháng này
- Sự thật về dòng tiền lớn ít người kể
- Bẫy tâm lý vùng đỉnh bạn cần tránh
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
