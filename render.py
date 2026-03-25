# ==============================
# RENDER VIDEO
# ==============================

from moviepy.editor import *
import os, math, random
from overlay import create_overlay
from market_data import get_market_data

def render_video(audio_path, subtitles, output):
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    # background
    if os.path.exists("background.mp4"):
        bg = VideoFileClip("background.mp4")

        if bg.duration < duration:
            loop = math.ceil(duration / bg.duration)
            bg = concatenate_videoclips([bg]*loop)

        start = random.uniform(0, bg.duration-duration)
        video = bg.subclip(start, start+duration)
    else:
        video = ColorClip((720,1280), color=(0,0,0), duration=duration)

    video = video.resize(height=1280).crop(width=720, x_center=video.w/2)
    video = video.set_audio(audio)

    # 🔥 overlay data thật
    market_data = get_market_data()
    overlay = create_overlay(market_data, duration)

    final = CompositeVideoClip([video, overlay] + subtitles)

    final.write_videofile(output, fps=30)
