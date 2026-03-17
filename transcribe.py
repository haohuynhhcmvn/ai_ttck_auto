
# ==============================
# WHISPER TRANSCRIBE
# ==============================

import whisper

def transcribe(audio):
    model = whisper.load_model("tiny")
    result = model.transcribe(audio, word_timestamps=True)

    words = []
    for seg in result["segments"]:
        for w in seg["words"]:
            words.append(w)

    return words
