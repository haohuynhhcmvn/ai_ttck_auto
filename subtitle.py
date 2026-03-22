
# ==============================
# CREATE SUBTITLES
# ==============================

from moviepy.editor import TextClip

def create_subtitles(words):
    clips = []

    for w in words:
        try:
            txt = w["word"]

            clip = TextClip(
                txt,
                fontsize=80,              # 🔥 chỉnh size ở đây
                color="white",
                stroke_color="black",     # viền chữ cho dễ đọc
                stroke_width=2,
                font="DejaVu-Sans",
                method="caption",
                size=(700, None)          # tự xuống dòng
            ).set_start(
                w["start"]
            ).set_duration(
                w["end"] - w["start"]
            ).set_position(
                ("center", "center")      # 🔥 CHỮ Ở GIỮA
            )

            clips.append(clip)

        except Exception as e:
            print("⚠️ subtitle lỗi:", e)

    return clips
