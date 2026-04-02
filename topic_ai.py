import requests
import os
import time
import random

# ==============================
# CONFIG & API KEYS
# ==============================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# Cập nhật model name chính xác cho Gemini (thường là 1.5 hoặc 2.0 flash)
GEMINI_MODEL = "gemini-1.5-flash" 
QWEN_MODEL = "qwen/qwen3.5-122b-a10b"

# ==============================
# DYNAMIC TOPIC ANGLES (Bí kíp chống nhàm chán)
# ==============================
TOPIC_ANGLES = [
    {
        "name": "Tâm lý đám đông",
        "focus": "Bẫy tâm lý, FOMO, nỗi sợ, sự thật ngầm hiểu về hành vi nhà đầu tư cá nhân.",
        "example": "Tại sao bạn luôn mua đúng đỉnh và bán đúng đáy?"
    },
    {
        "name": "Dòng tiền thông minh",
        "focus": "Cách 'Cá mập' vận hành, dấu vết dòng tiền lớn, sự thao túng và bẫy thanh khoản.",
        "example": "Dấu hiệu nhận biết dòng tiền lớn đang âm thầm rút lui."
    },
    {
        "name": "Tư duy ngược (Contrarian)",
        "focus": "Đi ngược lại số đông, những góc nhìn ít người dám nói, cảnh báo khi thị trường hưng phấn.",
        "example": "Lý do bạn nên đứng ngoài khi cả thế giới đang hô hào múc."
    },
    {
        "name": "Quản trị rủi ro & Bài học",
        "focus": "Sai lầm xương máu, cách giữ tiền, quy tắc cắt lỗ, quản lý vốn của dân chuyên nghiệp.",
        "example": "Sai lầm chí mạng khiến 90 phần trăm tài khoản cháy sạch."
    }
]

# ==============================
# CALL QWEN (PRIORITY)
# ==============================
def call_qwen(prompt, retry=3):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": QWEN_MODEL,
        "messages": [
            {
                "role": "system", 
                "content": "Bạn là Creative Director cho kênh TikTok tài chính triệu view. Chuyên gia tạo Hook tiêu đề gây sốc nhưng an toàn chính sách."
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.95, # Tăng sáng tạo để tiêu đề không bị lặp
        "max_tokens": 300
    }

    for i in range(retry):
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            print(f"⚠️ Qwen lỗi HTTP {res.status_code}")
        except Exception as e:
            print(f"⚠️ Qwen lỗi lần {i+1}: {e}")
            time.sleep(2 * (i + 1))
    return None

# ==============================
# CALL GEMINI (FALLBACK)
# ==============================
def call_gemini(prompt, retry=3):
    # Sử dụng v1beta cho các tính năng mới nhất
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    for i in range(retry):
        try:
            res = requests.post(url, json=payload, timeout=30)
            if res.status_code == 200:
                return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"⚠️ Gemini lỗi lần {i+1}: {e}")
            time.sleep(2 * (i + 1))
    return None

# ==============================
# CLEAN OUTPUT
# ==============================
def clean_topics(text):
    if not text: return []
    # Loại bỏ các dấu gạch đầu dòng, số thứ tự và khoảng trắng thừa
    lines = text.replace("*", "").replace("\"", "").split("\n")
    topics = []
    for line in lines:
        t = re.sub(r'^\d+[\.\)]\s*', '', line).strip("- ").strip()
        if 10 < len(t) < 100: # Loại bỏ các dòng quá ngắn hoặc quá dài (rác)
            topics.append(t)
    return topics[:5]

# ==============================
# MAIN GENERATE TOPICS
# ==============================
import re

def generate_topics():
    # CHỌN NGẪU NHIÊN 1 CHIẾN THUẬT NỘI DUNG CHO NGÀY HÔM NAY
    angle = random.choice(TOPIC_ANGLES)
    print(f"🎯 Chiến thuật nội dung hôm nay: {angle['name']}")

    prompt = f"""
Nhiệm vụ: Tạo 5 tiêu đề video TikTok (Topic) về chứng khoán Việt Nam.
Góc nhìn chủ đạo: {angle['focus']}
Ví dụ hướng đi: {angle['example']}

QUY TẮC NÉ VI PHẠM (BẮT BUỘC):
- KHÔNG dùng: Cam kết, chắc chắn, làm giàu, kiếm tiền nhanh, phím kèo, múc, xúc, x tài khoản.
- KHÔNG dùng ký tự đặc biệt (@, #, $, %, con số phần trăm). 
- Dùng từ thay thế: Thay 'lãi' bằng 'hiệu suất', thay 'mất tiền' bằng 'bào mòn vốn'.

YÊU CẦU ĐỊNH DẠNG:
- Hook cực mạnh, đánh vào sự tò mò hoặc 'nỗi đau' của nhà đầu tư.
- Độ dài: Dưới 12 từ.
- Mỗi dòng 1 topic, không số thứ tự, không giải thích thêm.
"""

    # 1. ƯU TIÊN QWEN
    if NVIDIA_API_KEY:
        print("📡 Đang lấy Topic từ Qwen...")
        text = call_qwen(prompt)
        topics = clean_topics(text)
        if topics: return topics

    # 2. FALLBACK GEMINI
    if GEMINI_API_KEY:
        print("📡 Đang lấy Topic từ Gemini...")
        text = call_gemini(prompt)
        topics = clean_topics(text)
        if topics: return topics

    # 3. FALLBACK CỨNG (Luôn chuẩn bị sẵn phòng khi API sập)
    print("⚠️ Dùng fallback topics cố định")
    return [
        "Tại sao đám đông luôn sai ở vùng đỉnh",
        "Sự thật ngầm hiểu về dòng tiền lớn",
        "Cách quản trị vốn của nhà đầu tư chuyên nghiệp",
        "Bẫy tâm lý FOMO khiến bạn dễ mất tiền",
        "Tư duy ngược để tồn tại trên thị trường"
    ]

def pick_best_topic(topics):
    # Thay vì luôn lấy cái đầu tiên, hãy lấy ngẫu nhiên để tăng tính biến thiên
    if not topics: return "Nhận định thị trường chứng khoán hôm nay"
    return random.choice(topics)

# --- TEST ---
if __name__ == "__main__":
    ts = generate_topics()
    for idx, t in enumerate(ts):
        print(f"{idx+1}. {t}")
    print(f"\n👉 Topic được chọn: {pick_best_topic(ts)}")
