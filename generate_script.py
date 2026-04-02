# ==============================
# GENERATE SCRIPT PRO MAX (DYNAMIC ENGINE)
# ==============================

import requests
import os
import time
import re
import random
from datetime import datetime
from num2words import num2words

# Import giả định - Đảm bảo các file này tồn tại trong repo của bạn
try:
    from market_data import get_market_data
except ImportError:
    def get_market_data(): return {"gain_text": "VN-Index tăng nhẹ", "lose_text": "Nhóm Bất động sản chỉnh"}

# ==============================
# CONFIG & API KEYS
# ==============================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

QWEN_MODEL = "qwen/qwen3.5-122b-a10b"
GEMINI_MODEL = "gemini-2.0-flash" # Cập nhật model mới nhất nếu có thể

# ==============================
# DYNAMIC PERSONA CONFIG (Chống rập khuôn)
# ==============================
STYLES = [
    {
        "name": "Sát thủ thị trường", 
        "tone": "Góc nhìn thực tế, hơi phũ, tập trung vào bẫy tâm lý và sự khốc liệt.",
        "hook_type": "Đánh thẳng vào nỗi sợ hoặc sự mất mát của đám đông."
    },
    {
        "name": "Chuyên gia điềm tĩnh", 
        "tone": "Phân tích logic, dùng số liệu vĩ mô, ngôn ngữ chuyên nghiệp nhưng dễ hiểu.",
        "hook_type": "Đưa ra một con số thống kê gây kinh ngạc."
    },
    {
        "name": "Người kể chuyện (Storyteller)", 
        "tone": "Dùng ẩn dụ (về bờ, cá mập, săn mồi), ngôn ngữ đời thường của dân trading.",
        "hook_type": "Bắt đầu bằng một tình huống giả định mà ai cũng từng gặp."
    }
]

# ==============================
# NUMBER NORMALIZATION
# ==============================
def read_decimal_or_int(num_str):
    num_str = num_str.replace(",", "")
    try:
        if '.' in num_str:
            integer, decimal = num_str.split(".")
            int_part = num2words(int(integer), lang='vi')
            dec_part = ' '.join([num2words(int(d), lang='vi') for d in decimal])
            return f"{int_part} phẩy {dec_part}"
        else:
            return num2words(int(num_str), lang='vi')
    except:
        return num_str

def normalize_numbers(text):
    text = re.sub(r'(\d+(\.\d+)?)%', lambda m: read_decimal_or_int(m.group(1)) + " phần trăm", text)
    text = re.sub(r'(\d{1,3}(?:,\d{3})+)', lambda m: num2words(int(m.group().replace(",", "")), lang='vi'), text)
    text = re.sub(r'\d+(\.\d+)?', lambda m: read_decimal_or_int(m.group()), text)
    return text

def optimize_for_tts(text):
    text = re.sub(r'[<>{}\[\]/\\*^$#@~_]', '', text)
    # Xử lý các mã chứng khoán để TTS đọc từng chữ cái (Ví dụ: SSI -> S S I)
    text = re.sub(r'\b([A-Z]{3})\b', lambda m: " ".join(list(m.group())), text)
    text = text.replace(".", ". ").replace(",", ", ").replace("...", "... ")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# ==============================
# LLM CALLS
# ==============================
def call_qwen(prompt, retry=3):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": QWEN_MODEL,
        "messages": [
            {"role": "system", "content": "Bạn là biên tập viên tài chính bản sắc riêng. Không dùng văn mẫu. Viết câu ngắn, súc tích, nhịp điệu dồn dập như bản tin nhanh."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.85, # Tăng sáng tạo
        "max_tokens": 1000
    }
    for i in range(retry):
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=60)
            if res.status_code == 200: return res.json()["choices"][0]["message"]["content"]
            time.sleep(5)
        except: time.sleep(5)
    return None

def call_gemini(prompt, retry=2):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.9}}
    for i in range(retry):
        try:
            res = requests.post(url, json=payload, timeout=25)
            if res.status_code == 200: return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        except: time.sleep(2)
    return None

# ==============================
# GENERATE SCRIPT MAIN
# ==============================
def generate_script(topic, market_data=None):
    if not market_data:
        try: market_data = get_market_data()
        except: market_data = {}

    gain_text = market_data.get("gain_text", "một vài mã xanh nhẹ")
    lose_text = market_data.get("lose_text", "áp lực chốt lời diện rộng")
    
    # CHỌN NGẪU NHIÊN PHONG CÁCH CHO MỖI LẦN CHẠY
    style = random.choice(STYLES)
    print(f"🎭 Style hôm nay: {style['name']}")

    prompt = f"""
# VAI TRÒ: Bạn là một {style['name']}. 
# PHONG CÁCH: {style['tone']}
# NHIỆM VỤ: Viết kịch bản video dọc 180 giây về chủ đề: {topic}.

# YÊU CẦU NGÔN NGỮ (SỐNG CÒN):
- Tuyệt đối KHÔNG dùng: "Xin chào", "Trong video này", "Chào mừng các bạn", "Hãy cùng xem".
- KHÔNG dùng cấu trúc liệt kê khô khan. Hãy biến dữ liệu thành một câu chuyện.
- Dùng tiếng lóng chứng khoán: "Cá mập", "F0", "Đu đỉnh", "Về bờ", "Múa bên trăng", "Sập hầm", "Full margin".
- Độ dài: 450 - 500 chữ. Câu cực ngắn.

# DỮ LIỆU THỰC TẾ:
- Tích cực: {gain_text}
- Tiêu cực: {lose_text}

# CẤU TRÚC KỊCH BẢN:
1. MỞ ĐẦU (HOOK): {style['hook_type']}. Vào thẳng vấn đề, cực kỳ sốc hoặc gây tò mò trong 3 câu đầu.
2. PHÂN TÍCH: Tại sao thị trường lại vận hành như vậy? Đừng chỉ liệt kê số, hãy giải thích tâm lý đằng sau con số đó.
3. TIÊU ĐIỂM DÒNG TIỀN: Nói về {gain_text} và {lose_text} như một trận chiến giữa bên mua và bên bán.
4. QUẢN TRỊ RỦI RO: Đưa ra lời khuyên về tư duy (Không phải lời khuyên mua bán). Cách giữ tiền quan trọng hơn cách kiếm tiền.
5. KẾT THÚC: Một câu khẳng định đầy sức nặng hoặc một câu hỏi để khán giả phải comment tranh luận.

LƯU Ý: Chỉ trả về nội dung kịch bản, không kèm tiêu đề hay ghi chú. Không dùng emoji, không dùng hashtag.
"""

    print("🤖 AI đang 'nhập vai' viết kịch bản...")
    script = call_qwen(prompt) or call_gemini(prompt)

    if not script:
        script = f"Thị trường {topic} đang khiến nhiều người mất phương hướng. Nhóm {gain_text} nỗ lực giữ nhịp nhưng áp lực từ {lose_text} vẫn quá lớn. Đừng vội vàng lúc này."

    # Xử lý hậu kỳ
    script = normalize_numbers(script)
    script = optimize_for_tts(script)

    return script

if __name__ == "__main__":
    print(generate_script("Tại sao nhà đầu tư cá nhân luôn thua lỗ?"))
