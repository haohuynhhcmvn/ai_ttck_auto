# ==============================
# TTS PRO MAX (STABLE + CLEAN)
# ==============================

import edge_tts
import asyncio
import uuid
import re
from num2words import num2words
import random

VOICES = [
    "vi-VN-HoaiMyNeural",
    "vi-VN-NamMinhNeural"
]

RATE = "+12%"
PITCH = "+0Hz"

_loop = None


# ==============================
# EVENT LOOP
# ==============================
def get_loop():
    global _loop
    if _loop is None:
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop


# ==============================
# CLEAN TEXT (QUAN TRỌNG NHẤT)
# ==============================
def clean_text(text):
    # bỏ ký tự rác
    text = re.sub(r"[^\w\s.,%]", "", text)

    # bỏ dấu ... dư
    text = re.sub(r"\.{2,}", ".", text)

    # bỏ nhiều space
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==============================
# NUMBER NORMALIZATION
# ==============================
def read_decimal(num_str):
    integer, decimal = num_str.split(".")
    return f"{num2words(int(integer), lang='vi')} phẩy {' '.join(num2words(int(d), lang='vi') for d in decimal)}"


def convert_number(match):
    num = match.group()
    try:
        if "." in num:
            return read_decimal(num)
        return num2words(int(num), lang='vi')
    except:
        return num


def normalize_numbers(text):
    text = re.sub(r'(\d+(\.\d+)?)%',
                  lambda m: convert_number(m) + " phần trăm",
                  text)

    text = re.sub(r'(\d{1,3}(,\d{3})+)',
                  lambda m: num2words(int(m.group().replace(",", "")), lang='vi'),
                  text)

    text = re.sub(r'\d+(\.\d+)?', convert_number, text)

    return text


# ==============================
# FINANCIAL TEXT FIX
# ==============================
def normalize_finance(text):
    text = text.replace("VN-Index", "vi en index")
    text = text.replace("HNX-Index", "hát en xờ index")
    text = text.replace("UPCOM", "úp com")
    return text


# ==============================
# ADD PAUSE (NHẸ)
# ==============================
def add_pause(text):
    text = text.replace(".", ". <break time='400ms'/>")
    text = text.replace(",", ", <break time='200ms'/>")
    return text


# ==============================
# FINAL NORMALIZE
# ==============================
def normalize_text(text):
    text = clean_text(text)
    text = normalize_finance(text)
    text = normalize_numbers(text)
    text = add_pause(text)
    return text


# ==============================
# BUILD SSML
# ==============================
def build_ssml(text, voice):
    return f"""
<speak version="1.0" xml:lang="vi-VN">
    <voice name="{voice}">
        <prosody rate="{RATE}" pitch="{PITCH}">
            {text}
        </prosody>
    </voice>
</speak>
"""


# ==============================
# TTS CORE
# ==============================
async def tts_async(text, filename, voice):
    ssml = build_ssml(text, voice)

    # 🔥 KHÔNG truyền voice ở đây nữa
    communicate = edge_tts.Communicate(ssml)

    await communicate.save(filename)


# ==============================
# MAIN
# ==============================
def text_to_speech(text, voice=None):
    text = normalize_text(text)

    if not voice:
        voice = random.choice(VOICES)

    filename = f"voice_{uuid.uuid4().hex}.mp3"

    loop = get_loop()
    loop.run_until_complete(tts_async(text, filename, voice))

    return filename
