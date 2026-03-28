# ==============================
# TTS PRO STABLE (NO SSML BUG)
# ==============================

import edge_tts
import asyncio
import uuid
import re
import random
from num2words import num2words

# ==============================
# CONFIG
# ==============================

VOICES = {
    "female": "vi-VN-HoaiMyNeural",
    "male": "vi-VN-NamMinhNeural"
}

RATE = "+10%"
PITCH = "-5Hz"
VOLUME = "+30%"   # 🔥 giống Colab → âm rõ hơn

_loop = None


# ==============================
# EVENT LOOP (GITHUB SAFE)
# ==============================

def get_loop():
    global _loop
    if _loop is None:
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop


# ==============================
# NUMBER NORMALIZATION
# ==============================

def read_decimal(num_str):
    integer, decimal = num_str.split(".")
    int_part = num2words(int(integer), lang="vi")

    # đọc từng số cho tự nhiên
    dec_part = " ".join(num2words(int(d), lang="vi") for d in decimal)

    return f"{int_part} phẩy {dec_part}"


def convert_number(match):
    num = match.group()
    try:
        if "." in num:
            return read_decimal(num)
        return num2words(int(num), lang="vi")
    except:
        return num


def normalize_numbers(text):
    # %
    text = re.sub(
        r'(\d+(\.\d+)?)%',
        lambda m: convert_number(m) + " phần trăm",
        text
    )

    # 1,000,000
    text = re.sub(
        r'(\d{1,3}(,\d{3})+)',
        lambda m: num2words(int(m.group().replace(",", "")), lang="vi"),
        text
    )

    # số thường
    text = re.sub(r'\d+(\.\d+)?', convert_number, text)

    return text


# ==============================
# CLEAN TEXT (QUAN TRỌNG NHẤT)
# ==============================

def clean_text(text):
    text = normalize_numbers(text)

    # tài chính
    text = text.replace("VN-Index", "vi en index")
    text = text.replace("HNX-Index", "hát en xờ index")
    text = text.replace("UPCOM", "úp com")

    # 🔥 loại bỏ ký tự nguy hiểm
    text = re.sub(r'[<>{}]', '', text)

    # 🔥 pause bằng dấu câu (KHÔNG dùng SSML)
    text = text.replace("...", ". ")
    text = text.replace(",", ", ")
    text = text.replace(".", ". ")

    # fix spacing
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# ==============================
# TTS CORE (KHÔNG SSML)
# ==============================

async def tts_async(text, filename, voice):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=RATE,
        pitch=PITCH,
        volume=VOLUME
    )

    await communicate.save(filename)


# ==============================
# MAIN FUNCTION
# ==============================

def text_to_speech(text, voice=None):
    """
    INPUT: text
    OUTPUT: mp3 path
    """

    # 🔥 clean chuẩn
    text = clean_text(text)

    # 🔥 chọn giọng random (A/B test)
    if not voice:
        voice = random.choice(list(VOICES.values()))

    filename = f"voice_{uuid.uuid4().hex}.mp3"

    loop = get_loop()
    loop.run_until_complete(tts_async(text, filename, voice))

    return filename


# ==============================
# TEST
# ==============================

if __name__ == "__main__":
    sample = "NVL tăng 2.35% lên 12,500 đồng. VN-Index đạt 1234.56 điểm"
    file = text_to_speech(sample)
    print("Generated:", file)
