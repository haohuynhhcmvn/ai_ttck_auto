# ==============================
# RENDER VIDEO PRO MAX (FIXED)
# ==============================

import subprocess
import os
import random
from moviepy.editor import *
from overlay import create_overlay


def render_video(audio_path, subtitles, output, topic=None, market_data=None, script=None):
    print("🎬 Render video 9:16 (FFmpeg PRO MAX)...")

    audio = AudioFileClip(audio_path)
    duration = audio.duration

    # ==========================
    # OVERLAY
    # ==========================
    overlay_path = None

    if market_data:
        try:
            overlay_clip = create_overlay(market_data, duration)

            overlay_path = "overlay.mp4"
            overlay_clip.write_videofile(
                overlay_path,
                fps=30,
                codec="libx264",
                audio=False,
                preset="ultrafast"   # 🔥 tăng tốc
            )

            overlay_clip.close()

        except Exception as e:
            print("⚠️ overlay lỗi:", e)

    # ==========================
    # BACKGROUND
    # ==========================
    if os.path.exists("background.mp4"):
        start_time = random.uniform(0, 5)

        bg_input = [
            "-ss", str(start_time),
            "-stream_loop", "-1",
            "-i", "background.mp4"
        ]
    else:
        bg_input = [
            "-f", "lavfi",
            "-i", "color=c=black:s=720x1280:r=24"
        ]

    # ==========================
    # FILTER
    # ==========================
    filters = []

    filters.append(
        "[0:v]fps=24,scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280[bg]"
    )

    # overlay
    if overlay_path:
        filters.append("[bg][1:v]overlay=0:0[tmp1]")
        last_video = "[tmp1]"
        audio_index = 2
    else:
        last_video = "[bg]"
        audio_index = 1

    # subtitle
    if subtitles and subtitles.endswith(".ass"):
        safe_sub = subtitles.replace("\\", "/")
        filters.append(f"{last_video}ass={safe_sub}[v]")
    else:
        filters.append(f"{last_video}null[v]")

    filter_complex = ";".join(filters)

    # ==========================
    # BUILD CMD
    # ==========================
    cmd = [
        "ffmpeg",
        "-y",
        *bg_input,
    ]

    if overlay_path:
        cmd += ["-i", overlay_path]

    cmd += [
        "-i", audio_path,

        "-filter_complex", filter_complex,

        "-map", "[v]",
        "-map", f"{audio_index}:a",

        "-t", str(duration),   # 🔥 FIX QUAN TRỌNG
        "-shortest",

        "-r", "24",

        "-c:v", "libx264",
        "-preset", "ultrafast",   # 🔥 nhanh hơn
        "-crf", "23",
        "-pix_fmt", "yuv420p",

        "-c:a", "aac",
        "-b:a", "128k",

        output
    ]

    print("⚙️ FFmpeg CMD:", " ".join(cmd))

    subprocess.run(cmd, check=True)

    print("✅ Done video:", output)
