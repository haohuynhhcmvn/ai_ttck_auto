# ==============================
# GENERATE SOCIAL CONTENT (AI POWERED)
# ==============================

import requests
import os
import time
import random

# ==============================
# CONFIG & API KEYS (Đồng nhất với generate_script)
# ==============================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

QWEN_MODEL = "qwen/qwen3.5-122b-a10b"
GEMINI_MODEL = "gemini-2.5-flash"

# ==============================
# LLM CALLS (Giữ nguyên logic gọi API của bạn)
# ==============================
def call_qwen_social(prompt, retry=3): # Tăng lên 3 lần thử
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}", 
        "Content-Type": "application/json"
    }
    payload = {
        "model": QWEN_MODEL,
        "messages": [
            {"role": "system", "content": "Bạn là chuyên gia sáng tạo nội dung tài chính. Viết nội dung ngắn gọn, thu hút kèm emoji."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000 # Tăng nhẹ để tránh bị cắt cụt content
    }
    
    for i in range(retry):
        try:
            # Tăng timeout lên 60s vì Qwen 122B xử lý Tiếng Việt khá nặng
            res = requests.post(url, headers=headers, json=payload, timeout=60) 
            
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            
            elif res.status_code == 429:
                print(f"⏳ Đang bị giới hạn (Rate Limit), nghỉ 10s trước khi thử lại lần {i+1}...")
                time.sleep(10)
            else:
                print(f"⚠️ Qwen trả về lỗi mã: {res.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"🕒 Lần {i+1}: API phản hồi quá chậm (Timeout). Đang thử lại...")
        except Exception as e:
            print(f"❌ Lần {i+1} lỗi: {e}")
        
        # Nghỉ tăng dần giữa các lần retry (2s, 4s, 8s...)
        time.sleep(2 * (i + 1))
        
    return None

def call_gemini_social(prompt, retry=2):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    for i in range(retry):
        try:
            res = requests.post(url, json=payload, timeout=25)
            if res.status_code == 200:
                return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"⚠️ Gemini Social lỗi: {e}")
            time.sleep(2)
    return None

# ==============================
# MAIN FUNCTION: SCRIPT TO CONTENT
# ==============================
def script_to_content(script, topic=None):
    """
    Sử dụng AI để chuyển đổi script TTS sang nội dung mạng xã hội chuyên nghiệp.
    """
    
    prompt = f"""
# NHIỆM VỤ: Chuyển đổi kịch bản video (dùng để đọc) thành bài đăng mạng xã hội (TikTok/Facebook/Telegram) chỉ rút gọn lại tối đa 200 từ.
# CHỦ ĐỀ: {topic if topic else "Bản tin tài chính"}
# KỊCH BẢN GỐC: {script}

# YÊU CẦU CHI TIẾT:
1. Chuyển đổi từ phiên âm sang viết chuẩn: 'Vờ ni In đéc' -> 'VN-Index', 'phần trăm' -> '%', 'phẩy' -> dấu chấm thập phân.
2. Thêm Emoji (📈, 🚀, 🏦, 📉) phù hợp với ngữ cảnh tăng giảm.
3. Cấu trúc bài đăng:
   - Header: Hook giật gân về {topic}.
   - Body: Các gạch đầu dòng phân tích thị trường dứt khoát.
   - List: Liệt kê các mã cổ phiếu nổi bật (nếu có).
   - CTA: Kêu gọi Follow và miễn trừ trách nhiệm.
4. Hashtag: 5-7 cái liên quan (ví dụ: #chungkhoan #vimo #dautu).

Chỉ trả về nội dung bài đăng, không giải thích thêm.
"""

    print("🤖 AI đang viết nội dung bài đăng Social...")
    # Thử Qwen trước, nếu lỗi thì dùng Gemini
    social_post = call_qwen_social(prompt) or call_gemini_social(prompt)

    if not social_post:
        print("⚠️ Cả 2 AI Social lỗi, dùng logic dự phòng thủ công.")
        # Logic dự phòng (Fallback) giống bản cũ của bạn
        lines = script.split(".")
        content = [f"🚨 {topic.upper()}" if topic else "📊 BẢN TIN CHỨNG KHOÁN"]
        for i, line in enumerate(lines[:5]):
            content.append(f"👉 {line.strip()}")
        content.append("\n#chungkhoan #stock #dautu")
        return "\n".join(content)

    return social_post.strip()

# --- TEST ---
if __name__ == "__main__":
    test_script = "Vờ ni In đéc hôm nay bùng nổ mạnh mẽ. Thị trường tăng mười lăm phẩy năm điểm. Nhóm thép dẫn đầu với mã Hòa Phát tăng kịch trần."
    print(script_to_content(test_script, topic="VNINDEX BÙNG NỔ"))
