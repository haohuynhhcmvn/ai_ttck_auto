
# ==============================
# CREATE SUBTITLES
# ==============================

from moviepy.editor import TextClip

def create_subtitles(words):
    clips = []
    for w in words:
        clip = TextClip(
            w["word"],
            fontsize=70,
            color="yellow",
            stroke_color="black",
            stroke_width=2
        ).set_start(w["start"]).set_duration(w["end"] - w["start"]).set_position(("center","bottom"))

        clips.append(clip)

    return clips
