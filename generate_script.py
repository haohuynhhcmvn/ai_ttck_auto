# ==============================
# GENERATE SCRIPT (FINAL PRO - SSI DATA)
# ==============================

import requests
import os
import time
from datetime import datetime
from market_data import get_market_data  # ✅ dùng data chuẩn

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
# CALL GEMINI (RETRY)
# ==============================
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


# ==============================
# MAIN GENERATE SCRIPT
# ==============================
def generate_script(topic):
    today = datetime.now().strftime("%d/%m/%Y")

    # 🔥 LẤY DATA THẬT
    data = get_market_data()

    vn = data.get("vnindex", {})
    vn30 = data.get("vn30", {})
    gainers = data.get("gainers", [])[:3]
    losers = data.get("losers", [])[:3]

    # ==============================
    # BUILD TEXT DATA (ANTI FAKE)
    # ==============================
    if vn.get("close") != "N/A":
        vn_text = f"""
VN-Index: {vn.get('close')} điểm...
Biến động: {vn.get('change')} điểm...
"""
    else:
        vn_text = "Chưa có dữ liệu VN-Index..."

    if vn30.get("close") != "N/A":
        vn30_text = f"VN30: {vn30.get('close')} điểm..."
    else:
        vn30_text = ""

    gain_text = ", ".join([f"{s} {v}%" for s, v in gainers]) if gainers else ""
    lose_text = ", ".join([f"{s} {v}%" for s, v in losers]) if losers else ""

    # ==============================
    # PROMPT VIRAL
    # ==============================
    prompt = f"""
Bạn là chuyên gia tạo video tài chính viral.

DỮ LIỆU THỊ TRƯỜNG:
{vn_text}
{vn30_text}

Top tăng: {gain_text}
Top giảm: {lose_text}

YÊU CẦU:

1. HOOK cực mạnh 3 giây đầu
2. Gây FOMO + sợ mất tiền
3. Không nói hết → giữ người xem
4. Câu ngắn 5–10 từ
5. Không bịa data

ĐỘ DÀI: 200–250 chữ

FORMAT:
- Đọc liên tục
- Không ký hiệu
- Không hashtag

Chủ đề: {topic}
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    script = call_gemini(payload)

    if not script:
        return fallback_script(topic, vn_text)

    return optimize_for_tts(script.strip())


# ==============================
# FALLBACK (KHÔNG AI)
# ==============================
def fallback_script(topic, vn_text):
    print("⚠️ Dùng fallback script")

    return f"""
90% nhà đầu tư đang hiểu sai thị trường...

{vn_text}

Dòng tiền đang dịch chuyển âm thầm...

Top cổ phiếu bắt đầu phân hóa mạnh...

Nếu bạn vào sai nhịp...

Tài khoản sẽ bốc hơi rất nhanh...

Nhưng nếu hiểu đúng dòng tiền...

Cơ hội vẫn còn phía trước...

Ai hiểu sẽ hành động sớm...
"""
