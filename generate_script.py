
# ==============================
# GENERATE SCRIPT USING GEMINI
# ==============================

import requests
import os

API_KEY = os.getenv("GEMINI_API_KEY")

def generate_script(topic):
    prompt = f""" 
        Bạn là một Chuyên gia Phân tích Chiến lược Chứng khoán cấp cao với khả năng "đọc vị" thị trường và tâm lý đám đông. Nhiệm vụ của bạn là viết một đoạn lời thoại (Voiceover) 30 giây cực kỳ lôi cuốn cho video ngắn về chủ đề: "{topic}".
        
        # YÊU CẦU VỀ VĂN PHONG (CHỨNG KHOÁN)
        - **Giọng điệu:** Quyết đoán, chuyên nghiệp, mang tính "tiết lộ bí mật" hoặc "cảnh báo khẩn cấp".
        - **Ngôn ngữ:** Sử dụng linh hoạt các thuật ngữ chứng khoán (như: FOMO, thanh khoản, đu đỉnh, cắt lỗ, cá mập, gom hàng...) một cách tự nhiên.
        - **Nhịp điệu:** Nhanh, dồn dập ở phần đầu (tạo sự kịch tính) và chậm lại, chắc chắn ở phần đưa ra giải pháp.
        
        # CẤU TRÚC LỜI THOẠI (STRICTLY VOICEOVER ONLY)
        Văn bản trả về phải là một đoạn nói liền mạch, không có ký hiệu kịch bản, bao gồm 3 phần:
        
        1.  **THE HOOK (Cú tát thị trường):** Đánh thẳng vào một sai lầm chết người mà số đông đang mắc phải hoặc một cơ hội sắp trôi qua. (Ví dụ: "Bạn đang vui mừng vì mã này tím? Coi chừng, đó là cái bẫy!")
        2.  **THE INSIGHT (Góc nhìn chuyên gia):** Giải mã "game" của đội lái hoặc đưa ra một chỉ số kỹ thuật/vĩ mô cực kỳ quan trọng về {topic} mà ít người để ý.
        3.  **THE CALL (Hành động):** Lời kêu gọi mang tính đặc quyền. (Ví dụ: "Đừng để bị 'thịt' thêm lần nào nữa. Click vào bio xem danh mục siêu cổ phiếu tuần tới của mình.")
        
        # RÀNG BUỘC ĐẦU RA
        - Chỉ trả về DUY NHẤT lời thoại để đọc, không giải thích, không thêm ký hiệu [Cảnh], không dùng hashtag.
        - Độ dài: 80 - 100 chữ (vừa đủ cho 30 giây nói tốc độ trung bình).
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    res = requests.post(url, json={
        "contents": [{"parts": [{"text": prompt}]}]
    })

    return res.json()["candidates"][0]["content"]["parts"][0]["text"]
