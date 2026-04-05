# ==============================================================
# MAIN PIPELINE (PRO MAX STABLE - HOOK STRATEGY ENABLED)
# ==============================================================

import os
import sys
import time
from datetime import datetime, timezone, timedelta

# Fix lỗi MoviePy trên các môi trường server
os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg" 
from moviepy.editor import AudioFileClip

# Import các modules nội bộ
try:
    from topic_ai import generate_topics
    from generate_script import generate_script, call_gemini
    from content_ai import script_to_content # <-- Hàm đã nâng cấp trả về Dict
    from tts import text_to_speech
    import sub_utils 
    from render import render_video # <-- Hàm đã nâng cấp để vẽ Hook
    from upload_youtube import upload_video
    from telegram import send_message, send_video
    from market_data import get_market_data
    from text_utils import save_text, clean_text_for_tts
except ImportError as e:
    print(f"❌ Thiếu module: {e}")
    sys.exit(1)

# ==============================================================
# HÀM XỬ LÝ 1 VIDEO (PROCESS 1 VIDEO)
# ==============================================================
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
    print("2️⃣ AI đang biên soạn kịch bản đọc (Script)...")
    script = generate_script(topic, market_data)
    if not script or len(script) < 20:
        print("❌ Script lỗi → Bỏ qua")
        return
    save_text(script, f"raw_v{index}")

    # --- BƯỚC 3: CLEAN TEXT FOR TTS ---
    print("3️⃣ Làm sạch văn bản cho giọng đọc AI...")
    clean_script = clean_text_for_tts(script)

    # --- BƯỚC 4: SOCIAL CONTENT & HOOK REVERSE-ENGINEERING ---
    # [QUAN TRỌNG]: Nhận về Dictionary chứa cả Hook Video và Post Social
    print("4️⃣ AI đang 'truy ngược' kịch bản để tạo Hook & Nội dung Social...")
    content_data = script_to_content(script, topic)
    
    # Bóc tách dữ liệu từ Dictionary
    video_hook = content_data.get("video_hook", f"BẢN TIN {topic.upper()}")
    social_post = content_data.get("social_post", "Cập nhật thị trường mới nhất!")

    # --- BƯỚC 5: TEXT TO SPEECH ---
    print("5️⃣ Đang chuyển đổi văn bản thành âm thanh...")
    audio = None
    try:
        audio = text_to_speech(clean_script)
        if not audio or not os.path.exists(audio):
            raise Exception("Lỗi file Audio")
            
        audio_clip = AudioFileClip(audio)
        duration = audio_clip.duration
        audio_clip.close()
    except Exception as e:
        print(f"❌ Lỗi TTS: {e}")
        return

    # --- BƯỚC 6 & 7: GENERATE TICKER ---
    print("6️⃣ & 7️⃣ Tạo Ticker chữ chạy ngang...")
    ass_file = None
    try:
        ticker_prompt = (f"Trích 5 tin vắn quan trọng từ kịch bản này: {script}. "
                         "Yêu cầu: VIẾT HOA, ngăn cách bằng ' • '.")
        summary_text = call_gemini(ticker_prompt) or f"🔥 CẬP NHẬT: {topic.upper()}"
        ass_file = sub_utils.create_ticker_sub(summary_text, duration)
    except Exception as e:
        print(f"⚠️ Lỗi Ticker: {e}")

    # --- BƯỚC 8: RENDER VIDEO (TÍCH HỢP HOOK) ---
    print(f"8️⃣ Đang Render video với Hook: '{video_hook}'...")
    output = f"final_video_{index}_{int(time.time())}.mp4"
    
    try:
        # [MỚI]: Truyền thêm tham số video_hook vào engine render
        render_result = render_video(
            audio_path=audio,
            subtitles=ass_file,
            output=output,
            topic=topic,
            market_data=market_data,
            script=script,
            video_hook=video_hook # <-- BIẾN CỨU VIEW 3S ĐẦU
        )
        
        if not render_result or not os.path.exists(output):
            raise Exception("Render thất bại")
            
    except Exception as e:
        print(f"❌ Render sập: {e}")
        return

    # --- BƯỚC 9 & 10: PHÂN PHỐI ĐA NỀN TẢNG ---
    print("9️⃣ Gửi thông báo tới cộng đồng Telegram...")
    try:
        vn_tz = timezone(timedelta(hours=7))
        date_str = datetime.now(vn_tz).strftime("%d/%m/%Y")
        header_title = f"🚨 BẢN TIN TÀI CHÍNH 247 - NGÀY {date_str}"
        
        # Gửi bài đăng social đã được chuẩn hóa thuật ngữ từ Bước 4
        send_message(f"**{header_title}**\n\n{social_post}")
        send_video(output)
    except Exception as e:
        print(f"⚠️ Telegram lỗi: {e}")

    print("🔟 Uploading to YouTube Shorts...")
    try:
        url = upload_video(output)
        if url: send_message(f"📺 Xem trên YouTube: {url}")
    except Exception as e:
        print(f"⚠️ YouTube lỗi: {e}")

    # --- BƯỚC 11: DỌN DẸP ---
    print("🧹 Dọn dẹp tài nguyên tạm...")
    try:
        if audio and os.path.exists(audio): os.remove(audio)
        if ass_file and os.path.exists(ass_file): os.remove(ass_file)
    except: pass

# ==============================================================
# ĐỘNG CƠ CHÍNH (MAIN ENGINE)
# ==============================================================
def main():
    print("\n" + "="*50)
    print("🔥 HỆ THỐNG AUTO-VIDEO 2.0 (STRATEGY HOOK) KHỞI ĐỘNG")
    print("="*50)

    try:
        topics = generate_topics()
        if not topics: raise ValueError("AI không trả về topic")
    except:
        topics = ["Phân tích dòng tiền thị trường chứng khoán hôm nay"]

    # Chạy số lượng video mong muốn (topics[:3] cho 3 video một lúc)
    for i, topic in enumerate(topics[:1]):
        try:
            process_video(topic, i)
        except Exception as e:
            print(f"❌ Lỗi nghiêm trọng tại Video {i}: {e}")
        
        if i < len(topics[:1]) - 1:
            time.sleep(10) # Nghỉ để tránh nghẽn API

    print("\n✅ HOÀN TẤT CHIẾN DỊCH VIDEO HÔM NAY")
    print("="*50)

if __name__ == "__main__":
    main()
