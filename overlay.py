# ==============================
# OVERLAY (BLOOMBERG STYLE - COMPATIBLE)
# ==============================

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageClip, CompositeVideoClip


# ==============================
# LOAD FONT
# ==============================
def load_font(size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]

    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except:
            continue

    return ImageFont.load_default()


# ==============================
# SAFE TEXT
# ==============================
def safe_text(x):
    try:
        return str(x)
    except:
        return "N/A"


# ==============================
# BUILD TICKER TEXT
# ==============================
def build_ticker(data):
    parts = []

    for item in data.get("gainers", [])[:5]:
        try:
            s, v = item
            parts.append(f"{s} {v}")
        except:
            continue

    for item in data.get("losers", [])[:5]:
        try:
            s, v = item
            parts.append(f"{s} {v}")
        except:
            continue

    return "   |   ".join(parts)


# ==============================
# DRAW MAIN PANEL
# ==============================
def draw_panel(data, size=(720,1280)):
    img = Image.new("RGBA", size, (0,0,0,0))
    draw = ImageDraw.Draw(img)

    font_big = load_font(70)
    font_small = load_font(36)

    vn = data.get("vnindex", {})
    close = safe_text(vn.get("close", "N/A"))
    change = safe_text(vn.get("change", "N/A"))

    # 🎨 màu
    color = "white"
    if "-" in change:
        color = "#ff4d4f"
    elif "+" in change:
        color = "#00e676"

    # 🔳 box nền
    draw.rectangle([40, 60, 680, 240], fill=(0,0,0,180))

    draw.text((60, 70), "VN-INDEX", font=font_small, fill="white")

    draw.text((60, 120), close, font=font_big, fill=color)

    draw.text((420, 140), change, font=font_small, fill=color)

    return np.array(img)


# ==============================
# CREATE TICKER CLIP
# ==============================
def create_ticker(data, duration):
    font = load_font(36)

    text = build_ticker(data)

    # tạo ảnh dài
    img = Image.new("RGB", (3000, 100), (0,0,0))
    draw = ImageDraw.Draw(img)
    draw.text((10, 20), text, font=font, fill="white")

    arr = np.array(img)

    clip = ImageClip(arr).set_duration(duration)

    # 🎬 chạy ngang
    def move(t):
        speed = 150
        return (-speed * t % arr.shape[1], 1100)

    return clip.set_position(move)


# ==============================
# MAIN API (GIỮ NGUYÊN PIPELINE)
# ==============================
def create_overlay(data, duration):
    panel = ImageClip(draw_panel(data)).set_duration(duration)

    ticker = create_ticker(data, duration)

    return CompositeVideoClip([panel, ticker])
