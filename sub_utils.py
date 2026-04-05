import unicodedata
import os
import uuid

def create_ticker_sub(ticker_text, duration_seconds, filename="ticker.ass"):
    # --- 1. LÀM SẠCH NỘI DUNG (GIỮ NGUYÊN) ---
    # Chuyển về NFC để đảm bảo các dấu tiếng Việt không bị tách rời (như chữ 'ả' không bị thành 'a' + '?' )
    clean_text = ticker_text.replace("\n", " ").replace("*", "").strip()
    clean_text = unicodedata.normalize("NFC", clean_text)
    clean_text = clean_text.upper()
    
    padding = " " * 10
    full_display = f"{padding} • TIN NHANH: {clean_text} • {padding}"

    # --- 2. CẤU HÌNH VỊ TRÍ ---
    margin_v_position = 1122 

    # --- 3. ĐỊNH DẠNG THỜI GIAN ---
    def format_time(seconds):
        m, s = divmod(float(seconds), 60)
        h, m = divmod(m, 60)
        return f"{int(h)}:{int(m):02}:{s:05.2f}"

    start_time = "0:00:00.00"
    end_time = format_time(duration_seconds)

    # --- 4. HIỆU ỨNG BANNER ---
    effect = "Banner;15;0;0"

    # --- 5. HEADER VÀ STYLE ---
    # THAY ĐỔI: Chuyển Encoding cuối dòng Style thành 1 (Mặc định cho Unicode/UTF-8 trong ASS)
    header = f"""[Script Info]
Title: Ticker Auto Generated
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TickerStyle,Arial,40,&H0000D7FF,&H00000000,&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,2,0,2,20,20,{margin_v_position},1
"""

    # --- 6. XUẤT TỆP (ĐIỂM FIX CHÍNH) ---
    try:
        # SỬA: Dùng "utf-8" thuần thay vì "utf-8-sig" để FFmpeg trên Linux đọc tốt nhất
        with open(filename, "w", encoding="utf-8") as f:
            f.write(header)
            f.write("\n[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            # Đảm bảo dòng Dialogue ghi đúng định dạng
            line = f"Dialogue: 0,{start_time},{end_time},TickerStyle,,0,0,0,{effect},{full_display}"
            f.write(line)
            
        print(f"✨ Ticker ASS tạo thành công: {filename}")
    except Exception as e:
        print(f"❌ Lỗi ghi file: {e}")
        return None
    
    return filename
