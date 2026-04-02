from PIL import Image, ImageDraw, ImageFont
import numpy as np
from datetime import datetime
import pytz
import platform

# --- BẢNG MÀU PHONG CÁCH BLOOMBERG ---
C_ACCENT = (255, 153, 0)       # Màu cam thương hiệu (Header)
C_BG_BOX = (10, 10, 10, 180)   # Nền đen mờ cho nội dung chính (Glassmorphism)
C_TICKER_BG = (0, 0, 0, 220)    # Nền đen đậm cho dải chữ chạy Ticker
C_UP = (0, 255, 150)           # Màu xanh lục cho thị trường tăng
C_DOWN = (255, 60, 60)         # Màu đỏ cho thị trường giảm
C_WHITE = (255, 255, 255, 255) # Màu trắng thuần
C_SUB = (170, 170, 170, 255)   # Màu xám cho các tiêu đề phụ/đường kẻ

# --- CẤU HÌNH TỌA ĐỘ CỘT (Trục X) ---
COL_X = {"SYM": 45, "PRICE": 240, "PCT": 430, "VOL": 680}

def load_font(size, bold=False):
    """Hàm tải font hệ thống linh hoạt cho Linux (GHA) và Windows"""
    system = platform.system()
    # Đường dẫn font mặc định trên Ubuntu (GitHub Actions)
    f_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    # Đường dẫn font trên Windows để test máy cá nhân
    if system == "Windows": f_path = "arialbd.ttf" if bold else "arial.ttf"
    try: 
        return ImageFont.truetype(f_path, size)
    except: 
        return ImageFont.load_default()

def format_vol(v):
    """Định dạng số khối lượng (V) sang dạng rút gọn K, M hoặc phân cách hàng nghìn"""
    if v >= 1e6: return f"{v/1e6:.1f}M"
    if v >= 1e3: return f"{v/1e3:.0f}K"
    return f"{v:,.0f}"

def draw_overlay(data, size=(720, 1280)):
    """Hàm chính vẽ lớp phủ (overlay) lên video 9:16"""
    # Tạo ảnh nền trong suốt RGBA
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Khởi tạo các cỡ font chữ khác nhau
    f_h = load_font(42, True)      # Font Header chính
    f_b = load_font(22, True)      # Font nội dung bảng (In đậm)
    f_s = load_font(18)            # Font tiêu đề cột/phụ
    f_title = load_font(32, True)  # Font tiêu đề nhóm (Top Tăng/Giảm)

    # --- 1. VẼ HEADER (Phần đầu bản tin) ---
    draw.rectangle((0, 0, 720, 110), fill=C_ACCENT) # Nền cam
    draw.text((30, 15), "BẢN TIN TÀI CHÍNH 247", font=f_h, fill="black")
    # Lấy giờ thực tế Việt Nam
    vn_t = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime("%H:%M | %d/%m/%Y")
    draw.text((30, 70), vn_t, font=f_s, fill=(40, 40, 40))

    # --- 2. VẼ SUB HEADER (Nền cho chữ chạy Ticker) ---
    # Nằm ngay dưới chân Header (Y từ 110 đến 165)
    draw.rectangle((0, 110, 720, 165), fill=C_TICKER_BG)

    # --- 3. VẼ KHUNG NỘI DUNG CHÍNH (Nền mờ) ---
    # Giúp market data nổi bật trên nền video slideshow
    draw.rounded_rectangle((25, 175, 695, 1185), radius=15, fill=C_BG_BOX)

    gainers = data.get("gainers", [])
    losers = data.get("losers", [])
    
    start_y = 200 # Điểm bắt đầu vẽ theo trục Y
    row_h = 36    # Chiều cao mỗi dòng dữ liệu
    
    # --- VẼ NHÓM CỔ PHIẾU TĂNG ---
    if gainers:
        draw.text((45, start_y), "▲ TOP CỔ PHIẾU TĂNG TRƯỞNG", font=f_title, fill=C_UP)
        start_y += 55
        # Vẽ tiêu đề các cột (MÃ, GIÁ, %, VOL)
        for k, x in [("MÃ", COL_X["SYM"]), ("GIÁ", COL_X["PRICE"]), ("%", COL_X["PCT"]), ("VOL", COL_X["VOL"]-50)]:
            draw.text((x, start_y), k, font=f_s, fill=C_SUB)
        start_y += 35
        
        for item in gainers:
            # Vẽ Mã chứng khoán
            draw.text((COL_X["SYM"], start_y), item['symbol'], font=f_b, fill=C_WHITE)
            # Vẽ Giá (đã thêm phân cách hàng nghìn)
            p_txt = f"{item['price']:,}"
            draw.text((COL_X["PRICE"], start_y), p_txt, font=f_b, fill=C_WHITE)
            # Vẽ % thay đổi
            draw.text((COL_X["PCT"], start_y), f"+{item['change']}%", font=f_b, fill=C_UP)
            # Vẽ Khối lượng (căn lề phải dựa trên độ dài chữ)
            v_txt = format_vol(item['volume'])
            draw.text((COL_X["VOL"] - draw.textlength(v_txt, f_b), start_y), v_txt, font=f_b, fill=C_WHITE)
            # Vẽ đường kẻ ngang phân cách mờ
            draw.line((40, start_y+35, 680, start_y+35), fill=(255,255,255,15))
            start_y += row_h

    start_y += 36 # Khoảng cách giữa 2 bảng

    # --- VẼ NHÓM CỔ PHIẾU GIẢM ---
    if losers:
        draw.text((45, start_y), "▼ TOP CỔ PHIẾU GIẢM ĐIỂM", font=f_title, fill=C_DOWN)
        start_y += 55
        for k, x in [("MÃ", COL_X["SYM"]), ("GIÁ", COL_X["PRICE"]), ("%", COL_X["PCT"]), ("VOL", COL_X["VOL"]-50)]:
            draw.text((x, start_y), k, font=f_s, fill=C_SUB)
        start_y += 35
        
        for item in losers:
            draw.text((COL_X["SYM"], start_y), item['symbol'], font=f_b, fill=C_WHITE)
            # Vẽ Giá (đã thêm phân cách hàng nghìn)
            p_txt = f"{item['price']:,}"
            draw.text((COL_X["PRICE"], start_y), p_txt, font=f_b, fill=C_WHITE)
            # Vẽ % thay đổi (Màu đỏ)
            draw.text((COL_X["PCT"], start_y), f"{item['change']}%", font=f_b, fill=C_DOWN)
            # Vẽ Khối lượng
            v_txt = format_vol(item['volume'])
            draw.text((COL_X["VOL"] - draw.textlength(v_txt, f_b), start_y), v_txt, font=f_b, fill=C_WHITE)
            # Vẽ đường kẻ ngang
            draw.line((40, start_y+35, 680, start_y+35), fill=(255,255,255,15))
            start_y += row_h

    # --- 4. VẼ FOOTER (Phần cuối chân trang) ---
    draw.rectangle((0, 1200, 720, 1280), fill=(15, 15, 15, 255)) # Nền đen đặc
    draw.text((30, 1225), "Product by: Tâm sự 24h - Tài chính & Công nghệ", font=f_s, fill=C_SUB)

    # Chuyển đổi ảnh từ Pillow sang mảng Numpy để MoviePy có thể đọc được
    return np.array(img)
