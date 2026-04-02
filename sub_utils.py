# ==============================
# SUBTITLE UTILITIES (PRO STABLE - GITHUB ACTIONS READY)
# ==============================

import unicodedata
import os
import re

def create_ticker_sub(ticker_text, duration_seconds, filename="ticker.ass"):
    """
    Tạo file hiệu ứng chữ chạy ngang (Ticker) chuyên nghiệp.
    Tối ưu cho môi trường Linux (GitHub Actions) và chuẩn hóa tốc độ.
    """
    
    # --- 1. CHUẨN HÓA NỘI DUNG (CLEANING) ---
    # Loại bỏ rác từ AI và chuẩn hóa Unicode NFC để tránh lỗi font tiếng Việt
    clean_text = ticker_text.replace("\n", " ").replace("*", "").strip()
    clean_text = unicodedata.normalize("NFC", clean_text)
    
    # Chuyển sang VIẾT HOA và thêm icon phân tách chuyên nghiệp
    clean_text = clean_text.upper()
    
    # Tạo chuỗi lặp để dải chữ không bị trống khi video dài
    # Thêm khoảng trắng lớn (Padding) để chữ đi hết màn hình mới lặp lại
    padding = " " * 20
    full_display = f"{padding} • BẢN TIN TÀI CHÍNH CẬP NHẬT: {clean_text} • {padding}"

    # --- 2. CẤU HÌNH STYLE (HÀI HÒA VỚI VIDEO 9:16) ---
    # Fontname: 'DejaVu Sans' hoặc 'Liberation Sans' thường có sẵn trên Ubuntu/GHA.
    # BackColour: &H80000000 (Nền đen mờ 50%) giúp chữ trắng nổi bật trên mọi nền video.
    # Alignment 2: Căn lề dưới chính giữa (Bottom Center) để không che mặt MC.
    # MarginV 100: Đẩy lên một chút so với mép dưới (khoảng 1/10 màn hình).
    
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TickerStyle,DejaVu Sans,38,&H00FFFFFF,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,0,0,2,20,20,100,1
"""

    # --- 3. TÍNH TOÁN THỜI GIAN ---
    # Định dạng ASS yêu cầu H:MM:SS.cs (0:00:15.00)
    def format_time(seconds):
        m, s = divmod(float(seconds), 60)
        h, m = divmod(m, 60)
        return f"{int(h)}:{int(m):02}:{s:05.2f}"

    start_time = "0:00:00.00"
    end_time = format_time(duration_seconds)

    # --- 4. TÍNH TOÁN TỐC ĐỘ CHẠY (DYNAMIC SPEED) ---
    # Công thức: Tốc độ = (Độ dài chuỗi chữ / Thời gian video)
    # Tuy nhiên, hiệu ứng Banner trong ASS dùng tham số 'delay'. 
    # Delay càng nhỏ -> Chạy càng nhanh. 
    # Giá trị 15-25 là vừa phải cho tin tức chứng khoán.
    
    char_count = len(full_display)
    if char_count > 200:
        speed = 10 # Chạy nhanh hơn nếu tin quá dài
    else:
        speed = 18 # Chạy thong thả nếu tin ngắn
        
    # Cấu trúc Effect: Banner;delay;left_to_right;fadeawaywidth
    # left_to_right = 0 nghĩa là chạy từ PHẢI sang TRÁI
    effect = f"Banner;{speed};0;0"

    # --- 5. TẠO EVENT LINE ---
    event_line = f"Dialogue: 0,{start_time},{end_time},TickerStyle,,0,0,0,{effect},{full_display}"

    # --- 6. XUẤT FILE VỚI UTF-8-SIG (Để phần mềm Render nhận diện đúng BOM) ---
    try:
        with open(filename, "w", encoding="utf-8-sig") as f:
            f.write(header)
            f.write("\n[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            f.write(event_line)
        print(f"✅ Ticker ASS Created: {filename} ({char_count} chars, Speed: {speed})")
    except Exception as e:
        print(f"❌ Error creating ASS: {e}")
        return None
    
    return filename

# --- TEST ---
if __name__ == "__main__":
    # Giả định video dài 15 giây
    test_text = "Thị trường bùng nổ, SSI tăng trần, VN-Index vượt 1250 điểm với thanh khoản cực lớn."
    create_ticker_sub(test_text, 15)
