import unicodedata
import re

def create_ticker_sub(ticker_text, duration_seconds, filename="ticker.ass"):
    """
    Tạo file hiệu ứng chữ chạy ngang (Ticker) chuyên nghiệp.
    """
    # 1. Làm sạch văn bản: Loại bỏ xuống dòng và khoảng trắng thừa
    ticker_text = ticker_text.replace("\n", " ").strip()
    # Loại bỏ các dấu sao (*) nếu AI tóm tắt theo kiểu list
    ticker_text = ticker_text.replace("*", "")
    
    # 2. Chuẩn hóa Unicode NFC và Viết hoa
    clean_content = unicodedata.normalize("NFC", ticker_text).upper()
    
    # Thêm khoảng trống lớn ở đầu và cuối để dòng chữ trôi mượt hơn, không bị ngắt đột ngột
    padding = " " * 10
    full_display = f"{padding}• TÂM SỰ 24H: {clean_content} • DỮ LIỆU TÀI CHÍNH CẬP NHẬT LIÊN TỤC •{padding}"

    # 3. Cấu hình Style
    # Fontsize 38: Vừa đủ đọc trên điện thoại
    # BackColour &H90000000: Tạo dải đen mờ (Semi-transparent) phía sau chữ để dễ đọc trên mọi nền video
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Ticker,DejaVu Sans,38,&H00FFFFFF,&H00000000,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,0,0,2,10,10,70,1
"""
    # 4. Tính toán thời gian
    # Chuyển duration về định dạng ASS: H:MM:SS.cc
    m, s = divmod(int(duration_seconds), 60)
    h, m = divmod(m, 60)
    end_time = f"{h}:{m:02}:{s:02}.00"

    # 5. Hiệu ứng Banner
    # Tham số 15: Tốc độ trôi. 
    # Nếu nội dung của bạn rất dài, hãy giảm xuống 10-12 để chạy nhanh hơn.
    # Nếu nội dung ngắn, để 15-20 cho người ta kịp đọc.
    event_line = f"Dialogue: 0,0:00:00.00,{end_time},Ticker,,0,0,0,Banner;15;0;0,{full_display}"

    with open(filename, "w", encoding="utf-8-sig") as f:
        f.write(header + "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + event_line)
    
    print(f"🎬 Đã tạo file Ticker: {filename}")
    return filename
