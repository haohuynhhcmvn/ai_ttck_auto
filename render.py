# ==============================
# RENDER VIDEO PRO (TV STYLE)
# ==============================

from moviepy.editor import *
import os, math, random
from overlay import create_overlay

def render_video(audio_path, subtitles, output, topic=None, market_data=None, script=None):
    print("🎬 Render video...")

    audio = AudioFileClip(audio_path)
    duration = audio.duration

    # ==========================
    # BACKGROUND
    # ==========================
    if os.path.exists("background.mp4"):
        bg = VideoFileClip("background.mp4")

        if bg.duration < duration:
            loop = math.ceil(duration / bg.duration)
            bg = concatenate_videoclips([bg]*loop)

        start = random.uniform(0, max(0, bg.duration - duration))
        video = bg.subclip(start, start + duration)
    else:
        video = ColorClip((720,1280), color=(0,0,0), duration=duration)

    # resize chuẩn dọc
    video = video.resize(height=1280)
    video = video.crop(x_center=video.w/2, width=720)

    video = video.set_audio(audio)

    # ==========================
    # OVERLAY DATA
    # ==========================
    if market_data:
        try:
            overlay = create_overlay(market_data, duration)
            clips = [video, overlay] + subtitles
        except Exception as e:
            print("⚠️ overlay lỗi:", e)
            clips = [video] + subtitles
    else:
        clips = [video] + subtitles

    # ==========================
    # FINAL
    # ==========================
    final = CompositeVideoClip(clips)

    final.write_videofile(
        output,
        fps=30,
        codec="libx264",
        audio_codec="aac"
    )

    print("✅ Done:", output)
    print("✅ Done video:", output)
