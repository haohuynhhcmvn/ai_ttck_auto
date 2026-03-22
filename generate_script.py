
# ==============================
# GENERATE SCRIPT USING GEMINI
# ==============================

import requests
import os
from datetime import datetime

# Lấy API KEY từ biến môi trường
API_KEY = os.getenv("GEMINI_API_KEY")

def generate_script(topic):
    # Tự động lấy ngày hiện tại định dạng DD/MM/YYYY
    today = datetime.now().strftime("%d/%m/%Y")
    
    # Prompt chuyên sâu cho Bản tin Chứng khoán hàng ngày
    prompt = f"""
Bạn là một Biên tập viên Bản tin Tài chính cấp cao. Hãy viết một đoạn lời thoại (Voiceover) 30 giây cho bản tin chứng khoán ngày {today} về chủ đề: "{topic}".

# YÊU CẦU VỀ PHONG CÁCH
- **Mở đầu:** Phải có tên bản tin (Ví dụ: Nhịp đập thị trường, Chứng khoán 24h).
- **Văn phong:** Tin tức, dồn dập, khách quan nhưng sắc sảo. Tốc độ đọc chuyên nghiệp.
- **Ngôn ngữ:** Sử dụng thuật ngữ: VN-Index, thanh khoản, khối ngoại, tự doanh, bùng nổ, lội ngược dòng...

# CẤU TRÚC LỜI THOẠI (STRICTLY VOICEOVER ONLY)
Văn bản trả về là một đoạn nói liền mạch, không chia cảnh, không ký hiệu, bao gồm:
1. Chào sân & Cập nhật chỉ số VN-Index của ngày {today}.
2. Điểm nhấn ngành nóng nhất trong phiên liên quan đến {topic}.
3. Lời khuyên hành động/Chiến lược cho phiên giao dịch kế tiếp.
4. Câu chốt thương hiệu và kêu gọi hành động (CTA).

# RÀNG BUỘC ĐẦU RA
- Chỉ trả về DUY NHẤT lời thoại để đọc.
- Không dùng ký hiệu [Cảnh], không giải thích, không hashtag.
- Độ dài: Khoảng 80 - 120 chữ (tối ưu cho 60 giây nói).
"""

    # URL API (Sử dụng model gemini-1.5-flash để ổn định nhất hiện tại)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={API_KEY}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,  # Giúp lời thoại sáng tạo nhưng vẫn chuẩn mực
            "topP": 0.8,
            "topK": 40
        }
    }

    try:
        res = requests.post(url, json=payload)
        res.raise_for_status() # Kiểm tra lỗi HTTP
        
        # Trích xuất văn bản từ phản hồi của Gemini
        script = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        return script
    except Exception as e:
        return f"Đã xảy ra lỗi khi tạo kịch bản: {e}"
