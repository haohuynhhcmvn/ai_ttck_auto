
# ==============================
# CREATE SUBTITLES
# ==============================

from moviepy.editor import TextClip
import unicodedata

def create_subtitles(words):
    clips = []

    for w in words:
        try:
            txt = unicodedata.normalize("NFC", w["word"])

            clip = TextClip(
                txt,
                fontsize=80,
                color="white",
                stroke_color="black",
                stroke_width=2,
                font="assets/fonts/NotoSans-Regular.ttf",  # 🔥 font chuẩn
                method="caption",
                size=(700, None)
            ).set_start(
                w["start"]
            ).set_duration(
                w["end"] - w["start"]
            ).set_position(
                ("center", "center")
            )

            clips.append(clip)

        except Exception as e:
            print("⚠️ subtitle lỗi:", e)

    return clips
