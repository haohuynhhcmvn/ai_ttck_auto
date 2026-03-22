
# ==============================
# TEXT TO SPEECH (EDGE TTS)
# ==============================

import edge_tts
import asyncio

# ==============================
# TEXT TO SPEECH (EDGE TTS UPDATED)
# ==============================

async def tts(text):
    # Cấu hình giọng đọc:
    # rate="+25%": Đọc nhanh hơn 25% để tạo sự dồn dập của bản tin.
    # pitch="+5Hz": Tăng độ cao một chút để giọng sắc sảo, chuyên nghiệp hơn.
    # volume="+0%": Giữ nguyên âm lượng mặc định.
    
    voice = "vi-VN-HoaiMyNeural"
    rate = "+25%" 
    pitch = "+5Hz"
    
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save("voice.mp3")

def text_to_speech(text):
    # Xử lý chạy async trong môi trường đồng bộ
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(tts(text))
    return "voice.mp3"
