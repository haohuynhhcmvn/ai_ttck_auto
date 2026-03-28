# ==============================
# TTS PRO MAX (SMOOTH + FAST)
# ==============================

import edge_tts
import asyncio
import uuid
import re
from num2words import num2words
import random

# ==============================
# CONFIG
# ==============================

VOICES = [
    "vi-VN-HoaiMyNeural",
    "vi-VN-NamMinhNeural"
]

RATE = "+15%"     # 🔥 giảm nhẹ cho tự nhiên hơn
PITCH = "+2Hz"

_loop = None  # 🔥 cache event loop


# ==============================
# GET EVENT LOOP (FAST)
# ==============================
def get_loop():
    global _loop
    if _loop is None:
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop


# ==============================
# NUMBER NORMALIZATION (TỰ NHIÊN)
# ==============================

def read_decimal(num_str):
    integer, decimal = num_str.split(".")
    
    int_part = num2words(int(integer), lang='vi')
    
    # đọc từng số → tự nhiên hơn
    dec_part = " ".join([num2words(int(d), lang='vi') for d in decimal])
    
    return f"{int_part} phẩy {dec_part}"


def convert_number(match):
    num = match.group()
    
    try:
        if "." in num:
            return read_decimal(num)
        return num2words(int(num), lang='vi')
    except:
        return num


def normalize_numbers(text):
    # %
    text = re.sub(r'(\d+(\.\d+)?)%',
                  lambda m: convert_number(m) + " phần trăm",
                  text)

    # 1,000,000
    text = re.sub(r'(\d{1,3}(,\d{3})+)',
                  lambda m: num2words(int(m.group().replace(",", "")), lang='vi'),
                  text)

    # số thường
    text = re.sub(r'\d+(\.\d+)?', convert_number, text)

    return text


# ==============================
# TEXT CLEANING (TTS FRIENDLY)
# ==============================

def normalize_text(text):
    text = normalize_numbers(text)

    # tài chính
    text = text.replace("VN-Index", "vi en index")
    text = text.replace("HNX-Index", "hát en xờ index")
    text = text.replace("UPCOM", "úp com")

    # 🔥 nhịp đọc tự nhiên hơn
    text = text.replace(",", " <break time='250ms'/> ")
    text = text.replace(".", " <break time='500ms'/> ")

    return text.strip()


# ==============================
# BUILD SSML (NATURAL)
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

    communicate = edge_tts.Communicate(
        ssml,
        voice=voice
    )

    await communicate.save(filename)


# ==============================
# MAIN FUNCTION
# ==============================

def text_to_speech(text, voice=None):
    text = normalize_text(text)

    # 🔥 chọn giọng ổn định (có thể fix để A/B test)
    if not voice:
        voice = random.choice(VOICES)

    filename = f"voice_{uuid.uuid4().hex}.mp3"

    loop = get_loop()
    loop.run_until_complete(tts_async(text, filename, voice))

    return filename
