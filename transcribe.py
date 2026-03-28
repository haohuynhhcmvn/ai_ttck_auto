import whisper
import unicodedata

# ==============================
# LOAD MODEL (CACHE)
# ==============================

_MODEL = None

def get_model(model_size="base"):
    global _MODEL
    if _MODEL is None:
        _MODEL = whisper.load_model(model_size)
    return _MODEL


# ==============================
# CLEAN TEXT (GIỮ TIẾNG VIỆT CHUẨN)
# ==============================

def normalize_vietnamese(text):
    """
    Chuẩn hóa Unicode để tránh lỗi mất dấu tiếng Việt
    """
    text = unicodedata.normalize("NFC", text)
    
    # fix khoảng trắng
    text = text.replace(" ,", ",")
    text = text.replace(" .", ".")
    text = text.replace("  ", " ")
    
    return text.strip()


# ==============================
# TRANSCRIBE CORE
# ==============================

def transcribe(audio):
    """
    INPUT: audio path
    OUTPUT: list words [{word, start, end}]
    """
    
    model = get_model("base")  # giữ ổn định, không quá nặng
    
    result = model.transcribe(
        audio,
        language="vi",              # ép tiếng Việt
        task="transcribe",          # tránh auto translate
        word_timestamps=True,
        fp16=False                  # tránh lỗi trên CPU/GitHub Actions
    )

    words = []

    for seg in result.get("segments", []):
        for w in seg.get("words", []):
            word = normalize_vietnamese(w["word"])
            
            if word:  # tránh empty token
                words.append({
                    "word": word,
                    "start": round(w["start"], 2),
                    "end": round(w["end"], 2)
                })

    return words
