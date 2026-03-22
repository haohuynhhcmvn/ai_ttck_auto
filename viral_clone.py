
# ==============================
# CLONE VIRAL TOPIC
# ==============================

import requests
import os

API_KEY = os.getenv("GEMINI_API_KEY")

def generate_variations(topic):
    prompt = f"Tạo 1 biến thể viral từ topic: {topic}"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    res = requests.post(url, json={
        "contents": [{"parts": [{"text": prompt}]}]
    })

    text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
    return [
    t.strip("- ").strip()
    for t in text.split("\n")
    if len(t.strip()) > 10 and "Tuyệt vời" not in t
    ]
