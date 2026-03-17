
# ==============================
# CLONE VIRAL TOPIC
# ==============================

import requests
import os

API_KEY = os.getenv("GEMINI_API_KEY")

def generate_variations(topic):
    prompt = f"Tạo 5 biến thể viral từ topic: {topic}"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

    res = requests.post(url, json={
        "contents": [{"parts": [{"text": prompt}]}]
    })

    text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
    return [t for t in text.split("\n") if len(t) > 10]
