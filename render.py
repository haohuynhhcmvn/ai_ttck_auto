
# ==============================
# RENDER VIDEO
# ==============================

from moviepy.editor import *
import os

def render_video(audio_path, subtitles, output):
    if not os.path.exists("background.mp4"):
        print("⚠️ Không có background → dùng video màu đen")

        video = ColorClip(size=(720, 1280), color=(0,0,0), duration=30)
    else:
        video = VideoFileClip("background.mp4").subclip(0, 30)

    audio = AudioFileClip(audio_path)
    video = video.set_audio(audio)

    final = CompositeVideoClip([video] + subtitles)
    final.write_videofile(output, fps=24)
