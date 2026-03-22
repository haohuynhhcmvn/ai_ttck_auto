
# ==============================
# CREATE SUBTITLES
# ==============================

from moviepy.editor import TextClip

def create_subtitles(words):
    clips = []

    for w in words:
        try:
            clip = TextClip(
                w["word"],
                fontsize=60,
                color="white",
                font="DejaVu-Sans",  # 🔥 FIX FONT
                method="caption"     # 🔥 FIX ImageMagick
            ).set_start(w["start"]).set_duration(
                w["end"] - w["start"]
            ).set_position(("center", "bottom"))

            clips.append(clip)

        except Exception as e:
            print("⚠️ lỗi subtitle:", e)

    return clips
