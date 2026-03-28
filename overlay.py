# ==============================
# BLOOMBERG STYLE OVERLAY (PRO)
# ==============================

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageClip
from datetime import datetime


# ==============================
# LOAD FONT SAFE (GH ACTIONS)
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
# DRAW OVERLAY
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
    # VNINDEX
    # ==========================
    vn = data.get("vnindex", {})
    vn_close = vn.get("close", "N/A")
    vn_change = vn.get("change", "N/A")

    color = get_color(vn_change)

    draw.text(
        (20, y),
        f"VN-Index: {vn_close}",
        font=font_big,
        fill="white"
    )

    draw.text(
        (420, y),
        f"{vn_change}",
        font=font_big,
        fill=color
    )

    y += 80

    # ==========================
    # VN30
    # ==========================
    vn30 = data.get("vn30", {})
    vn30_change = vn30.get("change", "N/A")

    draw.text((20, y), "VN30:", font=font, fill="white")

    draw.text(
        (120, y),
        f"{vn30_change}",
        font=font,
        fill=get_color(vn30_change)
    )

    y += 60

    # ==========================
    # TOP GAINERS
    # ==========================
    draw.text((20, y), "TOP GAINERS", font=font_big, fill=(0, 230, 118))
    y += 40

    for s, v in data.get("gainers", [])[:8]:
        draw.text(
            (20, y),
            f"{s}",
            font=font,
            fill="white"
        )

        draw.text(
            (250, y),
            f"+{v}%",
            font=font,
            fill=(0, 230, 118)
        )

        y += 30

    # ==========================
    # TOP LOSERS
    # ==========================
    y += 20
    draw.text((20, y), "TOP LOSERS", font=font_big, fill=(255, 82, 82))
    y += 40

    for s, v in data.get("losers", [])[:8]:
        draw.text(
            (20, y),
            f"{s}",
            font=font,
            fill="white"
        )

        draw.text(
            (250, y),
            f"{v}%",
            font=font,
            fill=(255, 82, 82)
        )

        y += 30

    return np.array(img)


# ==============================
# CREATE OVERLAY (NHẸ + NHANH)
# ==============================
def create_overlay(data, duration):
    img = draw_overlay(data)

    return (
        ImageClip(img)
        .set_duration(duration)
        .set_position(("center", "center"))
    )
