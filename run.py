# ==============================
# MAIN PIPELINE (FINAL PRO MAX)
# ==============================

import os
import sys

# Import các modules tự xây dựng
try:
    from topic_ai import generate_topics
    from generate_script import generate_script
    from content_ai import script_to_content
    from tts import text_to_speech
    from transcribe import transcribe
    from subtitle import create_subtitles
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

    # --- BƯỚC 1: FETCH MARKET DATA (ƯU TIÊN HÀNG ĐẦU) ---
    print("1️⃣ Đang lấy dữ liệu thị trường thực tế...")
    try:
        market_data = get_market_data()
        # Đảm bảo market_data không rỗng để AI có số liệu viết script
    except Exception as e:
        print(f"⚠️ Lỗi lấy Market Data: {e}")
        market_data = {}

    # --- BƯỚC 2: GENERATE SCRIPT (DÙNG DATA THẬT) ---
    print("2️⃣ AI đang biên soạn nội dung...")
    # Truyền thêm market_data vào để script có số liệu VNINDEX, Top tăng/giảm
    script = generate_script(topic, market_data)

    if not script or len(script) < 20:
        print("❌ Script trống hoặc quá ngắn → Bỏ qua")
        return

    # Lưu bản gốc để đối chiếu
    save_text(script, f"raw_v{index}")

    # --- BƯỚC 3: CLEAN TEXT FOR TTS ---
    print("3️⃣ Làm sạch văn bản cho giọng đọc AI...")
    clean_script = clean_text_for_tts(script)
    save_text(clean_script, f"clean_v{index}")

    # --- BƯỚC 4: SOCIAL CONTENT ---
    print("4️⃣ Tạo nội dung đăng mạng xã hội (Caption)...")
    content = script_to_content(script, topic)

    # --- BƯỚC 5: TEXT TO SPEECH ---
    print("5️⃣ Đang chuyển đổi văn bản thành âm thanh...")
    try:
        audio = text_to_speech(clean_script)
    except Exception as e:
        print(f"❌ Lỗi TTS: {e}")
        return

    # --- BƯỚC 6: TRANSCRIBE ---
    print("6️⃣ Đang tách chữ và lấy timestamp...")
    try:
        words = transcribe(audio)
    except Exception as e:
        print(f"⚠️ Lỗi Transcribe: {e}")
        words = []

    # --- BƯỚC 7: SUBTITLE (.ASS) ---
    print("7️⃣ Khởi tạo file phụ đề...")
    try:
        ass_file = create_subtitles(words)
    except Exception as e:
        print(f"⚠️ Lỗi tạo Subtitle: {e}")
        ass_file = None

    # ==========================
    # 8. RENDER VIDEO
    # ==========================
    print("8️⃣ Render video")
    output = f"output_{index}.mp4"
    
    try:
        # BỎ keyword 'audio=', 'subtitle=' nếu tên biến trong render.py khác
        # Hoặc truyền đúng tên biến đã định nghĩa:
        render_video(
            audio_path=audio,    # Sửa từ 'audio' thành 'audio_path'
            subtitles=ass_file,  # Sửa từ 'subtitle' thành 'subtitles'
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
        #full_msg = f"🎬 **Video mới đã sẵn sàng!**\n\n📌 Chủ đề: {topic}\n🔗 Link: {url}\n\n📝 **Caption:**\n{content}"
        full_msg = f"{content}"
        send_message(full_msg)
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

    # Đảm bảo có thư mục log
    os.makedirs("logs", exist_ok=True)

    try:
        topics = generate_topics()
    except Exception as e:
        print(f"⚠️ Lỗi lấy Topic AI: {e}")
        topics = []

    # Nếu AI lỗi, dùng topic mặc định
    if not topics:
        topics = ["Nhận định thị trường chứng khoán hôm nay"]

    # Giới hạn 1 video mỗi lần chạy để tránh quá tải/timeout
    for i, topic in enumerate(topics[:1]):
        try:
            process_video(topic, i)
        except Exception as e:
            print(f"❌ Pipeline sập tại Video {i}: {e}")

    print("\n✅ TẤT CẢ TIẾN TRÌNH ĐÃ HOÀN TẤT")
    print("="*40)


if __name__ == "__main__":
    main()
