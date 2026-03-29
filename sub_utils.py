import unicodedata

def create_ticker_sub(ticker_text, duration_seconds, filename="ticker.ass"):
    """
    Tạo file hiệu ứng chữ chạy ngang (Ticker) từ phải sang trái.
    ticker_text: Nội dung tin vắn quan trọng đã được AI tóm tắt.
    """
    # 1. Chuẩn hóa Unicode NFC để tránh lỗi font tiếng Việt trên Linux
    clean_content = unicodedata.normalize("NFC", ticker_text).upper()
    
    # Thêm dải phân cách và thương hiệu
    full_display = f"  •  TÂM SỰ 24H: {clean_content}  •  DỮ LIỆU TÀI CHÍNH CẬP NHẬT LIÊN TỤC  •  "

    # 2. Cấu hình Style Bloomberg/TikTok
    # Alignment 2: Nằm dưới đáy màn hình
    # MarginV 60: Khoảng cách từ đáy lên để không bị che bởi thanh công cụ TikTok
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Ticker,DejaVu Sans,38,&H00FFFFFF,&H00000000,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,0,0,2,20,20,60,1
"""
    # Tính thời gian kết thúc video
    m, s = divmod(int(duration_seconds), 60)
    h, m = divmod(m, 60)
    end_time = f"{h}:{m:02}:{s:02}.00"

    # Hiệu ứng Banner;tốc độ 15 (vừa mắt);0 (phải sang trái)
    event_line = f"Dialogue: 0,0:00:00.00,{end_time},Ticker,,0,0,0,Banner;15;0;0,{full_display}"

    with open(filename, "w", encoding="utf-8-sig") as f:
        f.write(header + "\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n" + event_line)
    
    return filename
