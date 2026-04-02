# ==============================
# BLOOMBERG STYLE OVERLAY (PRO VERSION - OPTIMIZED)
# ==============================

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from datetime import datetime
import pytz
import platform

# ==============================
# SMART FONT LOADER
# ==============================
def load_font(size, bold=False):
    system = platform.system()
    if system == "Windows":
        fonts = ["arialbd.ttf" if bold else "arial.ttf", "calibrib.ttf"]
    else:
        # Font cho GitHub Actions / Docker (DejaVuSans là chuẩn nhất)
        fonts = [
            f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
            "/usr/share/fonts/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/liberation/LiberationSans.ttf"
        ]
    
    for f in fonts:
        try:
            return ImageFont.truetype(f, size)
        except:
            continue
    return ImageFont.load_default()

# ==============================
# COLOR PALETTE (BLOOMBERG)
# ==============================
C_ACCENT = (255, 153, 0)    # Cam Bloomberg đặc trưng
C_BG_BOX = (15, 15, 15, 180) # Nền đen phủ mờ (Glassmorphism nhẹ)
C_UP = (0, 255, 150)        # Xanh Emerald
C_DOWN = (255, 60, 60)      # Đỏ rực
C_WHITE = (255, 255, 255, 255)
C_SUB = (180, 180, 180, 255) # Màu chữ phụ

def get_vietnam_now():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(tz)

# ==============================
# MAIN DRAW FUNCTION
# ==============================
def draw_overlay(data, size=(720, 1280)):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Load Fonts
    f_h1 = load_font(42, bold=True)
    f_h2 = load_font(36, bold=True)
    f_body = load_font(32, bold=True)
    f_small = load_font(24)
    f_tiny = load_font(20)

    # --- 1. HEADER BAR (0 -> 110px) ---
    draw.rectangle((0, 0, 720, 110), fill=C_ACCENT)
    draw.text((30, 15), "BẢN TIN TÀI CHÍNH 247", font=f_h1, fill="black")
    
    now_vn = get_vietnam_now()
    time_str = now_vn.strftime("%H:%M  •  %d/%m/%Y (ICT)")
    draw.text((30, 68), time_str, font=f_small, fill=(40, 40, 40))

    # --- 2. MAIN CONTAINER ---
    # Vẽ khung chứa nội dung chính
    draw.rounded_rectangle((25, 130, 695, 1180), radius=20, fill=C_BG_BOX)

    # --- 3. TOP GAINERS SECTION ---
    curr_y = 160
    draw.text((50, curr_y), "▲ TOP CỔ PHIẾU TĂNG TRƯỞNG", font=f_h2, fill=C_UP)
    curr_y += 65
    
    # Header cột
    draw.text((70, curr_y), "MÃ CP", font=f_tiny, fill=C_SUB)
    draw.text((480, curr_y), "BIẾN ĐỘNG (%)", font=f_tiny, fill=C_SUB)
    curr_y += 35

    # Vòng lặp vẽ Gainers (Tối đa 10 mã để cân đối)
    gainers = data.get("gainers", [])[:10]
    for symbol, pct in gainers:
        # Đường kẻ chia dòng mờ
        draw.line((60, curr_y + 42, 660, curr_y + 42), fill=(255, 255, 255, 25), width=1)
        # Mã CP
        draw.text((70, curr_y), str(symbol), font=f_body, fill=C_WHITE)
        # % Tăng (Thêm dấu + phía trước)
        txt_pct = f"+{pct}%" if pct > 0 else f"{pct}%"
        draw.text((480, curr_y), txt_pct, font=f_body, fill=C_UP)
        curr_y += 52

    # --- 4. TOP LOSERS SECTION ---
    # Tự động nhảy xuống cách đoạn Tăng một khoảng hợp lý
    curr_y += 60 
    draw.text((50, curr_y), "▼ TOP CỔ PHIẾU GIẢM ĐIỂM", font=f_h2, fill=C_DOWN)
    curr_y += 65
    
    draw.text((70, curr_y), "MÃ CP", font=f_tiny, fill=C_SUB)
    draw.text((480, curr_y), "BIẾN ĐỘNG (%)", font=f_tiny, fill=C_SUB)
    curr_y += 35

    losers = data.get("losers", [])[:10]
    for symbol, pct in losers:
        draw.line((60, curr_y + 42, 660, curr_y + 42), fill=(255, 255, 255, 25), width=1)
        draw.text((70, curr_y), str(symbol), font=f_body, fill=C_WHITE)
        draw.text((480, curr_y), f"{pct}%", font=f_body, fill=C_DOWN)
        curr_y += 52

    # --- 5. FOOTER (Dưới cùng) ---
    # Thanh ngang chân trang
    draw.rectangle((0, 1200, 720, 1280), fill=(10, 10, 10, 220))
    footer_main = "NGUỒN DỮ LIỆU: REAL-TIME MARKET DATA (HOSE/HNX)"
    footer_sub = "Product by: Tâm sự 24h • Tin tức - Tài chính - Công nghệ"
    
    draw.text((30, 1215), footer_main, font=f_tiny, fill=C_SUB)
    draw.text((30, 1245), footer_sub, font=f_tiny, fill=(100, 100, 100))

    return np.array(img)
