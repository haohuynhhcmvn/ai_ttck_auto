# ==============================
# OVERLAY TEXT (PIL)
# ==============================

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageClip

def draw_text_block(data, size=(720,1280)):
    img = Image.new("RGBA", size, (0,0,0,0))
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("arial.ttf", 50)
        font = ImageFont.truetype("arial.ttf", 32)
    except:
        font_big = font = ImageFont.load_default()

    y = 50

    # 🔥 VNINDEX
    vn = data.get("vnindex", {})
    close = vn.get("close", "N/A")
    change = vn.get("change", "N/A")

    draw.text((50,y), f"VN-Index: {close} ({change})", font=font_big, fill="white")
    y += 80

    # 🔥 TOP TĂNG
    draw.text((50,y), "TOP TĂNG:", font=font, fill="green")
    y += 40

    for item in data.get("gainers", []):
        try:
            s, v = item
            draw.text((50,y), f"{s}: {v}", font=font, fill="green")
            y += 35
        except:
            continue

    # 🔥 TOP GIẢM
    y = 500
    draw.text((50,y), "TOP GIẢM:", font=font, fill="red")
    y += 40

    for item in data.get("losers", []):
        try:
            s, v = item
            draw.text((50,y), f"{s}: {v}", font=font, fill="red")
            y += 35
        except:
            continue

    return np.array(img)


def create_overlay(data, duration):
    img = draw_text_block(data)
    return ImageClip(img).set_duration(duration)
