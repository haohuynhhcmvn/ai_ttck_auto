from PIL import Image, ImageDraw, ImageFont
import numpy as np
from datetime import datetime
import pytz
import platform

# Palette Bloomberg
C_ACCENT = (255, 153, 0)
C_BG_BOX = (15, 15, 15, 200)
C_UP = (0, 255, 150)
C_DOWN = (255, 60, 60)
C_WHITE = (255, 255, 255, 255)
C_SUB = (160, 160, 160, 255)

# Cấu hình cột
COL_X = {"SYM": 40, "PRICE": 240, "PCT": 430, "VOL": 680}

def load_font(size, bold=False):
    system = platform.system()
    f_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if system == "Windows": f_path = "arialbd.ttf" if bold else "arial.ttf"
    try: return ImageFont.truetype(f_path, size)
    except: return ImageFont.load_default()

def format_vol(v):
    if v >= 1e6: return f"{v/1e6:.1f}M"
    if v >= 1e3: return f"{v/1e3:.0f}K"
    return str(v)

def draw_overlay(data, size=(720, 1280)):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    f_h = load_font(42, True); f_b = load_font(28, True); f_s = load_font(22)

    # --- 1. HEADER (Giữ nguyên) ---
    draw.rectangle((0, 0, 720, 110), fill=C_ACCENT)
    draw.text((30, 15), "BẢN TIN TÀI CHÍNH 247", font=f_h, fill="black")
    vn_t = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime("%H:%M | %d/%m/%Y")
    draw.text((30, 70), vn_t, font=f_s, fill=(50, 50, 50))

    # --- 2. SUB HEADER (TICKER BACKGROUND) ---
    # Đây là nơi dòng chữ chạy ngang của bạn sẽ hiển thị trong MoviePy
    # Chúng ta vẽ một dải nền đen mờ ngay dưới Header (110px -> 160px)
    draw.rectangle((0, 110, 720, 165), fill=(0, 0, 0, 180))

    # --- 3. DYNAMIC CONTENT CONTAINER ---
    gainers = data.get("gainers", [])
    losers = data.get("losers", [])
    
    # Tính toán vị trí co giãn
    start_y = 185
    row_h = 50 
    
    # Vẽ Top Tăng
    if gainers:
        draw.text((40, start_y), "▲ TOP TĂNG TRƯỞNG", font=load_font(32, True), fill=C_UP)
        start_y += 50
        # Vẽ Header cột
        for k, x in [("MÃ", COL_X["SYM"]), ("GIÁ", COL_X["PRICE"]), ("%", COL_X["PCT"]), ("VOL", COL_X["VOL"]-50)]:
            draw.text((x, start_y), k, font=f_s, fill=C_SUB)
        start_y += 35
        
        for item in gainers:
            draw.text((COL_X["SYM"], start_y), item['symbol'], font=f_b, fill=C_WHITE)
            draw.text((COL_X["PRICE"], start_y), str(item['price']), font=f_b, fill=C_WHITE)
            draw.text((COL_X["PCT"], start_y), f"+{item['change']}%", font=f_b, fill=C_UP)
            v_txt = format_vol(item['volume'])
            draw.text((COL_X["VOL"] - draw.textlength(v_txt, f_b), start_y), v_txt, font=f_b, fill=C_WHITE)
            draw.line((40, start_y+38, 680, start_y+38), fill=(255,255,255,20))
            start_y += row_h

    # Khoảng cách giữa 2 bảng co giãn
    start_y += 40 

    # Vẽ Top Giảm
    if losers:
        draw.text((40, start_y), "▼ TOP GIẢM ĐIỂM", font=load_font(32, True), fill=C_DOWN)
        start_y += 50
        for k, x in [("MÃ", COL_X["SYM"]), ("GIÁ", COL_X["PRICE"]), ("%", COL_X["PCT"]), ("VOL", COL_X["VOL"]-50)]:
            draw.text((x, start_y), k, font=f_s, fill=C_SUB)
        start_y += 35
        
        for item in losers:
            draw.text((COL_X["SYM"], start_y), item['symbol'], font=f_b, fill=C_WHITE)
            draw.text((COL_X["PRICE"], start_y), str(item['price']), font=f_b, fill=C_WHITE)
            draw.text((COL_X["PCT"], start_y), f"{item['change']}%", font=f_b, fill=C_DOWN)
            v_txt = format_vol(item['volume'])
            draw.text((COL_X["VOL"] - draw.textlength(v_txt, f_b), start_y), v_txt, font=f_b, fill=C_WHITE)
            draw.line((40, start_y+38, 680, start_y+38), fill=(255,255,255,20))
            start_y += row_h

    # --- 4. FOOTER (Giữ nguyên) ---
    draw.rectangle((0, 1200, 720, 1280), fill=(10, 10, 10, 255))
    draw.text((30, 1225), "Product by: Tâm sự 24h - Tài chính & Công nghệ", font=f_s, fill=C_SUB)

    return np.array(img)
