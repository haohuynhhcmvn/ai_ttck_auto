from PIL import Image, ImageDraw, ImageFont
import numpy as np
from datetime import datetime
import pytz
import platform
import os

# ==============================================================
# BẢNG MÀU PHONG CÁCH BLOOMBERG (Tạo cảm giác chuyên nghiệp, tin cậy)
# ==============================================================
C_ACCENT = (255, 153, 0)        # Màu cam thương hiệu (Headline)
C_BG_BOX = (10, 10, 10, 180)    # Nền bảng đen mờ (Glassmorphism)
C_TICKER_BG = (0, 0, 0, 220)    # Nền đen đậm cho dải chạy Ticker
C_UP = (0, 255, 150)            # Màu xanh lục (Thị trường tăng)
C_DOWN = (255, 60, 60)          # Màu đỏ (Thị trường giảm)
C_WHITE = (255, 255, 255, 255)  # Chữ trắng chính
C_SUB = (170, 170, 170, 255)    # Chữ xám phụ (Caption)

# Cấu hình tọa độ X cho các cột (Giúp căn lề thẳng hàng như Excel)
COL_X = {"SYM": 45, "PRICE": 240, "PCT": 430, "VOL": 680}

def load_font(size, bold=False):
    """
    Tự động tìm font phù hợp trên Windows và Linux (GitHub Actions).
    """
    system = platform.system()
    # Đường dẫn font mặc định trên Ubuntu (GHA thường dùng Ubuntu)
    f_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    
    if system == "Windows":
        f_path = "arialbd.ttf" if bold else "arial.ttf"
    
    try: 
        return ImageFont.truetype(f_path, size)
    except: 
        # Nếu không tìm thấy font hệ thống, dùng font mặc định của Pillow
        return ImageFont.load_default()

def format_vol(v):
    """
    Rút gọn số khối lượng (Ví dụ: 1.200.000 -> 1.2M, 5.000 -> 5K)
    """
    try:
        v = float(v)
        if v >= 1e6: return f"{v/1e6:.1f}M"
        if v >= 1e3: return f"{v/1e3:.0f}K"
        return f"{v:,.0f}"
    except:
        return str(v)

def draw_overlay(data, size=(720, 1280)):
    """
    HÀM VẼ CHÍNH: Tạo tấm ảnh trong suốt chứa bảng điện chứng khoán.
    """
    # 1. Tạo phôi ảnh RGBA trong suốt hoàn toàn (0, 0, 0, 0)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Khởi tạo các cỡ Font
    f_h = load_font(40, True)       # Font tiêu đề lớn
    f_b = load_font(22, True)       # Font dữ liệu bảng
    f_s = load_font(20)             # Font chú thích nhỏ
    f_title = load_font(30, True)   # Font nhóm Tăng/Giảm

    # --- PHẦN 1: VẼ HEADER (THANH TIÊU ĐỀ TRÊN) ---
    # Vẽ hình chữ nhật màu cam trên cùng
    draw.rectangle((0, 0, 720, 110), fill=C_ACCENT) 
    draw.text((30, 15), "BẢN TIN TÀI CHÍNH 247", font=f_h, fill="black")
    
    # Lấy thời gian hiện tại Việt Nam
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    vn_t = datetime.now(vn_tz).strftime("%H:%M | %d/%m/%Y")
    draw.text((30, 70), vn_t, font=f_s, fill=(40, 40, 40))

    # Thanh đen nhỏ dưới tiêu đề
    draw.rectangle((0, 110, 720, 165), fill=C_TICKER_BG)

    # --- PHẦN 2: VẼ BẢNG DỮ LIỆU CHÍNH ---
    # Vẽ khung bo góc mờ (Glassmorphism)
    draw.rounded_rectangle((25, 175, 695, 1185), radius=15, fill=C_BG_BOX)

    gainers = data.get("gainers", [])
    losers = data.get("losers", [])
    start_y = 200 # Tọa độ Y bắt đầu vẽ
    
    # --- VẼ NHÓM CỔ PHIẾU TĂNG ---
    if gainers:
        draw.text((45, start_y), "▲ TOP CỔ PHIẾU TĂNG TRƯỞNG", font=f_title, fill=C_UP)
        start_y += 55
        # Vẽ tiêu đề cột (Mã, Giá, %, Vol)
        for k, x in [("MÃ", COL_X["SYM"]), ("GIÁ", COL_X["PRICE"]), ("%", COL_X["PCT"]), ("VOL", COL_X["VOL"]-50)]:
            draw.text((x, start_y), k, font=f_s, fill=C_SUB)
        
        start_y += 35
        for item in gainers[:8]: # Giới hạn 8 mã để không bị tràn khung
            # Vẽ Mã chứng khoán
            draw.text((COL_X["SYM"], start_y), str(item['symbol']), font=f_b, fill=C_WHITE)
            # Vẽ Giá (Định dạng có dấu phẩy)
            draw.text((COL_X["PRICE"], start_y), f"{item['price']:,}", font=f_b, fill=C_WHITE)
            # Vẽ % Thay đổi (Màu xanh)
            draw.text((COL_X["PCT"], start_y), f"+{item['change']}%", font=f_b, fill=C_UP)
            # Vẽ Khối lượng (Căn lề phải)
            v_txt = format_vol(item['volume'])
            v_x = COL_X["VOL"] - draw.textlength(v_txt, f_b)
            draw.text((v_x, start_y), v_txt, font=f_b, fill=C_WHITE)
            
            # Vẽ đường kẻ ngang mờ phân cách các hàng
            draw.line((40, start_y+35, 680, start_y+35), fill=(255,255,255,20))
            start_y += 40 # Khoảng cách dòng

    start_y += 40 # Khoảng cách giữa 2 nhóm Tăng/Giảm

    # --- VẼ NHÓM CỔ PHIẾU GIẢM ---
    if losers:
        draw.text((45, start_y), "▼ TOP CỔ PHIẾU GIẢM ĐIỂM", font=f_title, fill=C_DOWN)
        start_y += 55
        for k, x in [("MÃ", COL_X["SYM"]), ("GIÁ", COL_X["PRICE"]), ("%", COL_X["PCT"]), ("VOL", COL_X["VOL"]-50)]:
            draw.text((x, start_y), k, font=f_s, fill=C_SUB)
        
        start_y += 35
        for item in losers[:8]:
            draw.text((COL_X["SYM"], start_y), str(item['symbol']), font=f_b, fill=C_WHITE)
            draw.text((COL_X["PRICE"], start_y), f"{item['price']:,}", font=f_b, fill=C_WHITE)
            draw.text((COL_X["PCT"], start_y), f"{item['change']}%", font=f_b, fill=C_DOWN)
            v_txt = format_vol(item['volume'])
            v_x = COL_X["VOL"] - draw.textlength(v_txt, f_b)
            draw.text((v_x, start_y), v_txt, font=f_b, fill=C_WHITE)
            
            draw.line((40, start_y+35, 680, start_y+35), fill=(255,255,255,20))
            start_y += 40

    # --- PHẦN 3: VẼ FOOTER (THANH DƯỚI CÙNG) ---
    draw.rectangle((0, 1200, 720, 1280), fill=(15, 15, 15, 255)) 
    draw.text((30, 1225), "Product by: Tâm sự 24h - Tài chính & Công nghệ", font=f_s, fill=C_SUB)

    # Chuyển đổi từ đối tượng ảnh Pillow sang mảng Numpy để FFmpeg/MoviePy đọc được
    return np.array(img)
