import unicodedata
import os

def create_ticker_sub(ticker_text, duration_seconds, filename="ticker.ass"):
    """
    Nhận nội dung tóm tắt và tạo file ASS chạy ngang.
    ticker_text: Nội dung ngắn gọn đã được AI lọc ra.
    """
    # 1. Chuẩn hóa tiếng Việt và viết hoa
    clean_content = unicodedata.normalize("NFC", ticker_text).upper()
    
    # Thêm ký hiệu ngăn cách và Brand
    full_display = f"  •  TÂM SỰ 24H: {clean_content}  •  TIN TỨC CẬP NHẬT LIÊN TỤC  •  "

    # 2. Cấu hình Style (Font DejaVu Sans để không lỗi trên Linux)
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Ticker,DejaVu Sans,38,&H00FFFFFF,&H00000000,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,0,0,2,20,20,60,1
"""
    m, s = divmod(int(duration_seconds), 60)
    h, m = divmod(m, 60)
    end_time = f"{h}:{m:02}:{s:02}.00"

    # Hiệu ứng Banner;tốc độ 15;0 (phải sang trái)
    event_line = f"Dialogue: 0,0:00:00.00,{end_time},Ticker,,0,0,0,Banner;15;0;0,{full_display}"

    with open(filename, "w", encoding="utf-8-sig") as f:
        f.write(header + "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + event_line)
    
    return filename
