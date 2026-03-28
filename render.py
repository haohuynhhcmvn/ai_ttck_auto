# ==============================
# RENDER VIDEO PRO MAX (ULTRA FAST)
# ==============================

import subprocess
import os
import random
from moviepy.editor import AudioFileClip
from overlay import draw_overlay
from PIL import Image


def render_video(audio_path, subtitles, output, topic=None, market_data=None, script=None):
    print("🎬 Render video PRO MAX (ULTRA FAST)...")

    audio = AudioFileClip(audio_path)
    duration = audio.duration

    # ==========================
    # OVERLAY → PNG (SIÊU NHẸ)
    # ==========================
    overlay_path = None

    if market_data:
        try:
            img = draw_overlay(market_data)
            overlay_path = "overlay.png"

            Image.fromarray(img).save(overlay_path)

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
    # BUILD FILTER
    # ==========================
    filters = []

    # chuẩn 9:16
    filters.append(
        "[0:v]scale=720:1280:force_original_aspect_ratio=increase,"
        "crop=720:1280[bg]"
    )

    # overlay PNG
    if overlay_path:
        filters.append("[bg][1:v]overlay=0:0[tmp1]")
        last_video = "[tmp1]"
        audio_index = 2
    else:
        last_video = "[bg]"
        audio_index = 1

    # subtitle ASS
    if subtitles and subtitles.endswith(".ass"):
        safe_sub = subtitles.replace("\\", "/")
        filters.append(f"{last_video}ass={safe_sub}[v]")
    else:
        filters.append(f"{last_video}[v]")

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
        cmd += ["-loop", "1", "-i", overlay_path]

    cmd += [
        "-i", audio_path,

        "-filter_complex", filter_complex,

        "-map", "[v]",
        "-map", f"{audio_index}:a",

        "-t", str(duration),
        "-shortest",

        # 🔥 encode nhanh hơn nhiều
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "fastdecode",
        "-crf", "23",
        "-pix_fmt", "yuv420p",

        "-c:a", "aac",
        "-b:a", "128k",

        output
    ]

    print("⚙️ FFmpeg CMD:", " ".join(cmd))

    subprocess.run(cmd, check=True)

    print("✅ Done video:", output)
