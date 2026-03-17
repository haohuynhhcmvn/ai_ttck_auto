
# ==============================
# TEXT TO SPEECH (EDGE TTS)
# ==============================

import edge_tts
import asyncio

async def tts(text):
    communicate = edge_tts.Communicate(text, "vi-VN-HoaiMyNeural")
    await communicate.save("voice.mp3")

def text_to_speech(text):
    asyncio.run(tts(text))
    return "voice.mp3"
