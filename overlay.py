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

    # VNINDEX
    vn = data["vnindex"]
    draw.text((50,y), f"VNINDEX: {vn[0]} ({vn[1]})", font=font_big, fill="white")
    y += 80

    # VN30
    vn30 = data["vn30"]
    draw.text((50,y), f"VN30: {vn30[0]} ({vn30[1]})", font=font, fill="yellow")
    y += 60

    # TOP TĂNG
    draw.text((50,y), "TOP TĂNG:", font=font, fill="green")
    y += 40
    for s,v in data["gainers"]:
        draw.text((50,y), f"{s}: {v}", font=font, fill="green")
        y += 35

    # TOP GIẢM
    y = 400
    draw.text((50,y), "TOP GIẢM:", font=font, fill="red")
    y += 40
    for s,v in data["losers"]:
        draw.text((50,y), f"{s}: {v}", font=font, fill="red")
        y += 35

    return np.array(img)

def create_overlay(data, duration):
    img = draw_text_block(data)
    return ImageClip(img).set_duration(duration)
