# ==============================
# OVERLAY TEXT (PRO - FIX FONT + STYLE)
# ==============================

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageClip


# ==============================
# LOAD FONT (CHUẨN GITHUB ACTION)
# ==============================
def load_font(size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]

    for path in paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            continue

    return ImageFont.load_default()


# ==============================
# SAFE TEXT (TRÁNH LỖI TIẾNG VIỆT)
# ==============================
def safe_text(text):
    try:
        return str(text)
    except:
        return ""


# ==============================
# DRAW TEXT CÓ VIỀN (PRO STYLE)
# ==============================
def draw_text(draw, pos, text, font, fill, stroke_width=2):
    x, y = pos

    # viền đen
    draw.text((x, y), text, font=font, fill=fill,
              stroke_width=stroke_width, stroke_fill="black")


# ==============================
# MAIN DRAW
# ==============================
def draw_text_block(data, size=(720,1280)):
    img = Image.new("RGBA", size, (0,0,0,0))
    draw = ImageDraw.Draw(img)

    font_big = load_font(60)
    font = load_font(36)

    y = 80

    # ==============================
    # VNINDEX
    # ==============================
    vn = data.get("vnindex", {})
    close = safe_text(vn.get("close", "N/A"))
    change = safe_text(vn.get("change", "N/A"))

    color = "white"
    if "-" in change:
        color = "#ff4d4f"   # đỏ
    elif "+" in change:
        color = "#00e676"   # xanh

    draw_text(
        draw,
        (50, y),
        f"VN-Index: {close} ({change})",
        font_big,
        color,
        3
    )

    y += 100

    # ==============================
    # TOP TĂNG
    # ==============================
    draw_text(draw, (50, y), "TOP TĂNG", font, "#00e676")
    y += 50

    for item in data.get("gainers", [])[:10]:
        try:
            s, v = item
            draw_text(draw, (50, y), f"{s}: {v}", font, "#00e676")
            y += 40
        except:
            continue

    # ==============================
    # TOP GIẢM
    # ==============================
    y = 700
    draw_text(draw, (50, y), "TOP GIẢM", font, "#ff4d4f")
    y += 50

    for item in data.get("losers", [])[:10]:
        try:
            s, v = item
            draw_text(draw, (50, y), f"{s}: {v}", font, "#ff4d4f")
            y += 40
        except:
            continue

    return np.array(img)


# ==============================
# CREATE OVERLAY CLIP
# ==============================
def create_overlay(data, duration):
    img = draw_text_block(data)

    return (
        ImageClip(img)
        .set_duration(duration)
        .set_position(("center", "center"))
        .fadein(0.5)
        .fadeout(0.5)
    )
