
# ==============================
# CLONE VIRAL TOPIC
# ==============================

import requests
import os

API_KEY = os.getenv("GEMINI_API_KEY")

def generate_variations(topic):
    if not API_KEY:
        print("❌ Missing GEMINI_API_KEY")
        return [topic]

    prompt = f"""
Tạo 5 biến thể viral từ topic:
{topic}

Yêu cầu:
- mỗi dòng 1 câu
- ngắn gọn
- gây tò mò
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    try:
        res = requests.post(url, json={
            "contents": [{"parts": [{"text": prompt}]}]
        })

        data = res.json()

        print("DEBUG CLONE:", data)

        text = data["candidates"][0]["content"]["parts"][0]["text"]

        return [
            t.strip("- ").strip()
            for t in text.split("\n")
            if len(t.strip()) > 10
        ]

    except Exception as e:
        print("⚠️ Gemini clone lỗi:", e)

        # fallback cực quan trọng
        return [
            topic,
            f"{topic} - cơ hội lớn",
            f"{topic} - cảnh báo quan trọng",
            f"{topic} - điều bạn chưa biết",
            f"{topic} - sai lầm nhiều người mắc"
        ]
