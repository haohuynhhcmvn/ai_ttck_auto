# ==============================
# RENDER VIDEO PRO (VIRAL STYLE)
# ==============================

from moviepy.editor import *
import os
import math
import random

def render_video(audio_path, subtitles, output):
    # 🔊 Load audio
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    # 🎬 Load background
    if not os.path.exists("background.mp4"):
        print("⚠️ Không có background → nền đen")
        base = ColorClip(size=(720, 1280), color=(0,0,0), duration=duration)

    else:
        bg = VideoFileClip("background.mp4")
        bg_duration = bg.duration

        # 🔁 Loop nếu ngắn
        if bg_duration < duration:
            loop_count = math.ceil(duration / bg_duration)
            bg = concatenate_videoclips([bg] * loop_count)

        # 🎯 Random đoạn video (tránh lặp nhàm)
        max_start = max(0, bg.duration - duration)
        start = random.uniform(0, max_start)
        base = bg.subclip(start, start + duration)

    # 📱 Resize chuẩn dọc 9:16
    base = base.resize(height=1280).crop(x_center=base.w/2, width=720)

    # 🔍 Zoom nhẹ liên tục (rất quan trọng)
    base = base.fx(vfx.resize, lambda t: 1 + 0.05*t/duration)

    # 🌫 Blur nền (giúp nổi chữ)
    try:
        blurred = base.fx(vfx.gaussian_blur, sigma=10)
    except:
        blurred = base  # fallback nếu lỗi

    # 🌓 Overlay tối nhẹ
    dark = ColorClip(size=(720,1280), color=(0,0,0), duration=duration).set_opacity(0.3)

    # 🎬 Combine layers
    video = CompositeVideoClip([blurred, dark])

    # 🔊 Gắn audio
    video = video.set_audio(audio)

    # 📝 Add subtitle
    final = CompositeVideoClip([video] + subtitles)

    # 💾 Export
    final.write_videofile(
        output,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="2500k"
    )
