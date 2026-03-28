# ==============================
# TEXT UTILITIES (SAVE + CLEAN)
# ==============================

import os
import re
from datetime import datetime


# ==============================
# SAVE TEXT
# ==============================
def save_text(text, prefix="script"):
    os.makedirs("logs", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"logs/{prefix}_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"💾 Saved: {filename}")
    return filename


# ==============================
# CLEAN TEXT FOR TTS (PRO)
# ==============================
def clean_text_for_tts(text):
    # 🔥 chuẩn hóa unicode
    text = text.strip()

    # ==========================
    # FIX NUMBER (QUAN TRỌNG)
    # ==========================
    text = text.replace(".", " phẩy ")
    text = text.replace(",", " ")

    # ví dụ: 1 234 → 1234
    text = re.sub(r"(\d)\s+(\d)", r"\1\2", text)

    # ==========================
    # FIX KÝ HIỆU
    # ==========================
    text = text.replace("%", " phần trăm")
    text = text.replace("+", " tăng ")
    text = text.replace("-", " giảm ")

    # ==========================
    # FIX NGẮT CÂU
    # ==========================
    text = text.replace("...", ". ")
    text = text.replace("..", ". ")

    # ==========================
    # XÓA KHOẢNG TRẮNG THỪA
    # ==========================
    text = re.sub(r"\s+", " ", text)

    return text.strip()
