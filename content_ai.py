# ==============================
# GENERATE SOCIAL CONTENT PRO (DYNAMIC REVERSE-ENGINEERING)
# ==============================

import requests
import os
import time
import random
import re

# ==============================
# CONFIG & API KEYS
# ==============================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

QWEN_MODEL = "qwen/qwen3.5-122b-a10b"
GEMINI_MODEL = "gemini-2.5-flash" # Dùng bản Flash để tối ưu tốc độ cho Social

# ==============================
# LLM CALLS
# ==============================
def call_qwen_social(prompt, retry=3):
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": QWEN_MODEL,
        "messages": [
            {"role": "system", "content": "Bạn là giám đốc nội dung cho quỹ đầu tư. Viết bài ngắn gọn, sắc sảo, dùng ngôn ngữ chuyên gia nhưng gần gũi với nhà đầu tư cá nhân."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 800
    }
    for i in range(retry):
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=60)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            time.sleep(5)
        except: time.sleep(5)
    return None

def call_gemini_social(prompt, retry=2):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.9}}
    for i in range(retry):
        try:
            res = requests.post(url, json=payload, timeout=25)
            if res.status_code == 200:
                return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        except: time.sleep(2)
    return None

# ==============================
# MAIN FUNCTION: SCRIPT TO CONTENT
# ==============================
def script_to_content(script, topic=None):
    """
    Chuyển đổi kịch bản TTS sang bài đăng Social chuẩn chỉnh.
    """
    
    # Danh sách các 'Góc nhìn' để bài đăng đa dạng
    angles = [
        "Tóm tắt nhanh cho nhà đầu tư bận rộn.",
        "Phân tích sâu về hành vi dòng tiền phiên nay.",
        "Cảnh báo các bẫy tâm lý xuất hiện trong phiên.",
        "Góc nhìn vĩ mô và tác động đến nhóm ngành nổi bật."
    ]
    current_angle = random.choice(angles)

    prompt = f"""
# ROLE: Bạn là Chuyên gia Content Marketing trong lĩnh vực Fintech.
# NHIỆM VỤ: Chuyển kịch bản đọc (TTS) bên dưới thành 1 bài đăng Social thu hút.
# CHIẾN THUẬT NỘI DUNG: {current_angle}

# KỊCH BẢN GỐC (Đã qua xử lý TTS): 
{script}

# YÊU CẦU QUAN TRỌNG (REVERSE-ENGINEERING):
1. CHUẨN HÓA THUẬT NGỮ: 
   - 'Vờ ni In đếch' hoặc 'Vờ ni' -> 'VN-Index'.
   - 'phần trăm' -> '%'.
   - 'phẩy' -> dấu chấm (vd: mười lăm phẩy năm -> 15.5).
   - Các chữ cái rời 'S S I', 'H P G' -> Viết liền thành mã 'SSI', 'HPG'.
2. NÉ VI PHẠM: Tuyệt đối không dùng 'làm giàu', 'kiếm tiền', 'cam kết lãi', 'chắc chắn sập'. Thay bằng 'hiệu suất', 'quản trị rủi ro', 'vận động giá'.
3. TRÌNH BÀY: Dùng tối đa 5 emoji. Chia đoạn rõ ràng.

# CẤU TRÚC:
- Tiêu đề: Đậm chất 'giật gân' nhưng chuyên nghiệp về {topic}.
- Nội dung: 3 ý chính rút gọn từ kịch bản.
- Hành động: Một lời khuyên về tư duy kỷ luật.
- Hashtag: 5 cái bắt trend chứng khoán.

Chỉ trả về nội dung bài đăng, không thêm lời dẫn.
"""
    print(f"🤖 AI đang viết Social Post (Angle: {current_angle})...")
    social_post = call_qwen_social(prompt) or call_gemini_social(prompt)

    if not social_post:
        # Fallback an toàn nếu API lỗi
        return f"📊 BẢN TIN THỊ TRƯỜNG: {topic}\n\n📍 Thị trường có những vận động đáng chú ý. Nhà đầu tư nên tập trung vào quản trị danh mục và giữ kỷ luật thép.\n\n#chungkhoan #vimo #dautu"

    # Hậu xử lý nhẹ để đảm bảo sạch sẽ
    social_post = social_post.replace("**", "").replace("###", "") # Xóa markdown thừa nếu AI tự ý thêm
    return social_post.strip()

# --- TEST ---
if __name__ == "__main__":
    test_script = "Vờ ni In đếch hôm nay tăng mười lăm phẩy năm điểm. Nhóm chứng khoán bùng nổ với mã S S I tăng kịch trần."
    print(script_to_content(test_script, topic="THỊ TRƯỜNG HƯNG PHẤN"))
