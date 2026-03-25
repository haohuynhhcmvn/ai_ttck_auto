# ==============================
# GENERATE SCRIPT (FINAL PRO)
# ==============================

import requests
import os
import time
from datetime import datetime
from market_data import get_vnindex

API_KEY = os.getenv("GEMINI_API_KEY")


def optimize_for_tts(text):
    text = text.replace("VNINDEX", "VN-Index")
    text = text.replace(",", "...")
    text = text.replace(".", "...")
    return text


def call_gemini(payload, retry=3):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    for i in range(retry):
        try:
            res = requests.post(url, json=payload, timeout=30)

            if res.status_code != 200:
                raise Exception(res.text)

            data = res.json()

            if "candidates" not in data:
                raise Exception(data)

            return data["candidates"][0]["content"]["parts"][0]["text"]

        except Exception as e:
            print(f"⚠️ Gemini lỗi lần {i+1}: {e}")
            time.sleep(2 * (i + 1))

    return None


def generate_script(topic):
    today = datetime.now().strftime("%d/%m/%Y")

    data = get_vnindex()

    if isinstance(data, dict) and data.get("close") != "N/A":
        vnindex_text = f"""
            VN-Index đóng cửa tại {data['close']} điểm...
            Biến động {data['change']} điểm...
            """
    else:
        vnindex_text = """
            Hiện chưa có dữ liệu chính xác VN-Index...
            Phân tích xu hướng chung...
            """

    prompt = f"""
            Bạn là chuyên gia tạo nội dung video viral TikTok về tài chính.
            
            DỮ LIỆU THỊ TRƯỜNG:
            {vnindex_text}
            
            MỤC TIÊU:
            Giữ chân người xem >80%
            
            YÊU CẦU CỰC KỲ QUAN TRỌNG:
            
            1. HOOK 3 GIÂY ĐẦU:
            - Gây sốc / tranh cãi / sai lầm
            - Ví dụ: "90% nhà đầu tư đang sai ngay lúc này..."
            
            2. CÂU NGẮN:
            - Mỗi câu 5–10 từ
            - Nhịp nhanh, dồn dập
            
            3. TÂM LÝ:
            - FOMO (sợ bỏ lỡ)
            - SỢ MẤT TIỀN
            - NGHI NGỜ THỊ TRƯỜNG
            
            4. GIỮ LOOP:
            - KHÔNG nói hết ngay
            - Luôn tạo cảm giác "còn gì đó phía sau"
            
            5. DATA:
            - CHỈ dùng dữ liệu đã cung cấp
            - Không bịa số
            
            6. CTA:
            - Không lộ liễu
            - Kiểu: "Ai hiểu sẽ hành động sớm..."
            
            ĐỘ DÀI:
            200–250 chữ
            
            FORMAT:
            - Viết thành đoạn đọc liên tục
            - Không ký hiệu, không hashtag
            """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    script = call_gemini(payload)

    if not script:
        return fallback_script(topic, vnindex_text)

    return optimize_for_tts(script.strip())


def fallback_script(topic, vnindex_text):
    print("⚠️ Dùng fallback script")

    return f"""
            Thị trường đang có biến động mạnh...
            
            {vnindex_text}
            
            Dòng tiền phân hóa rõ rệt...
            
            Nhà đầu tư cần thận trọng...
            
            Theo dõi kênh để cập nhật nhanh nhất...
            """
