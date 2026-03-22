
# ==============================
# CLONE VIRAL TOPIC
# ==============================

import requests
import os

# API_KEY = os.getenv("GEMINI_API_KEY")

def generate_variations_local(topic):
    return [
        topic,
        f"{topic} - cơ hội lớn",
        f"{topic} - cảnh báo quan trọng",
        f"{topic} - điều ít ai biết",
        f"{topic} - sai lầm nhiều người mắc"
    ]
