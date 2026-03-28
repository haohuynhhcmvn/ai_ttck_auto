import requests
import os

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "qwen/qwen2.5-72b-instruct"

def call_qwen(prompt):
    api_key = os.getenv("NVIDIA_API_KEY")

    if not api_key:
        raise ValueError("Missing NVIDIA_API_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Bạn là MC tài chính, viết ngắn gọn, hấp dẫn, dễ đọc cho TTS."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    res = requests.post(API_URL, headers=headers, json=payload)

    if res.status_code != 200:
        raise Exception(res.text)

    return res.json()["choices"][0]["message"]["content"]
