# ==============================
# TRANSCRIBE PRO MAX (FAST + CLEAN)
# ==============================

import whisper
import unicodedata
import re

_MODEL = None


# ==============================
# LOAD MODEL (CACHE)
# ==============================
def get_model(model_size="tiny"):
    global _MODEL
    if _MODEL is None:
        print(f"🚀 Load Whisper model: {model_size}")
        _MODEL = whisper.load_model(model_size)
    return _MODEL


# ==============================
# CLEAN TEXT (VIETNAMESE SAFE)
# ==============================
def normalize_vietnamese(text):
    text = unicodedata.normalize("NFC", text)

    # remove ký tự rác đầu/cuối
    text = text.strip()

    # fix khoảng trắng
    text = re.sub(r"\s+", " ", text)
    text = text.replace(" ,", ",").replace(" .", ".")

    return text


# ==============================
# FILTER WORD
# ==============================
def clean_word(word):
    word = normalize_vietnamese(word)

    # bỏ ký tự rác
    if not word:
        return None

    if word in ["...", "-", "—"]:
        return None

    return word


# ==============================
# MERGE WORD (SMOOTH SUBTITLE)
# ==============================
def merge_short_words(words, min_duration=0.15):
    merged = []

    for w in words:
        if not merged:
            merged.append(w)
            continue

        prev = merged[-1]

        duration = w["end"] - w["start"]

        # nếu từ quá ngắn → gộp
        if duration < min_duration:
            prev["word"] += " " + w["word"]
            prev["end"] = w["end"]
        else:
            merged.append(w)

    return merged


# ==============================
# TRANSCRIBE CORE
# ==============================
def transcribe(audio):
    model = get_model("tiny")  # 🔥 nhanh hơn base

    result = model.transcribe(
        audio,
        language="vi",
        task="transcribe",
        word_timestamps=True,
        fp16=False
    )

    words = []

    for seg in result.get("segments", []):
        for w in seg.get("words", []):
            word = clean_word(w["word"])

            if not word:
                continue

            words.append({
                "word": word,
                "start": float(w["start"]),   # 🔥 giữ nguyên (không round)
                "end": float(w["end"])
            })

    # 🔥 merge để subtitle mượt hơn
    words = merge_short_words(words)

    return words
