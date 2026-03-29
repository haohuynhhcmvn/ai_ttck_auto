# ==============================
# MAIN PIPELINE (FINAL PRO MAX - TICKER VERSION)
# ==============================

import os
import sys
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

    # --- BƯỚC 6 & 7: GENERATE TICKER ---
    print("6️⃣ & 7️⃣ Đang tóm tắt tin vắn và tạo dải chữ chạy ngang...")
    try:
        ticker_prompt = (
            f"Dựa trên kịch bản, trích ra 6-8 tin vắn. "
            f"Yêu cầu: VIẾT HOA | Độ dài các câu xấp xỉ nhau | Ngăn cách bằng ký tự ' • ' | "
            f"Mỗi tin bắt đầu bằng một Emoji phù hợp. "
            f"Ví dụ: 🚀 SSI BÙNG NỔ THANH KHOẢN • 🟢 VN-INDEX GIỮ VỮNG SẮC XANH • ..."
        )
        
        # Gọi AI tóm tắt
        summary_text = call_gemini(ticker_prompt) 
        
        # Tạo file ASS chạy ngang
        ass_file = sub_utils.create_ticker_sub(summary_text, duration)
    except Exception as e:
        print(f"⚠️ Lỗi tạo Ticker: {e}")
        ass_file = None

    # --- BƯỚC 8: RENDER VIDEO ---
    print("8️⃣ Render video chuẩn 9:16")
    output = f"output_{index}.mp4"
    
    try:
        render_video(
            audio_path=audio,
            subtitles=ass_file,
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
