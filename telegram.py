
# ==============================
# TELEGRAM BOT
# ==============================

import requests
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_message(text):
    res = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"   # 🔥 hỗ trợ format đẹp
        }
    )
    print("📩 send_message:", res.text)

# 🔥 FIX CHUẨN
def send_video(file):
    if not os.path.exists(file):
        print("❌ File không tồn tại:", file)
        return

    size = os.path.getsize(file) / (1024 * 1024)
    print(f"📦 Video size: {size:.2f} MB")

    try:
        with open(file, "rb") as f:
            res = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
                data={"chat_id": CHAT_ID},
                files={"video": ("video.mp4", f, "video/mp4")},
                timeout=120
            )

        print("📡 Telegram response:", res.text)

    except Exception as e:
        print("❌ Lỗi gửi video:", e)
