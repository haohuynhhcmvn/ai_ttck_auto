# ==============================
# CREATE SUBTITLES (CENTER FIX)
# ==============================

from moviepy.editor import TextClip, CompositeVideoClip
import unicodedata

FONT_PATH = "assets/fonts/NotoSans-Regular.ttf"
FONT_SIZE = 80
MAX_WORDS = 6


def normalize_text(text):
    text = unicodedata.normalize("NFC", text)
    text = text.replace(" ,", ",").replace(" .", ".")
    text = text.replace("  ", " ")
    return text.strip()


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


def create_subtitles(words):
    clips = []
    lines = group_words(words)

    for line in lines:
        try:
            full_text = normalize_text(" ".join([w["word"] for w in line]))

            start = line[0]["start"]
            end = line[-1]["end"]

            # 🔥 BASE TEXT (CENTER CHUẨN)
            base_clip = TextClip(
                full_text,
                fontsize=FONT_SIZE,
                color="white",
                stroke_color="black",
                stroke_width=3,
                font=FONT_PATH,
                method="caption",
                size=(900, None),        # 🔥 rộng hơn để không xuống dòng xấu
                align="center"           # 🔥 canh chữ giữa
            ).set_start(start).set_duration(end - start).set_position(
                ("center", 0.6), relative=True   # 🔥 FIX CHUẨN CENTER (TikTok style)
            )

            sub_clips = [base_clip]

            # 🔥 HIGHLIGHT
            for w in line:
                word = normalize_text(w["word"])

                highlight = TextClip(
                    word,
                    fontsize=FONT_SIZE,
                    color="yellow",
                    stroke_color="black",
                    stroke_width=3,
                    font=FONT_PATH,
                    method="caption"
                ).set_start(w["start"]).set_duration(
                    w["end"] - w["start"]
                ).set_position(
                    ("center", 0.6), relative=True   # 🔥 đồng bộ vị trí
                )

                sub_clips.append(highlight)

            final_clip = CompositeVideoClip(sub_clips)

            clips.append(final_clip)

        except Exception as e:
            print("⚠️ subtitle lỗi:", e)

    return clips
