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

RATE = "+20%"
PITCH = "+5Hz"

# ==============================
# NUMBER NORMALIZATION
# ==============================

def read_decimal(num_str):
    integer, decimal = num_str.split(".")
    
    int_part = num2words(int(integer), lang='vi')
    
    # đọc tự nhiên hơn: nhóm 2 số nếu dài
    if len(decimal) >= 2:
        groups = [decimal[i:i+2] for i in range(0, len(decimal), 2)]
        dec_part = " ".join([num2words(int(g), lang='vi') for g in groups])
    else:
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
    # % (phần trăm)
    text = re.sub(r'(\d+(\.\d+)?)%', 
                  lambda m: convert_number(m) + " phần trăm", 
                  text)
    
    # số có dấu phẩy (1,000,000)
    text = re.sub(r'(\d{1,3}(,\d{3})+)', 
                  lambda m: num2words(int(m.group().replace(",", "")), lang='vi'), 
                  text)
    
    # số thường
    text = re.sub(r'\d+(\.\d+)?', convert_number, text)
    
    return text


# ==============================
# TEXT CLEANING (TỐI ƯU GIỌNG ĐỌC)
# ==============================

def normalize_text(text):
    text = normalize_numbers(text)
    
    # đọc ký hiệu tài chính phổ biến
    text = text.replace("VN-Index", "Vi En Index")
    text = text.replace("HNX-Index", "Hát En Xờ Index")
    text = text.replace("UPCOM", "Up Com")
    
    # pause tự nhiên
    text = text.replace(",", ", <break time='200ms'/>")
    text = text.replace(".", ". <break time='400ms'/>")
    
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
    
    communicate = edge_tts.Communicate(
        ssml,
        voice=voice
    )
    
    await communicate.save(filename)


# ==============================
# MAIN FUNCTION (PIPELINE ENTRY)
# ==============================

def text_to_speech(text, voice=None):
    """
    INPUT: raw text
    OUTPUT: mp3 file path
    """
    
    # 1. normalize text
    text = normalize_text(text)
    
    # 2. chọn giọng (A/B test)
    if not voice:
        voice = random.choice(VOICES)
    
    # 3. tạo filename unique
    filename = f"voice_{uuid.uuid4().hex}.mp3"
    
    # 4. run async (safe cho mọi môi trường)
    try:
        asyncio.run(tts_async(text, filename, voice))
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(tts_async(text, filename, voice))
    
    return filename


# ==============================
# TEST
# ==============================

if __name__ == "__main__":
    sample = "NVL tăng 2.35% lên 12,500 đồng. VN-Index đạt 1234.56 điểm"
    file = text_to_speech(sample)
    print("Generated:", file)
