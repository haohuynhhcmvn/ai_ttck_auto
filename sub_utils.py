# ==============================
# TIỆN ÍCH PHỤ ĐỀ (PHIÊN BẢN CHỮ VÀNG ÁNH KIM)
# ==============================

import unicodedata  # Thư viện chuẩn hóa ký tự Unicode
import os           # Thư viện tương tác với hệ thống tệp tin

def create_ticker_sub(ticker_text, duration_seconds, filename="ticker.ass"):
    """
    Tạo tệp phụ đề .ASS với hiệu ứng chữ chạy ngang màu Vàng Gold.
    Nằm chính xác ở dải đen dưới Header (Tọa độ Y: 110-165).
    """
    
    # --- 1. CHUẨN HÓA VÀ LÀM SẠCH NỘI DUNG ---
    # Thay thế xuống dòng bằng khoảng trắng, loại bỏ dấu sao trang trí, xóa khoảng trắng thừa
    clean_text = ticker_text.replace("\n", " ").replace("*", "").strip()
    
    # Chuẩn hóa Unicode sang dạng NFC để hiển thị tiếng Việt không bị lỗi dấu
    clean_text = unicodedata.normalize("NFC", clean_text)
    
    # Chuyển toàn bộ văn bản sang chữ IN HOA để tạo sự trang trọng của bản tin tài chính
    clean_text = clean_text.upper()
    
    # Tạo khoảng trống đệm ở hai đầu để khi chữ chạy hết màn hình sẽ có khoảng nghỉ trước khi lặp lại
    padding = " " * 15
    full_display = f"{padding} • TIN NHANH: {clean_text} • {padding}"

    # --- 2. CẤU HÌNH VỊ TRÍ VÀ MÀU SẮC (PHẦN BẠN CẦN LƯU Ý) ---
    # MarginV tính từ cạnh dưới video (1280px) lên trên. 
    # Con số 1138 đưa tâm chữ vào vùng Y=142px (nằm giữa dải đen 110px-165px).
    margin_v_position = 1138  # <-- TĂNG số này để đẩy chữ lên cao, GIẢM để hạ chữ xuống

    # Mã màu Vàng Ánh Kim (Gold): &H0000D7FF (Định dạng màu trong ASS là &H AABBGGRR - Xanh/Lục/Đỏ)
    # PrimaryColour (&H0000D7FF): Màu vàng Gold rực rỡ
    # OutlineColour (&H00000000): Viền đen giúp chữ nổi bật trên mọi nền video
    
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TickerStyle,DejaVu Sans,34,&H0000D7FF,&H00000000,&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,1,0,2,0,0,{margin_v_position},1
"""

    # --- 3. ĐỊNH DẠNG THỜI GIAN THEO CHUẨN PHỤ ĐỀ (H:MM:SS.cs) ---
    def format_time(seconds):
        # Chia giây thành phút và giây lẻ
        m, s = divmod(float(seconds), 60)
        # Chia phút thành giờ và phút lẻ
        h, m = divmod(m, 60)
        # Trả về định dạng chuẩn cho tệp .ass
        return f"{int(h)}:{int(m):02}:{s:05.2f}"

    # Thời điểm bắt đầu (giây thứ 0)
    start_time = "0:00:00.00"
    # Thời điểm kết thúc (lấy theo tổng thời lượng video)
    end_time = format_time(duration_seconds)

    # --- 4. HIỆU ỨNG CHỮ CHẠY (BANNER) ---
    # Banner;delay;left_to_right;fadeawaywidth
    # delay (15): Tốc độ chạy (số càng nhỏ chạy càng nhanh)
    # left_to_right (0): 1 là chạy từ Trái sang Phải, 0 là Phải sang Trái
    effect = "Banner;18;1;0"

    # --- 5. TẠO DÒNG SỰ KIỆN (EVENT LINE) ---
    # Kết hợp các thành phần thành một dòng Dialogue hoàn chỉnh trong tệp phụ đề
    event_line = f"Dialogue: 0,{start_time},{end_time},TickerStyle,,0,0,0,{effect},{full_display}"

    # --- 6. XUẤT TỆP TIN ---
    try:
        # Ghi tệp với mã hóa utf-8-sig (BOM) để đảm bảo trình render nhận diện đúng ký tự tiếng Việt
        with open(filename, "w", encoding="utf-8-sig") as f:
            f.write(header)                # Ghi phần khai báo Styles
            f.write("\n[Events]\n")        # Ghi tiêu đề mục Sự kiện
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
            f.write(event_line)            # Ghi nội dung chữ chạy
        print(f"✨ Đã tạo xong tệp Ticker màu Vàng tại vị trí MarginV: {margin_v_position}")
    except Exception as e:
        # Thông báo lỗi nếu quá trình ghi tệp thất bại (ví dụ: ổ đĩa đầy hoặc không có quyền ghi)
        print(f"❌ Lỗi khi tạo tệp ASS: {e}")
        return None
    
    return filename # Trả về tên tệp để các hàm khác sử dụng
