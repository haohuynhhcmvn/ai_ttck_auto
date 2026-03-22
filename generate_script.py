
# ==============================
# GENERATE SCRIPT USING GEMINI
# ==============================

import requests
import os

API_KEY = os.getenv("GEMINI_API_KEY")

def generate_script(topic):
    prompt = f""" 
        Bạn là một Giám đốc Sáng tạo (Creative Director) chuyên về nội dung ngắn Viral trên nền tảng TikTok, Reels & Shorts, có hiểu biết sâu sắc về tâm lý đám đông và thuật toán phân phối nội dung năm 2026. Nhiệm vụ của bạn là viết một kịch bản video TikTok 30 giây bùng nổ về chủ đề: "{topic}".
        # TARGET AUDIENCE
        - Nhóm đối tượng: Gen Z & Millennials trẻ, bận rộn, lướt nhanh, thích sự thực tế, hài hước hoặc thông tin cực sốc (edutainment).
        - Nỗi đau (Pain point) liên quan đến chủ đề: {topic} (Ví dụ: thiếu thời gian, sợ bị lừa, không biết bắt đầu từ đâu...).
        
        # SCRIPT REQUIREMENTS (CRITICAL)
        Kịch bản phải tuân thủ nghiêm ngặt cấu trúc và các yếu tố sau để tối ưu hóa Giữ chân khán giả (Watch time) và Tương tác (Engagement):
        
        1.  **THE HOOK (0-3s) - Cấp độ "Dừng lướt":**
            * Phải là một câu nói hoặc hình ảnh gây sốc, đánh trúng vào nỗi sợ hãi lớn nhất, sự tò mò tột độ hoặc một lầm tưởng phổ biến (myth) liên quan đến {topic}.
            * *Không được mở đầu bằng: "Chào mọi người...", "Hôm nay mình sẽ..."*
        
        2.  **THE CONTENT BODY (4-25s) - GIÁ TRỊ CỐT LÕI:**
            * Cung cấp chính xác 3 "vũ khí bí mật", 3 bước thực hiện ngay lập tức, hoặc 1 bí mật mà 99% mọi người không biết về {topic}.
            * Nội dung phải đi thẳng vào vấn đề, sử dụng từ ngữ hành động mạnh mạnh, không có từ thừa.
        
        3.  **THE CTA (CALL TO ACTION) (26-30s) - TỐI ƯU CHUYỂN ĐỔI:**
            * Lời kêu gọi hành động phải tự nhiên, gắn liền với lợi ích của khán giả khi tương tác.
            * Ví dụ CTA nâng cấp: "Lưu lại ngay kẻo lạc mất", "Comment ['{topic}'] mình gửi tài liệu chi tiết", "Follow để không bỏ lỡ phần tiếp theo".
        ---
        Bắt đầu viết kịch bản ngay bây giờ:
"""


    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    res = requests.post(url, json={
        "contents": [{"parts": [{"text": prompt}]}]
    })

    return res.json()["candidates"][0]["content"]["parts"][0]["text"]
