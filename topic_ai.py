import requests
import os

API_KEY = os.getenv("GEMINI_API_KEY")

def generate_topics():
    if not API_KEY:
        print("❌ Missing GEMINI_API_KEY")
        return ["Tin nóng thị trường hôm nay"]

    prompt = "Tạo 10 topic viral về chứng khoán Việt Nam"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview-flash:generateContent?key={API_KEY}"

    res = requests.post(url, json={
        "contents": [{"parts": [{"text": prompt}]}]
    })

    data = res.json()

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]

        return [
            t.strip("- ").strip()
            for t in text.split("\n")
            if len(t.strip()) > 10
        ]
    except:
        print("⚠️ Gemini lỗi → fallback")

        return [
            "VNINDEX có dấu hiệu đảo chiều?",
            "Cổ phiếu bank còn cơ hội không?",
            "Sai lầm khiến bạn mất tiền",
            "Cơ hội lớn tuần này"
        ]


# 🔥 PHẢI CÓ HÀM NÀY
def pick_best_topic(topics):
    return topics[0] if topics else "Tin nóng thị trường"
