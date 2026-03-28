# ==============================
# BLOOMBERG STYLE OVERLAY (LEAN - PRO)
# ==============================

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from datetime import datetime
import pytz  # <--- THÊM THƯ VIỆN NÀY
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
# ==============================
# BLOOMBERG STYLE OVERLAY (VIETNAM TIME READY)
# ==============================

def get_vietnam_now():
    """Lấy thời gian hiện tại chuẩn múi giờ Việt Nam"""
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(tz)

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
    draw.rectangle((0, 0, 720, 100), fill=C_ACCENT)
    draw.text((30, 20), "BẢN TIN CHỨNG KHOÁN", font=f_header, fill="black")
    
    # --- CẬP NHẬT GIỜ VIỆT NAM ---
    now_vn = get_vietnam_now()
    # Hiển thị thêm "ICT" để tăng độ uy tín cho bản tin
    today_str = now_vn.strftime("%H:%M | %d/%m/%Y (ICT)") 
    draw.text((380, 65), today_str, font=f_small, fill="black") # Chỉnh lại tọa độ x một chút để tránh tràn lề

    # --- CONTAINER BACKGROUND ---
    margin_x = 20
    draw.rounded_rectangle((margin_x, 110, 700, 1150), radius=15, fill=C_BG)

    y = 150

    # --- TOP GAINERS ---
    draw.text((50, y), "▲ TOP GAINERS", font=f_section, fill=C_UP)
    y += 70

    # Header cột (Thêm nhãn rõ ràng hơn)
    draw.text((60, y), "MÃ CP", font=f_small, fill=(200, 200, 200))
    draw.text((450, y), "BIẾN ĐỘNG (%)", font=f_small, fill=(200, 200, 200))
    y += 45

    # ... (Phần vòng lặp vẽ gainers/losers giữ nguyên logic cũ của bạn) ...
    # Lưu ý: Trong vòng lặp, hãy đảm bảo hiển thị đúng số thực tế
    for s, v in data.get("gainers", [])[:8]:
        draw.line((60, y+40, 660, y+40), fill=(255, 255, 255, 30), width=1)
        draw.text((60, y), str(s), font=f_ticker, fill=C_WHITE)
        draw.text((450, y), f"+{v}%", font=f_ticker, fill=C_UP)
        y += 65

    # --- PHẦN LOSERS ---
    y += 70 # Khoảng cách giữa 2 bảng
    draw.text((50, y), "▼ TOP LOSERS", font=f_section, fill=C_DOWN)
    y += 70
    
    for s, v in data.get("losers", [])[:8]:
        draw.line((60, y+40, 660, y+40), fill=(255, 255, 255, 30), width=1)
        draw.text((60, y), str(s), font=f_ticker, fill=C_WHITE)
        draw.text((450, y), f"{v}%", font=f_ticker, fill=C_DOWN)
        y += 65

    # --- FOOTER ---
    # Ghi chú dữ liệu theo giờ Việt Nam
    draw.rectangle((0, 1200, 720, 1280), fill=(20, 20, 20, 200))
    footer_text = f"Product by: Tâm sự 24h - Tin tức - Tài chính - Công nghệ"
    draw.text((30, 1225), footer_text, font=f_small, fill=(150, 150, 150))

    return np.array(img)
