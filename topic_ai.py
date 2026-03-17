
# ==============================
# GENERATE TRENDING TOPICS
# ==============================

import requests
import os

API_KEY = os.getenv("GEMINI_API_KEY")

def generate_topics():
    prompt = "Tạo 10 topic viral về chứng khoán Việt Nam"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

    res = requests.post(url, json={
        "contents": [{"parts": [{"text": prompt}]}]
    })

    text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
    return [t for t in text.split("\n") if len(t) > 10]

def pick_best_topic(topics):
    return topics[0]
