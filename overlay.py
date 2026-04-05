from PIL import Image, ImageDraw, ImageFont
import numpy as np
from datetime import datetime
import pytz
import platform

# --- BẢNG MÀU PHONG CÁCH BLOOMBERG (GIỮ NGUYÊN) ---
C_ACCENT = (255, 153, 0)       # Màu cam thương hiệu
C_BG_BOX = (10, 10, 10, 180)   # Nền đen mờ (Glassmorphism)
C_TICKER_BG = (0, 0, 0, 220)    # Nền đen đậm cho Ticker
C_UP = (0, 255, 150)           # Màu xanh lục
C_DOWN = (255, 60, 60)         # Màu đỏ
C_WHITE = (255, 255, 255, 255) 
C_SUB = (170, 170, 170, 255)   

# --- CẤU HÌNH TỌA ĐỘ CỘT ---
COL_X = {"SYM": 45, "PRICE": 240, "PCT": 430, "VOL": 680}

def load_font(size, bold=False):
    """Tải font hệ thống (Hỗ trợ Linux GHA & Windows)"""
    system = platform.system()
    f_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if system == "Windows": f_path = "arialbd.ttf" if bold else "arial.ttf"
    try: 
        return ImageFont.truetype(f_path, size)
    except: 
        return ImageFont.load_default()

def format_vol(v):
    """Định dạng số khối lượng rút gọn K, M"""
    if v >= 1e6: return f"{v/1e6:.1f}M"
    if v >= 1e3: return f"{v/1e3:.0f}K"
    return f"{v:,.0f}"

# --- CẬP NHẬT: THÊM THAM SỐ frame_time VÀO HÀM CHÍNH ---
def draw_overlay(data, size=(720, 1280), frame_time=0):
    """
    Vẽ lớp phủ overlay.
    LOGIC MỚI: Nếu frame_time < 2.5, chỉ vẽ Header & Footer, để trống phần giữa cho Hook.
    """
    # Tạo ảnh nền trong suốt RGBA
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Khởi tạo font
    f_h = load_font(40, True)      
    f_b = load_font(22, True)      
    f_s = load_font(20)            
    f_title = load_font(30, True)  

    # --- 1. VẼ HEADER (LUÔN HIỆN ĐỂ GIỮ THƯƠNG HIỆU) ---
    draw.rectangle((0, 0, 720, 110), fill=C_ACCENT) 
    draw.text((30, 15), "BẢN TIN TÀI CHÍNH 247", font=f_h, fill="black")
    vn_t = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime("%H:%M | %d/%m/%Y")
    draw.text((30, 70), vn_t, font=f_s, fill=(40, 40, 40))

    # Nền cho Ticker
    draw.rectangle((0, 110, 720, 165), fill=C_TICKER_BG)

    # --- 2. LOGIC HIỂN THỊ NỘI DUNG CHÍNH (CỰC KỲ QUAN TRỌNG) ---
    # Chỉ vẽ bảng dữ liệu nếu đã qua giai đoạn Hook (2.5 giây đầu)
    if frame_time > 2.5:
        # Vẽ khung nền mờ
        draw.rounded_rectangle((25, 175, 695, 1185), radius=15, fill=C_BG_BOX)

        gainers = data.get("gainers", [])
        losers = data.get("losers", [])
        start_y = 200 
        row_h = 36    
        
        # --- VẼ NHÓM TĂNG ---
        if gainers:
            draw.text((45, start_y), "▲ TOP CỔ PHIẾU TĂNG TRƯỞNG", font=f_title, fill=C_UP)
            start_y += 55
            for k, x in [("MÃ", COL_X["SYM"]), ("GIÁ", COL_X["PRICE"]), ("%", COL_X["PCT"]), ("VOL", COL_X["VOL"]-50)]:
                draw.text((x, start_y), k, font=f_s, fill=C_SUB)
            start_y += 35
            for item in gainers:
                draw.text((COL_X["SYM"], start_y), item['symbol'], font=f_b, fill=C_WHITE)
                draw.text((COL_X["PRICE"], start_y), f"{item['price']:,}", font=f_b, fill=C_WHITE)
                draw.text((COL_X["PCT"], start_y), f"+{item['change']}%", font=f_b, fill=C_UP)
                v_txt = format_vol(item['volume'])
                draw.text((COL_X["VOL"] - draw.textlength(v_txt, f_b), start_y), v_txt, font=f_b, fill=C_WHITE)
                draw.line((40, start_y+35, 680, start_y+35), fill=(255,255,255,15))
                start_y += row_h

        start_y += 30 

        # --- VẼ NHÓM GIẢM ---
        if losers:
            draw.text((45, start_y), "▼ TOP CỔ PHIẾU GIẢM ĐIỂM", font=f_title, fill=C_DOWN)
            start_y += 55
            for k, x in [("MÃ", COL_X["SYM"]), ("GIÁ", COL_X["PRICE"]), ("%", COL_X["PCT"]), ("VOL", COL_X["VOL"]-50)]:
                draw.text((x, start_y), k, font=f_s, fill=C_SUB)
            start_y += 35
            for item in losers:
                draw.text((COL_X["SYM"], start_y), item['symbol'], font=f_b, fill=C_WHITE)
                draw.text((COL_X["PRICE"], start_y), f"{item['price']:,}", font=f_b, fill=C_WHITE)
                draw.text((COL_X["PCT"], start_y), f"{item['change']}%", font=f_b, fill=C_DOWN)
                v_txt = format_vol(item['volume'])
                draw.text((COL_X["VOL"] - draw.textlength(v_txt, f_b), start_y), v_txt, font=f_b, fill=C_WHITE)
                draw.line((40, start_y+35, 680, start_y+35), fill=(255,255,255,15))
                start_y += row_h

    # --- 3. VẼ FOOTER (LUÔN HIỆN) ---
    draw.rectangle((0, 1200, 720, 1280), fill=(15, 15, 15, 255)) 
    draw.text((30, 1225), "Product by: Tâm sự 24h - Tài chính & Công nghệ", font=f_s, fill=C_SUB)

    # Chuyển đổi sang mảng Numpy
    return np.array(img)
