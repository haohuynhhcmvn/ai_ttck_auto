
# ==============================
# TELEGRAM BOT
# ==============================

import requests
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_message(text):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text}
    )

# 🔥 THÊM HÀM NÀY
def send_video(file):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
        files={"video": open(file, "rb")},
        data={"chat_id": CHAT_ID}
    )
