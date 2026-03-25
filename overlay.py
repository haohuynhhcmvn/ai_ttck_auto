# ==============================
# BLOOMBERG STYLE OVERLAY
# ==============================

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageClip
from datetime import datetime

def draw_overlay(data, size=(720,1280)):
    img = Image.new("RGBA", size, (0,0,0,180))
    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 42)
        font = ImageFont.truetype("DejaVuSans.ttf", 26)
    except:
        font_big = font = ImageFont.load_default()


    # ===== HEADER =====
    draw.rectangle((0,0,720,80), fill=(255,140,0,255))
    
    # 📅 Lấy ngày hiện tại
    today = datetime.now().strftime("%d/%m/%Y")
    
    # 📰 Title bên trái
    draw.text((20,20), "MARKET LIVE", font=font_big, fill="black")
    
    # 📅 Ngày bên phải (căn phải cho đẹp như TV)
    draw.text((520,20), today, font=font, fill="black")

    y = 120

    # ===== VNINDEX =====
    vn = data.get("vnindex", {})
    text = f"VN-Index: {vn.get('close')} ({vn.get('change')})"
    draw.text((20,y), text, font=font_big, fill="white")
    y += 80

    # ===== VN30 =====
    vn30 = data.get("vn30", {})
    text = f"VN30: {vn30.get('close')} ({vn30.get('change')})"
    draw.text((20,y), text, font=font, fill="white")
    y += 60

    # ===== TOP GAINERS =====
    draw.text((20,y), "TOP GAINERS", font=font_big, fill="green")
    y += 40

    for s, v in data.get("gainers", [])[:5]:
        draw.text((20,y), f"{s}: +{v}%", font=font, fill="green")
        y += 30

    # ===== TOP LOSERS =====
    y += 30
    draw.text((20,y), "TOP LOSERS", font=font_big, fill="red")
    y += 40

    for s, v in data.get("losers", [])[:5]:
        draw.text((20,y), f"{s}: {v}%", font=font, fill="red")
        y += 30

    return np.array(img)


def create_overlay(data, duration):
    img = draw_overlay(data)
    return ImageClip(img).set_duration(duration)
