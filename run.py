# ==============================
# MAIN PIPELINE (PRO MAX STABLE)
# ==============================

import os
import sys
import time
from datetime import datetime, timezone, timedelta # <-- THÊM DÒNG NÀY

# Fix lỗi MoviePy đôi khi không giải phóng file audio trên Windows/Linux
os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg" 
from moviepy.editor import AudioFileClip

# Import các modules tự xây dựng
try:
    from topic_ai import generate_topics
    from generate_script import generate_script, call_gemini
    from content_ai import script_to_content
    from tts import text_to_speech
    import sub_utils 
    from render import render_video
    from upload_youtube import upload_video
    from telegram import send_message, send_video
    from market_data import get_market_data
    from text_utils import save_text, clean_text_for_tts
except ImportError as e:
    print(f"❌ Thiếu module: {e}")
    sys.exit(1)

# ==============================
# PROCESS 1 VIDEO
# ==============================
def process_video(topic, index):
    print(f"\n🚀 BẮT ĐẦU XỬ LÝ VIDEO {index + 1}: {topic}")

    # --- BƯỚC 1: FETCH MARKET DATA ---
    print("1️⃣ Đang lấy dữ liệu thị trường...")
    try:
        market_data = get_market_data()
    except Exception as e:
        print(f"⚠️ Lỗi lấy Market Data: {e}")
        market_data = {}

    # --- BƯỚC 2: GENERATE SCRIPT ---
    print("2️⃣ AI đang biên soạn nội dung...")
    script = generate_script(topic, market_data)

    if not script or len(script) < 20:
        print("❌ Script trống hoặc quá ngắn → Bỏ qua")
        return

    save_text(script, f"raw_v{index}")

    # --- BƯỚC 3: CLEAN TEXT FOR TTS ---
    print("3️⃣ Làm sạch văn bản cho giọng đọc AI...")
    clean_script = clean_text_for_tts(script)
    save_text(clean_script, f"clean_v{index}")

    # --- BƯỚC 4: SOCIAL CONTENT ---
    print("4️⃣ Tạo nội dung đăng mạng xã hội...")
    content = script_to_content(script, topic)
    if not content:
        content = f"📊 BẢN TIN THỊ TRƯỜNG: {topic}\n\nXem chi tiết tại video bên dưới!"

    # --- BƯỚC 5: TEXT TO SPEECH ---
    print("5️⃣ Đang chuyển đổi văn bản thành âm thanh...")
    audio = None
    try:
        audio = text_to_speech(clean_script)
        if not audio or not os.path.exists(audio):
            raise Exception("Không tạo được file Audio")
            
        audio_clip = AudioFileClip(audio)
        duration = audio_clip.duration
        audio_clip.close()
    except Exception as e:
        print(f"❌ Lỗi TTS: {e}")
        return # Dừng tiến trình nếu không có âm thanh

    # --- BƯỚC 6 & 7: GENERATE TICKER ---
    print("6️⃣ & 7️⃣ Tạo Ticker chữ chạy ngang...")
    ass_file = None
    try:
        ticker_prompt = (
            f"Dựa trên kịch bản, trích ra 5 tin vắn quan trọng nhất. "
            f"Yêu cầu: VIẾT HOA | Độ dài xấp xỉ nhau | Ngăn cách bằng ký tự ' • ' | "
            f"Mỗi tin bắt đầu bằng một Emoji. Kịch bản: {script}"
        )
        summary_text = call_gemini(ticker_prompt) 
        
        # Fallback nếu AI lỗi
        if not summary_text:
            summary_text = f"🔥 THÔNG TIN CẬP NHẬT: {topic.upper()} • THỊ TRƯỜNG BIẾN ĐỘNG LIÊN TỤC •"
            
        ass_file = sub_utils.create_ticker_sub(summary_text, duration)
    except Exception as e:
        print(f"⚠️ Lỗi tạo Ticker (Bỏ qua sub): {e}")

    # --- BƯỚC 8: RENDER VIDEO ---
    print("8️⃣ Render video chuẩn 9:16...")
    # Thêm timestamp vào tên file để không bị ghi đè
    output = f"final_video_{index}_{int(time.time())}.mp4"
    
    try:
        render_result = render_video(
            audio_path=audio,
            subtitles=ass_file,
            output=output,
            topic=topic,
            market_data=market_data,
            script=script
        )
        
        # Kiểm tra file video thực sự tồn tại và có dung lượng > 0
        if not render_result or not os.path.exists(output) or os.path.getsize(output) < 1000:
            raise Exception("File Output bị lỗi hoặc trống")
            
    except Exception as e:
        print(f"❌ Render sập: {e}")
        return # Dừng nếu render hỏng

    # --- BƯỚC 9 & 10: PHÂN PHỐI ---
    # Ưu tiên gửi Telegram trước vì tỷ lệ thành công cao hơn YouTube
    # --- BƯỚC 9 & 10: PHÂN PHỐI ---
    print("9️⃣ Đang gửi thông báo Telegram...")
    try:
        # Lấy giờ Việt Nam (UTC+7) chuẩn xác dù server ở bất kỳ đâu
        vn_timezone = timezone(timedelta(hours=7))
        current_date = datetime.now(vn_timezone).strftime("%d/%m/%Y")
        
        # Tạo tiêu đề chuẩn
        title = f"BẢN TIN TÀI CHÍNH 247 - NGÀY {current_date}"
        
        # Gửi tin nhắn và video
        send_message(f"🚨 **{title}**\n\n{content}")
        send_video(output)
    except Exception as e:
        print(f"⚠️ Lỗi Telegram: {e}")

    print("🔟 Đang tải lên YouTube Shorts...")
    url = "Chưa có link"
    try:
        url = upload_video(output)
        if url:
            send_message(f"📺 Đã có mặt trên YouTube: {url}")
    except Exception as e:
        print(f"⚠️ Lỗi Upload YouTube: {e}")

    # --- BƯỚC 11: DỌN DẸP TÀI NGUYÊN (CLEANUP) ---
    print("🧹 Đang dọn dẹp file tạm...")
    try:
        if audio and os.path.exists(audio): os.remove(audio)
        if ass_file and os.path.exists(ass_file): os.remove(ass_file)
        # Không xóa output video để bạn có thể xem lại hoặc GH Actions upload làm artifact
    except Exception as e:
        print(f"⚠️ Lỗi dọn dẹp: {e}")

# ==============================
# MAIN ENGINE
# ==============================
def main():
    print("\n" + "="*50)
    print("🔥 HỆ THỐNG AUTO-VIDEO CHỨNG KHOÁN ĐÃ KHỞI ĐỘNG")
    print("="*50)

    os.makedirs("logs", exist_ok=True)

    try:
        topics = generate_topics()
        if not topics: raise ValueError("AI trả về danh sách topic rỗng")
    except Exception as e:
        print(f"⚠️ Lỗi lấy Topic: {e}. Sử dụng Topic dự phòng.")
        topics = ["Nhận định nhanh diễn biến thị trường hôm nay"]

    # Đổi topics[:1] thành số lượng bạn muốn chạy mỗi lần (Khuyên dùng: 2 hoặc 3)
    for i, topic in enumerate(topics[:1]):
        try:
            process_video(topic, i)
        except Exception as e:
            print(f"❌ Pipeline sập hoàn toàn tại Video {i}: {e}")
            
        # Nghỉ 10s giữa các video để tránh spam API
        if i < len(topics[:1]) - 1:
            time.sleep(10) 

    print("\n✅ TẤT CẢ TIẾN TRÌNH ĐÃ HOÀN TẤT")
    print("="*50)

if __name__ == "__main__":
    main()
