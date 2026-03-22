
# ==============================
# GENERATE SCRIPT USING GEMINI
# ==============================

import requests
import os

API_KEY = os.getenv("GEMINI_API_KEY")

def generate_script(topic):
    prompt = f"""
Viết kịch bản video TikTok 30s về:
{topic}

Yêu cầu:
- Hook gây sốc
- Nội dung ngắn gọn
- Có CTA
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash:generateContent?key={API_KEY}"

    res = requests.post(url, json={
        "contents": [{"parts": [{"text": prompt}]}]
    })

    return res.json()["candidates"][0]["content"]["parts"][0]["text"]
