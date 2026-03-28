# ==============================
# CREATE SUBTITLES (OPTIMIZED)
# ==============================

from moviepy.editor import TextClip, CompositeVideoClip
import unicodedata

# ==============================
# CONFIG
# ==============================

FONT_PATH = "assets/fonts/NotoSans-Regular.ttf"
FONT_SIZE = 80
MAX_WORDS = 6  # số từ mỗi dòng


# ==============================
# NORMALIZE TEXT
# ==============================

def normalize_text(text):
    text = unicodedata.normalize("NFC", text)
    text = text.replace(" ,", ",").replace(" .", ".")
    text = text.replace("  ", " ")
    return text.strip()


# ==============================
# GROUP WORDS → LINES
# ==============================

def group_words(words):
    lines = []
    current = []

    for w in words:
        current.append(w)

        if len(current) >= MAX_WORDS or w["word"].endswith((".", ",")):
            lines.append(current)
            current = []

    if current:
        lines.append(current)

    return lines


# ==============================
# CREATE SUBTITLES
# ==============================

def create_subtitles(words):
    clips = []
    lines = group_words(words)

    for line in lines:
        try:
            # full text line
            full_text = normalize_text(" ".join([w["word"] for w in line]))

            start = line[0]["start"]
            end = line[-1]["end"]

            # 🔹 nền (text trắng)
            base_clip = TextClip(
                full_text,
                fontsize=FONT_SIZE,
                color="white",
                stroke_color="black",
                stroke_width=3,
                font=FONT_PATH,
                method="caption",
                size=(800, None)
            ).set_start(start).set_duration(end - start).set_position(("center", "center"))

            sub_clips = [base_clip]

            # 🔥 highlight từng từ
            for w in line:
                word = normalize_text(w["word"])

                highlight = TextClip(
                    word,
                    fontsize=FONT_SIZE,
                    color="yellow",  # màu highlight
                    stroke_color="black",
                    stroke_width=3,
                    font=FONT_PATH,
                    method="caption"
                ).set_start(w["start"]).set_duration(w["end"] - w["start"])

                # ⚠️ cần tính vị trí từng từ trong dòng
                # workaround: render cả dòng rồi mask từng từ
                highlight = highlight.set_position(("center", "center"))

                sub_clips.append(highlight)

            # ghép lại thành 1 clip
            final_clip = CompositeVideoClip(sub_clips)

            clips.append(final_clip)

        except Exception as e:
            print("⚠️ subtitle lỗi:", e)

    return clips
