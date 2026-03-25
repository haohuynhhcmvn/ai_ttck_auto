# ==============================
# GENERATE SCRIPT (REAL DATA + GEMINI)
# ==============================

import requests
import os
from datetime import datetime
from market_data import get_vnindex  # 🔥 lấy data thật

API_KEY = os.getenv("GEMINI_API_KEY")


# ==============================
# CLEAN TEXT FOR TTS
# ==============================
def optimize_for_tts(text):
    text = text.replace("VNINDEX", "VN-Index")
    text = text.replace(",", "...")
    text = text.replace(".", "...")
    return text


# ==============================
# GENERATE SCRIPT
# ==============================
def generate_script(topic):
    today = datetime.now().strftime("%d/%m/%Y")

    # 🔥 LẤY DATA THẬT
    data = get_vnindex()

    if data:
        vnindex_text = f"""
VN-Index đóng cửa tại {data['close']} điểm.
Biến động {data['change']} điểm trong phiên.
Thanh khoản đạt {data['volume']} cổ phiếu.
"""
    else:
        vnindex_text = """
Hiện chưa có dữ liệu chính xác VN-Index hôm nay.
Hãy phân tích xu hướng chung của thị trường.
"""

    # ==============================
    # PROMPT CHUẨN (ANTI-BỊA DATA)
    # ==============================
    prompt = f"""
Bạn là một Biên tập viên Bản tin Tài chính cấp cao.

DỮ LIỆU THỊ TRƯỜNG HÔM NAY:
{vnindex_text}

YÊU CẦU QUAN TRỌNG:
- CHỈ sử dụng dữ liệu đã cung cấp
- TUYỆT ĐỐI KHÔNG được tự tạo số liệu mới
- Nếu thiếu dữ liệu → chỉ phân tích xu hướng

Nhiệm vụ:
Viết lời thoại bản tin chứng khoán 90 giây cho ngày {today}

Chủ đề: {topic}

YÊU CẦU:
- Văn phong tin tức, nhanh, dồn dập
- Câu ngắn (rất quan trọng cho TTS)
- Có nhịp ngắt tự nhiên (dùng dấu ...)
- Có cảm xúc nhẹ (tăng giữ chân người xem)

CẤU TRÚC:
1. Mở đầu gây chú ý (hook mạnh)
2. Cập nhật VN-Index (dựa trên data thật)
3. Ngành / cổ phiếu nổi bật
4. Chiến lược hành động
5. CTA (follow kênh)

RÀNG BUỘC:
- 200–250 chữ
- Viết thành đoạn đọc liền mạch
- KHÔNG dùng ký hiệu, không hashtag
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.8,
            "topK": 40
        }
    }

    try:
        res = requests.post(url, json=payload, timeout=30)
        res.raise_for_status()

        data_json = res.json()

        # 🔥 DEBUG nếu lỗi quota hoặc response khác
        if "candidates" not in data_json:
            print("⚠️ Gemini lỗi:", data_json)
            return fallback_script(topic, vnindex_text)

        script = data_json["candidates"][0]["content"]["parts"][0]["text"].strip()

        # 🔥 tối ưu cho TTS
        script = optimize_for_tts(script)

        return script

    except Exception as e:
        print("⚠️ Lỗi Gemini:", e)
        return fallback_script(topic, vnindex_text)


# ==============================
# FALLBACK (KHÔNG DÙNG AI)
# ==============================
def fallback_script(topic, vnindex_text):
    print("⚠️ Dùng fallback script")

    return f"""
Nhịp đập thị trường...

Hôm nay, thị trường chứng khoán ghi nhận diễn biến đáng chú ý...

{vnindex_text}

Dòng tiền đang có sự phân hóa mạnh giữa các nhóm ngành...

Nhà đầu tư cần thận trọng trong các quyết định mua mới...
Ưu tiên quản trị rủi ro...

Đừng quên theo dõi kênh để cập nhật nhanh nhất diễn biến thị trường...
"""
