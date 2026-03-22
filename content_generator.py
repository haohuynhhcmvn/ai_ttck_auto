# ==============================
# GENERATE POST CONTENT
# ==============================

import requests
import os

API_KEY = os.getenv("GEMINI_API_KEY")

def generate_content(topic, script):
    if not API_KEY:
        return {
            "title": topic,
            "caption": f"{topic}\n👉 Xem ngay trước khi quá muộn!",
            "hashtags": "#chungkhoan #dautu #f0 #stock"
        }

    prompt = f"""
Bạn là chuyên gia content TikTok/YouTube Shorts.

Viết content cho video về chủ đề:
{topic}

Nội dung video:
{script}

Yêu cầu:
- Hook gây sốc (1 dòng đầu)
- Caption ngắn gọn (2-3 dòng)
- CTA kéo về Telegram
- Hashtag viral

Trả về dạng JSON:
{{
"title": "...",
"caption": "...",
"hashtags": "..."
}}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    try:
        res = requests.post(url, json={
            "contents": [{"parts": [{"text": prompt}]}]
        })

        data = res.json()

        text = data["candidates"][0]["content"]["parts"][0]["text"]

        # ⚠️ parse JSON đơn giản
        import json
        return json.loads(text)

    except Exception as e:
        print("⚠️ content AI lỗi:", e)

        return {
            "title": topic,
            "caption": f"{topic}\n👉 Link Telegram trong bio!",
            "hashtags": "#chungkhoan #stock #dautu"
        }
