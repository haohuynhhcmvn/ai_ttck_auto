import unicodedata
import os
import uuid

def create_ticker_sub(ticker_text, duration_seconds, filename="ticker.ass"):
    # --- 1. LÀM SẠCH NỘI DUNG ---
    clean_text = ticker_text.replace("\n", " ").replace("*", "").strip()
    clean_text = unicodedata.normalize("NFC", clean_text)
    clean_text = clean_text.upper()
    
    # Đệm khoảng trống để chữ không bị dính vào nhau khi lặp
    padding = " " * 10
    full_display = f"{padding} • TIN NHANH: {clean_text} • {padding}"

    # --- 2. CẤU HÌNH VỊ TRÍ (QUAN TRỌNG) ---
    # MarginV cho Alignment 2 (Bottom-Center) là khoảng cách từ CẠNH DƯỚI lên.
    # Để chữ nằm ở vùng Y=140 (gần đỉnh đầu video 1280), MarginV phải khoảng 1140.
    margin_v_position = 1122 

    # --- 3. ĐỊNH DẠNG THỜI GIAN ---
    def format_time(seconds):
        m, s = divmod(float(seconds), 60)
        h, m = divmod(m, 60)
        return f"{int(h)}:{int(m):02}:{s:05.2f}"

    start_time = "0:00:00.00"
    end_time = format_time(duration_seconds)

    # --- 4. HIỆU ỨNG BANNER ---
    # Banner;tốc_độ;hướng;độ_mờ_biên
    # Tốc độ: 15 (càng lớn càng chậm), Hướng: 0 (Phải sang Trái)
    effect = "Banner;15;0;0"

    # --- 5. HEADER VÀ STYLE (ĐÃ SỬA VỊ TRÍ MARGINV) ---
    # Lưu ý: Alignment 2 là căn giữa dưới. MarginV sẽ đẩy nó ngược lên trên.
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TickerStyle,Arial,40,&H0000D7FF,&H00000000,&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,2,0,2,20,20,{margin_v_position},1
"""

    # --- 6. XUẤT TỆP ---
    try:
        with open(filename, "w", encoding="utf-8-sig") as f:
            f.write(header)
            f.write("\n[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            # Layer 0, dùng Effect Banner đã khai báo
            f.write(f"Dialogue: 0,{start_time},{end_time},TickerStyle,,0,0,0,{effect},{full_display}")
        print(f"✨ Ticker ASS tạo thành công: {filename} (Vị trí: {margin_v_position})")
    except Exception as e:
        print(f"❌ Lỗi ghi file: {e}")
        return None
    
    return filename
