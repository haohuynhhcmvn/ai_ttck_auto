# ==============================
# RENDER VIDEO PRO (TV STYLE)
# ==============================

from moviepy.editor import *
import os, math, random
from overlay import create_overlay
from market_data import get_market_data


def loop_background(bg, duration):
    """Loop video background nếu ngắn"""
    if bg.duration < duration:
        loop_count = math.ceil(duration / bg.duration)
        bg = concatenate_videoclips([bg] * loop_count)
    return bg


def safe_resize_crop(video):
    """Resize + crop chuẩn 9:16 (fix lỗi PIL ANTIALIAS)"""
    video = video.resize(height=1280)
    w, h = video.size

    if w > 720:
        video = video.crop(x_center=w/2, width=720)
    else:
        video = video.resize(width=720)

    return video


def add_zoom_effect(video, duration):
    """Zoom nhẹ kiểu TikTok giữ chân viewer"""
    return video.fx(vfx.resize, lambda t: 1 + 0.04 * t / duration)


def render_video(audio_path, subtitles, output):
    print("🎬 Render video PRO...")

    audio = AudioFileClip(audio_path)
    duration = audio.duration

    # ==============================
    # BACKGROUND
    # ==============================
    if os.path.exists("background.mp4"):
        bg = VideoFileClip("background.mp4")

        bg = loop_background(bg, duration)

        max_start = max(0, bg.duration - duration)
        start = random.uniform(0, max_start)

        video = bg.subclip(start, start + duration)
    else:
        print("⚠️ Không có background → nền đen")
        video = ColorClip((720, 1280), color=(0, 0, 0), duration=duration)

    video = safe_resize_crop(video)

    # 🔥 zoom nhẹ (giữ chân)
    video = add_zoom_effect(video, duration)

    # ==============================
    # DARK OVERLAY (giúp nổi chữ)
    # ==============================
    dark = ColorClip((720, 1280), color=(0, 0, 0), duration=duration).set_opacity(0.35)

    base = CompositeVideoClip([video, dark])

    # ==============================
    # DATA REALTIME
    # ==============================
    try:
        market_data = get_market_data()
    except:
        market_data = {}

    overlay = create_overlay(market_data, duration)

    # ==============================
    # SCENE CHIA (giống TV)
    # ==============================
    intro = TextClip(
        "BẢN TIN CHỨNG KHOÁN",
        fontsize=70,
        color="cyan",
        method="caption",
        size=(700, None)
    ).set_position(("center", 200)).set_duration(3)

    intro = intro.crossfadein(0.5)

    # ==============================
    # FINAL COMPOSE
    # ==============================
    final = CompositeVideoClip(
        [base, overlay, intro] + subtitles
    ).set_audio(audio)

    # ==============================
    # EXPORT
    # ==============================
    final.write_videofile(
        output,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="2500k",
        threads=2
    )

    print("✅ Done video:", output)
