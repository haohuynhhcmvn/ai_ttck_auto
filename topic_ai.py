
# ==============================
# GENERATE TRENDING TOPICS
# ==============================

import requests
import os

API_KEY = os.getenv("GEMINI_API_KEY")


def generate_topics():
    
    if not API_KEY:
    print("❌ Missing GEMINI_API_KEY")
    return ["Tin nóng thị trường hôm nay"]
    
    prompt = "Tạo 10 topic viral về chứng khoán Việt Nam"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

    res = requests.post(url, json={
        "contents": [{"parts": [{"text": prompt}]}]
    })

    data = res.json()

    # DEBUG nếu lỗi
    print("GEMINI RESPONSE:", data)

    try:
        return [
            t for t in data["candidates"][0]["content"]["parts"][0]["text"].split("\n")
            if len(t) > 10
        ]
    except:
        print("⚠️ Gemini lỗi → fallback topic")

        return [
            "VNINDEX có dấu hiệu đảo chiều?",
            "Cổ phiếu bank có còn cơ hội?",
            "Sai lầm khiến bạn mất tiền",
            "Cơ hội lớn tuần này"
        ]
