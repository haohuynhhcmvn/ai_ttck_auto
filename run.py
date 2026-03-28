# ==============================
# MAIN PIPELINE (FINAL PRO)
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
    print("1️⃣ AI viết nội dung")
    script = generate_script(topic)

    # 💾 lưu bản gốc
    save_text(script, "raw")

    # ==========================
    # 2. CLEAN TEXT (TTS)
    # ==========================
    print("2️⃣ Clean text cho TTS")
    clean_script = clean_text_for_tts(script)

    # 💾 lưu bản clean
    save_text(clean_script, "clean")

    # ==========================
    # 3. SOCIAL CONTENT
    # ==========================
    print("3️⃣ Tạo content social")
    content = script_to_content(script, topic)

    # ==========================
    # 4. MARKET DATA
    # ==========================
    print("4️⃣ Lấy dữ liệu thị trường")
    try:
        market_data = get_market_data()
    except Exception as e:
        print("⚠️ Lỗi data:", e)
        market_data = {}

    # ==========================
    # 5. TEXT TO SPEECH
    # ==========================
    print("5️⃣ Tạo audio")
    audio = text_to_speech(clean_script)  # 🔥 dùng clean_script

    # ==========================
    # 6. TRANSCRIBE
    # ==========================
    print("6️⃣ Timestamp từng từ")
    words = transcribe(audio)

    # ==========================
    # 7. SUBTITLE (ASS)
    # ==========================
    print("7️⃣ Tạo subtitle")
    ass_file = create_subtitles(words)

    # ==========================
    # 8. RENDER VIDEO
    # ==========================
    print("8️⃣ Render video")
    output = f"output_{index}.mp4"

    render_video(
        audio,
        ass_file,   # 🔥 dùng ASS subtitle
        output,
        topic,
        market_data,
        script
    )

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
    print("🔟 Gửi Telegram")

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

    # 🔥 giới hạn để tránh timeout GitHub
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
