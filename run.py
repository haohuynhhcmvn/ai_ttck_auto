# ==============================
# MAIN PIPELINE (FINAL PRO MAX)
# ==============================

import os
from market_data import get_market_data
from generate_script import generate_script
from text_utils import save_text, clean_text_for_tts
from tts import text_to_speech
from content_ai import script_to_content
from transcribe import transcribe
from subtitle import create_subtitles
from render import render_video
from upload_youtube import upload_video
from telegram import send_message, send_video
from topic_ai import generate_topics

# ==============================
# PROCESS 1 VIDEO
# ==============================
def process_video(topic, index):
    print(f"\n🚀 Đang xử lý Video {index + 1}: {topic}")

    # 1. LẤY DỮ LIỆU THỊ TRƯỜNG (PHẢI CÓ TRƯỚC)
    print("1️⃣ Đang lấy dữ liệu thị trường thực tế...")
    try:
        # market_data nên trả về dict: {'gain_text': '...', 'lose_text': '...', 'index_status': '...'}
        market_data = get_market_data()
    except Exception as e:
        print(f"⚠️ Lỗi lấy data: {e}")
        market_data = {"gain_text": "Đang cập nhật", "lose_text": "Đang cập nhật"}

    # 2. GENERATE SCRIPT (DỰA TRÊN DATA THẬT)
    print("2️⃣ AI đang viết Script dựa trên dữ liệu phiên hôm nay...")
    script = generate_script(topic, market_data)

    if not script or len(script) < 50:
        print("❌ Script quá ngắn hoặc lỗi -> Bỏ qua video này.")
        return

    save_text(script, f"raw_{index}")

    # 3. LÀM SẠCH TEXT CHO GIỌNG ĐỌC
    print("3️⃣ Chuẩn hóa văn bản cho TTS...")
    clean_script = clean_text_for_tts(script)
    save_text(clean_script, f"clean_{index}")

    # 4. TẠO CONTENT SOCIAL (CAPTION TIKTOK/YOUTUBE)
    print("4️⃣ Tạo nội dung Social...")
    social_content = script_to_content(script, topic)

    # 5. TEXT TO SPEECH (AUDIO)
    print("5️⃣ Đang chuyển đổi văn bản thành giọng nói...")
    try:
        audio_file = text_to_speech(clean_script)
    except Exception as e:
        print(f"❌ Lỗi TTS: {e}")
        return

    # 6. TRANSCRIBE (LẤY TIMESTAMP TỪNG TỪ)
    print("6️⃣ Đang tách chữ từ âm thanh (Transcribe)...")
    try:
        words = transcribe(audio_file)
    except Exception as e:
        print(f"⚠️ Lỗi Transcribe: {e}")
        words = []

    # 7. TẠO SUBTITLE (FILE .ASS)
    print("7️⃣ Đang tạo file phụ kiện Subtitle...")
    ass_file = None
    if words:
        try:
            ass_file = create_subtitles(words)
        except Exception as e:
            print(f"⚠️ Lỗi tạo Sub: {e}")

    # 8. RENDER VIDEO (KẾT HỢP TẤT CẢ)
    print("8️⃣ Đang Render Video hoàn chỉnh...")
    output_filename = f"final_video_{index}.mp4"
    try:
        render_video(
            audio=audio_file,
            subtitle=ass_file,
            output=output_filename,
            topic=topic,
            market_data=market_data,
            script=script
        )
    except Exception as e:
        print(f"❌ Lỗi Render: {e}")
        return

    # 9. UPLOAD & NOTIFY (BƯỚC CUỐI)
    # ==========================
    # 9. UPLOAD YOUTUBE
    # ==========================
    print("9️⃣ Upload YouTube")

    try:
        url = upload_video(output)
    except Exception as e:
        print("⚠️ Upload lỗi:", e)
        url = "Upload lỗi"

    # ==========================
    # 10. TELEGRAM
    # ==========================
    print("🔟 Send Telegram")

    try:
        send_message(f"{content}\n{url}")
    except Exception as e:
        print("⚠️ Telegram text lỗi:", e)

    try:
        send_video(output)
    except Exception as e:
        print("⚠️ Telegram video lỗi:", e)


# ==============================
# MAIN
# ==============================
def main():
    print("🔥 START PIPELINE")

    try:
        topics = generate_topics()
    except Exception as e:
        print("⚠️ Topic AI lỗi:", e)
        topics = []

    # fallback
    if not topics:
        topics = ["Thị trường chứng khoán hôm nay có gì?"]

    # 🔥 tránh timeout GitHub
    topics = topics[:1]

    for i, topic in enumerate(topics):
        try:
            process_video(topic, i)
        except Exception as e:
            print("❌ Pipeline crash:", e)

    print("✅ DONE ALL")


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    main()
