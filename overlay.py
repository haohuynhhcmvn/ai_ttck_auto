# ==============================
# BLOOMBERG STYLE OVERLAY (LEAN - PRO)
# ==============================

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from datetime import datetime
import platform

# ==============================
# SMART FONT LOADER
# ==============================
def load_font(size, bold=False):
    """Tự động tìm font phù hợp trên mọi OS"""
    system = platform.system()
    fonts = []
    
    if system == "Windows":
        fonts = ["arialbd.ttf" if bold else "arial.ttf", "calibrib.ttf", "segoeuib.ttf"]
    else: # Linux/Docker
        fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
            "DejaVuSans-Bold.ttf"
        ]
    
    for f in fonts:
        try:
            return ImageFont.truetype(f, size)
        except:
            continue
    return ImageFont.load_default()

# ==============================
# COLOR PALETTE
# ==============================
C_BG = (0, 0, 0, 140)      # Nền đen trong suốt
C_ACCENT = (255, 165, 0)   # Cam Bloomberg
C_UP = (0, 255, 127)       # Xanh neon
C_DOWN = (255, 69, 58)     # Đỏ rực
C_WHITE = (255, 255, 255, 255)

# ==============================
# DRAW OVERLAY (PRO VERSION)
# ==============================
def draw_overlay(data, size=(720, 1280)):
    # 1. Tạo base layer RGBA
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    f_header = load_font(40, bold=True)
    f_section = load_font(38, bold=True)
    f_ticker = load_font(30, bold=True)
    f_small = load_font(24)

    # --- HEADER BAR ---
    # Vẽ dải cam đặc trưng của Bloomberg
    draw.rectangle((0, 0, 720, 90), fill=C_ACCENT)
    draw.text((30, 20), "BẢN TIN CHỨNG KHOÁN", font=f_header, fill="black")
    
    today = datetime.now().strftime("%H:%M | %d/%m/%Y")
    draw.text((450, 150), today, font=f_small, fill="black")

    # --- CONTAINER BACKGROUND ---
    # Vẽ một hình chữ nhật bo góc mờ để chứa bảng giá
    margin_x = 20
    draw.rounded_rectangle((margin_x, 110, 700, 1150), radius=15, fill=C_BG)

    y = 150

    # --- TOP GAINERS ---
    draw.text((50, y), "▲ TOP GAINERS", font=f_section, fill=C_UP)
    y += 70

    # Header cột
    draw.text((60, y), "TICKER", font=f_small, fill=(200, 200, 200))
    draw.text((450, y), "CHANGE (%)", font=f_small, fill=(200, 200, 200))
    y += 45

    for s, v in data.get("gainers", [])[:8]:
        # Dòng kẻ ngang mờ
        draw.line((60, y+40, 660, y+40), fill=(255, 255, 255, 30), width=1)
        
        draw.text((60, y), str(s), font=f_ticker, fill=C_WHITE)
        draw.text((450, y), f"+{v}%", font=f_ticker, fill=C_UP)
        y += 65

    # --- TOP LOSERS ---
    y += 150
    draw.text((50, y), "▼ TOP LOSERS", font=f_section, fill=C_DOWN)
    y += 70

    for s, v in data.get("losers", [])[:8]:
        draw.line((60, y+40, 660, y+40), fill=(255, 255, 255, 30), width=1)
        
        draw.text((60, y), str(s), font=f_ticker, fill=C_WHITE)
        draw.text((450, y), f"{v}%", font=f_ticker, fill=C_DOWN)
        y += 65

    # --- FOOTER ---
    draw.rectangle((0, 1200, 720, 1280), fill=(20, 20, 20, 200))
    draw.text((30, 1225), "Data provided by Yahoo Finance API", font=f_small, fill=(150, 150, 150))

    return np.array(img)

# --- TEST ---
if __name__ == "__main__":
    sample_data = {
        "gainers": [("FPT", 6.9), ("HPG", 4.5), ("SSI", 3.2), ("MWG", 2.1)],
        "losers": [("VIC", -4.2), ("VHM", -3.8), ("NVL", -2.5), ("PDR", -1.9)]
    }
    img_array = draw_overlay(sample_data)
    # Lưu test
    test_img = Image.fromarray(img_array)
    test_img.save("overlay_test.png")
    print("✅ Đã tạo file overlay_test.png để xem thử.")
