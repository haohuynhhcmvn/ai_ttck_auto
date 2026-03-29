import unicodedata
import os

def create_ticker_sub(ticker_text, duration_seconds, filename="ticker.ass"):
    """
    Tạo file hiệu ứng chữ chạy ngang (Ticker) ở CHÍNH GIỮA màn hình.
    ticker_text: Nội dung tin vắn từ AI.
    duration_seconds: Thời lượng video để khớp tốc độ chạy.
    """
    
    # --- 1. XỬ LÝ NỘI DUNG (CLEANING) ---
    # Loại bỏ xuống dòng, dấu sao, khoảng trắng thừa
    clean_text = ticker_text.replace("\n", " ").replace("*", "").strip()
    # Chuẩn hóa Unicode NFC (Tránh lỗi font tiếng Việt trên Linux/Server)
    clean_text = unicodedata.normalize("NFC", clean_text).upper()
    
    # Thêm khoảng trống (Padding) lớn ở hai đầu để tạo vòng lặp mượt mà
    padding = " " * 15
    full_display = f"{padding}• TIN TỨC CẬP NHẬT: {clean_text} • DỮ LIỆU TÀI CHÍNH CẬP NHẬT LIÊN TỤC •{padding}"

    # --- 2. CẤU HÌNH STYLE (CHÍNH GIỮA MÀN HÌNH) ---
    # Alignment 5: Chính giữa tâm video (Middle Center)
    # MarginV 0: Không lệch lên hay xuống so với tâm
    # BackColour &H90000000: Dải nền đen mờ 56% giúp chữ trắng nổi bật
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TickerStyle,DejaVu Sans,40,&H00FFFFFF,&H00000000,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,0,0,5,10,10,0,1
"""

    # --- 3. TÍNH TOÁN THỜI GIAN ---
    m, s = divmod(int(duration_seconds), 60)
    h, m = divmod(m, 60)
    end_time = f"{h}:{m:02}:{s:02}.00"

    # --- 4. HIỆU ỨNG BANNER (TỪ PHẢI QUA TRÁI) ---
    # Tham số 15: Tốc độ trôi (Số càng nhỏ chạy càng nhanh)
    # 0;0: Chạy từ phải sang trái
    event_line = f"Dialogue: 0,0:00:00.00,{end_time},TickerStyle,,0,0,0,Banner;15;0;0,{full_display}"

    # --- 5. XUẤT FILE ---
    with open(filename, "w", encoding="utf-8-sig") as f:
        f.write(header + "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + event_line)
    
    print(f"✅ Đã tạo file Ticker tại tâm video: {filename}")
    return filename
