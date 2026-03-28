# ==============================
# BLOOMBERG STYLE OVERLAY (LEAN - NO INDEX)
# ==============================

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageClip
from datetime import datetime


# ==============================
# LOAD FONT SAFE
# ==============================
def load_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size
            )
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size
        )
    except:
        return ImageFont.load_default()


# ==============================
# COLOR HELPER
# ==============================
def get_color(value):
    try:
        value = float(value)
        return (0, 230, 118) if value >= 0 else (255, 82, 82)
    except:
        return (255, 255, 255)


# ==============================
# DRAW OVERLAY (NO INDEX)
# ==============================
def draw_overlay(data, size=(720, 1280)):
    img = Image.new("RGBA", size, (0, 0, 0, 160))
    draw = ImageDraw.Draw(img)

    font_big = load_font(42, bold=True)
    font = load_font(26)

    # ==========================
    # HEADER
    # ==========================
    draw.rectangle((0, 0, 720, 80), fill=(255, 140, 0, 255))

    today = datetime.now().strftime("%d/%m/%Y")

    draw.text((20, 18), "MARKET LIVE", font=font_big, fill="black")
    draw.text((500, 25), today, font=font, fill="black")

    y = 120

    # ==========================
    # TOP GAINERS
    # ==========================
    draw.text((20, y), "TOP GAINERS", font=font_big, fill=(0, 230, 118))
    y += 50

    for s, v in data.get("gainers", [])[:8]:
        draw.text((20, y), f"{s}", font=font, fill="white")

        draw.text(
            (250, y),
            f"+{v}%",
            font=font,
            fill=get_color(v)
        )

        y += 32

    # ==========================
    # TOP LOSERS
    # ==========================
    y += 30
    draw.text((20, y), "TOP LOSERS", font=font_big, fill=(255, 82, 82))
    y += 50

    for s, v in data.get("losers", [])[:8]:
        draw.text((20, y), f"{s}", font=font, fill="white")

        draw.text(
            (250, y),
            f"{v}%",
            font=font,
            fill=get_color(v)
        )

        y += 32

    return np.array(img)


# ==============================
# CREATE OVERLAY
# ==============================
def create_overlay(data, duration):
    img = draw_overlay(data)

    return (
        ImageClip(img)
        .set_duration(duration)
        .set_position(("center", "center"))
    )
