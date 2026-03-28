# ==============================
# MAIN PIPELINE (FINAL STABLE)
# ==============================

# Import modules
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


# ==============================
# PROCESS 1 VIDEO
# ==============================
def process_video(topic, index):
    print(f"\n🚀 Processing video {index}: {topic}")

    # ==========================
    # 1. GENERATE SCRIPT
    # ==========================
    print("1. AI viết nội dung")
    script = generate_script(topic)
    # 💾 lưu bản gốc
    save_text(script, "raw")
    # ==========================
    # CLEAN TEXT (TRƯỚC TTS)
    # ==========================
    print("2. Clean text cho TTS")
    clean_script = clean_text_for_tts(script)
    
    # 💾 lưu bản clean
    save_text(clean_script, "clean")

    # ==========================
    # 2. SOCIAL CONTENT
    # ==========================
    print("2. Tạo content social")
    content = script_to_content(script, topic)

    # ==========================
    # 3. MARKET DATA
    # ==========================
    print("3. Lấy dữ liệu thị trường")
    try:
        market_data = get_market_data()
    except Exception as e:
        print("⚠️ Lỗi data:", e)
        market_data = {}

    # ==========================
    # 4. TEXT TO SPEECH
    # ==========================
    print("4. Tạo audio")
    audio = text_to_speech(script)

    # ==========================
    # 5. TRANSCRIBE
    # ==========================
    print("5. Timestamp từng từ")
    words = transcribe(audio)

    # ==============================
    # 6. SUBTITLE
    # ==============================
    print("6. Tạo subtitle")
    ass_file = create_subtitles(words)
    
    # ==========================
    # 7. RENDER VIDEO
    # ==========================
    print("7. Render video")
    output = f"output_{index}.mp4"

    render_video(
    audio,
    ass_file,   # 🔥 đổi từ subs → ass_file
    output,
    topic,
    market_data,
    script
    )

    # ==========================
    # 8. UPLOAD YOUTUBE
    # ==========================
    print("8. Upload YouTube")
    try:
        url = upload_video(output)
    except Exception as e:
        print("⚠️ Upload lỗi:", e)
        url = "Upload lỗi"

    # ==========================
    # 9. TELEGRAM
    # ==========================
    print("9. Gửi Telegram")

    try:
        send_message(f"🔥 {content}\n{url}")
    except Exception as e:
        print("⚠️ gửi text lỗi:", e)

    try:
        send_video(output)
    except Exception as e:
        print("⚠️ gửi video lỗi:", e)


# ==============================
# MAIN
# ==============================
def main():
    print("🔥 START PIPELINE")

    topics = generate_topics()

    # fallback nếu AI lỗi
    if not topics:
        topics = ["VNINDEX hôm nay có gì?"]

    # giới hạn để tránh timeout GitHub
    topics = topics[:1]

    for i, topic in enumerate(topics):
        try:
            process_video(topic, i)
        except Exception as e:
            print("❌ Lỗi pipeline:", e)

    print("✅ DONE ALL")


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    main()
