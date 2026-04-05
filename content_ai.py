# ==============================================================
# HỆ THỐNG TẠO NỘI DUNG MẠNG XÃ HỘI (REVERSE-ENGINEERING)
# ==============================================================

import requests
import os
import time
import random
import re

# --- CẤU HÌNH & MÃ API (LẤY TỪ BIẾN MÔI TRƯỜNG) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# Chốt cứng 2 Model như đã thống nhất
QWEN_MODEL = "qwen/qwen3.5-122b-a10b"
GEMINI_MODEL = "gemini-2.5-flash" 

# ==============================================================
# CÁC HÀM GỌI AI (LLM CALLS)
# ==============================================================

def call_qwen_social(prompt, retry=3):
    """Gọi model Qwen qua NVIDIA API để xử lý ngôn ngữ tài chính sắc sảo"""
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": QWEN_MODEL,
        "messages": [
            {"role": "system", "content": "Bạn là giám đốc nội dung cho quỹ đầu tư. Viết bài ngắn gọn, sắc sảo."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8, # Để AI sáng tạo tiêu đề giật gân hơn
        "max_tokens": 800
    }
    for i in range(retry):
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=60)
            if res.status_code == 200:
                return res.json()["choices"][0]["message"]["content"]
            time.sleep(5) # Nghỉ 5s nếu API bận
        except: time.sleep(5)
    return None

def call_gemini_social(prompt, retry=2):
    """Gọi model Gemini 2.5 Flash để hỗ trợ nếu Qwen gặp sự cố"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.9}}
    for i in range(retry):
        try:
            res = requests.post(url, json=payload, timeout=25)
            if res.status_code == 200:
                return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        except: time.sleep(2)
    return None

# ==============================================================
# HÀM CHÍNH: BIẾN KỊCH BẢN THÀNH NỘI DUNG ĐA NỀN TẢNG
# ==============================================================

def script_to_content(script, topic=None):
    """
    Hàm này thực hiện 'truy ngược' kịch bản để tạo ra:
    1. VIDEO_HOOK: Tiêu đề hiện 3 giây đầu để giữ chân người xem.
    2. SOCIAL_POST: Bài đăng hoàn chỉnh cho Facebook/Telegram.
    """
    
    # Random các góc nhìn để nội dung kênh không bị nhàm chán
    angles = [
        "Tóm tắt nhanh cho nhà đầu tư bận rộn.",
        "Phân tích sâu về hành vi dòng tiền phiên nay.",
        "Cảnh báo các bẫy tâm lý xuất hiện trong phiên.",
        "Góc nhìn vĩ mô và tác động đến nhóm ngành nổi bật."
    ]
    current_angle = random.choice(angles)

    # Prompt yêu cầu AI bóc tách nội dung cực kỳ khắt khe
    prompt = f"""
# NHIỆM VỤ: 
1. Tạo 1 câu VIDEO_HOOK (dưới 7 từ) để hiện lên 3 giây đầu video. 
2. Viết bài đăng Social từ kịch bản TTS bên dưới.

# CHIẾN THUẬT: {current_angle}

# KỊCH BẢN GỐC (Dữ liệu đầu vào): 
{script}

# YÊU CẦU CHO VIDEO_HOOK (QUAN TRỌNG):
- Phải cực gắt, đánh vào mã cổ phiếu hot nhất. Viết HOA toàn bộ. 
- Mục tiêu: Khiến người xem dừng lướt ngay lập tức.
- VD: "SSI: TÍN HIỆU CỰC MẠNH?", "CẢNH BÁO: ĐỪNG MUA NVL?", "THÁO CHẠY HAY GOM HÀNG?"

# CHUẨN HÓA DỮ LIỆU (REVERSE-ENGINEERING):
- Chuyển 'Vờ ni In đếch' thành 'VN-Index'.
- Chuyển 'phần trăm' thành '%', 'phẩy' thành dấu chấm '.'.
- Ghép các mã cổ phiếu viết rời: 'H P G' -> 'HPG', 'V C B' -> 'VCB'.

# ĐỊNH DẠNG TRẢ VỀ (ÉP AI TRẢ VỀ ĐÚNG CẤU TRÚC NÀY):
[VIDEO_HOOK]
Câu tiêu đề video của bạn ở đây
[SOCIAL_POST]
Nội dung bài đăng mạng xã hội ở đây
"""
    print(f"🤖 AI đang 'truy ngược' kịch bản để tạo Hook & Post...")
    raw_response = call_qwen_social(prompt) or call_gemini_social(prompt)

    # Kết quả dự phòng nếu AI bị lỗi
    result = {
        "video_hook": f"BẢN TIN {topic.upper()}" if topic else "BẢN TIN CHỨNG KHOÁN",
        "social_post": f"📊 Cập nhật thị trường: {topic}\n\nXem chi tiết tại video!"
    }

    if raw_response:
        try:
            # Dùng Regex để tách phần Hook và phần Post dựa trên thẻ [TAG]
            hook_match = re.search(r"\[VIDEO_HOOK\]\n?(.*?)\n?\[SOCIAL_POST\]", raw_response, re.DOTALL)
            post_match = re.search(r"\[SOCIAL_POST\]\n?(.*)", raw_response, re.DOTALL)

            if hook_match:
                # Lấy câu Hook, xóa dấu ngoặc kép và khoảng trắng thừa
                result["video_hook"] = hook_match.group(1).strip().replace('"', '')
            
            if post_match:
                # Lấy bài đăng Social, làm sạch định dạng Markdown
                post = post_match.group(1).strip()
                result["social_post"] = post.replace("**", "").replace("###", "")
        except Exception as e:
            print(f"⚠️ Lỗi bóc tách nội dung: {e}")
            result["social_post"] = raw_response.strip()

    return result # Trả về Dictionary cho main.py sử dụng

# --- TEST THỬ NGHIỆM ---
if __name__ == "__main__":
    test_script = "Vờ ni In đếch hôm nay tăng mười lăm phẩy năm điểm. Mã H P G bùng nổ khối lượng."
    output = script_to_content(test_script, topic="THỊ TRƯỜNG BIẾN ĐỘNG")
    print(f"\n🎬 TIÊU ĐỀ VIDEO (3s ĐẦU): {output['video_hook']}")
    print(f"📝 BÀI ĐĂNG SOCIAL:\n{output['social_post']}")
