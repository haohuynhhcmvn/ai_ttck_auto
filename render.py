
# ==============================
# RENDER VIDEO
# ==============================

from moviepy.editor import *

def render_video(audio_path, subtitles, output):
    video = VideoFileClip("background.mp4").subclip(0, 30)

    audio = AudioFileClip(audio_path)
    video = video.set_audio(audio)

    final = CompositeVideoClip([video] + subtitles)
    final.write_videofile(output, fps=24)
