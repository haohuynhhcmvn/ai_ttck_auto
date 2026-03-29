# ==============================
# MAIN PIPELINE (FINAL PRO MAX - TICKER VERSION)
# ==============================

import os
import sys
from moviepy.editor import AudioFileClip

# Import các modules tự xây dựng
try:
    from topic_ai import generate_topics
    from generate_script import generate_script, call_gemini  # Thêm call_gemini để tóm tắt
    from content_ai import script_to_content
    from tts import text_to_speech
    # Loại bỏ transcribe và subtitle cũ
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
    print(f"\n🚀 BẮT ĐẦU XỬ LÝ VIDEO {index}: {topic}")

    # --- BƯỚC 1: FETCH MARKET DATA ---
    print("1️⃣ Đang lấy dữ liệu thị trường thực tế...")
    try:
        market_data = get_market_data()
    except Exception as e:
        print(f"⚠️ Lỗi lấy Market Data: {e}")
        market_data = {}

    # --- BƯỚC 2: GENERATE SCRIPT ---
    print("2️⃣ AI đang biên soạn nội dung...")
    script = generate_script(topic, market_data)

    if not script or len(script) < 20:
        print("❌ Script trống → Bỏ qua")
        return

    save_text(script, f"raw_v{index}")

    # --- BƯỚC 3: CLEAN TEXT FOR TTS ---
    print("3️⃣ Làm sạch văn bản cho giọng đọc AI...")
    clean_script = clean_text_for_tts(script)
    save_text(clean_script, f"clean_v{index}")

    # --- BƯỚC 4: SOCIAL CONTENT ---
    print("4️⃣ Tạo nội dung đăng mạng xã hội...")
    content = script_to_content(script, topic)

    # --- BƯỚC 5: TEXT TO SPEECH ---
    print("5️⃣ Đang chuyển đổi văn bản thành âm thanh...")
    try:
        audio = text_to_speech(clean_script)
        # Lấy thời lượng thực tế của audio để đồng bộ chữ chạy
        audio_clip = AudioFileClip(audio)
        duration = audio_clip.duration
        audio_clip.close()
    except Exception as e:
        print(f"❌ Lỗi TTS: {e}")
        return

    # --- BƯỚC 6 & 7: GENERATE TICKER (THAY THẾ TRANSCRIBE & SUBTITLE) ---
    print("6️⃣ & 7️⃣ Đang tóm tắt tin vắn và tạo dải chữ chạy ngang...")
    try:
        # Prompt tóm tắt ngắn gọn để làm Ticker
        ticker_prompt = (
            f"Dựa trên kịch bản sau, hãy trích ra 7-10 tin vắn tài chính 'giật gân' cực ngắn. "
            f"Yêu cầu: \n"
            f"1. VIẾT HOA TOÀN BỘ, cách nhau bằng dấu |. \n"
            f"2. Sử dụng các động từ mạnh: BÙNG NỔ, QUAY XE, THÁO CHẠY, ĐẠI TIỆC, RUNG LẮC, CHẠM ĐỈNH. \n"
            f"3. Thêm Emoji phù hợp ở mỗi tin (🚀, 🔥, 📊, 💎, 🔴, 🟢). \n"
            f"4. Giữ đúng mã cổ phiếu (VD: SSI, HPG, VND). \n"
            f"5. Độ dài mỗi tin dưới 15 từ. \n"
            f"Kịch bản: {script}"
       )
        
        # Gọi AI tóm tắt từ script gốc
        summary_text = call_gemini(ticker_prompt) 
        
        # Tạo file ASS chạy ngang (Ticker)
        ass_file = sub_utils.create_ticker_sub(summary_text, duration)
    except Exception as e:
        print(f"⚠️ Lỗi tạo Ticker: {e}")
        ass_file = None

    # --- BƯỚC 8: RENDER VIDEO ---
    print("8️⃣ Render video")
    output = f"output_{index}.mp4"
    
    try:
        render_video(
            audio_path=audio,
            subtitles=ass_file,  # Truyền file ticker .ass vào
            output=output,
            topic=topic,
            market_data=market_data,
            script=script
        )
    except Exception as e:
        print("❌ Render lỗi:", e)
        return

    # --- BƯỚC 9: UPLOAD YOUTUBE ---
    print("9️⃣ Đang tải lên YouTube...")
    try:
        url = upload_video(output)
    except Exception as e:
        print(f"⚠️ Lỗi Upload: {e}")
        url = "Không có link"

    # --- BƯỚC 10: TELEGRAM NOTIFICATION ---
    print("🔟 Đang gửi thông báo Telegram...")
    try:
        send_message(f"{content}\n\n🔗 Link: {url}")
        send_video(output)
    except Exception as e:
        print(f"⚠️ Lỗi Telegram: {e}")

# ==============================
# MAIN ENGINE
# ==============================
def main():
    print("\n" + "="*40)
    print("🔥 HỆ THỐNG AUTO-VIDEO CHỨNG KHOÁN START")
    print("="*40)

    os.makedirs("logs", exist_ok=True)

    try:
        topics = generate_topics()
    except Exception as e:
        print(f"⚠️ Lỗi lấy Topic AI: {e}")
        topics = ["Nhận định thị trường chứng khoán hôm nay"]

    for i, topic in enumerate(topics[:1]):
        try:
            process_video(topic, i)
        except Exception as e:
            print(f"❌ Pipeline sập tại Video {i}: {e}")

    print("\n✅ TẤT CẢ TIẾN TRÌNH ĐÃ HOÀN TẤT")
    print("="*40)

if __name__ == "__main__":
    main()
