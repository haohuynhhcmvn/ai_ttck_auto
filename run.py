# ==============================
# MAIN PIPELINE (FINAL PRO MAX)
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
    print("1️⃣ Generate script")
    script = generate_script(topic)

    if not script or len(script) < 20:
        print("❌ Script lỗi → skip")
        return

    # 💾 lưu raw
    save_text(script, "raw")

    # ==========================
    # 2. CLEAN TEXT FOR TTS
    # ==========================
    print("2️⃣ Clean text for TTS")
    clean_script = clean_text_for_tts(script)

    # 💾 lưu clean
    save_text(clean_script, "clean")

    # ==========================
    # 3. SOCIAL CONTENT
    # ==========================
    print("3️⃣ Generate social content")
    content = script_to_content(script, topic)

    # ==========================
    # 4. MARKET DATA
    # ==========================
    print("4️⃣ Fetch market data")
    try:
        market_data = get_market_data()
    except Exception as e:
        print("⚠️ Market data error:", e)
        market_data = {}

    # ==========================
    # 5. TEXT TO SPEECH
    # ==========================
    print("5️⃣ Generate audio")
    try:
        audio = text_to_speech(clean_script)  # 🔥 FIX QUAN TRỌNG
    except Exception as e:
        print("❌ TTS lỗi:", e)
        return

    # ==========================
    # 6. TRANSCRIBE
    # ==========================
    print("6️⃣ Transcribe words")
    try:
        words = transcribe(audio)
    except Exception as e:
        print("⚠️ Transcribe lỗi:", e)
        words = []

    # ==========================
    # 7. SUBTITLE (ASS)
    # ==========================
    print("7️⃣ Create subtitle")
    try:
        ass_file = create_subtitles(words)
    except Exception as e:
        print("⚠️ Subtitle lỗi:", e)
        ass_file = None

    # ==========================
    # 8. RENDER VIDEO
    # ==========================
    print("8️⃣ Render video")
    output = f"output_{index}.mp4"

    try:
        render_video(
            audio,
            ass_file,
            output,
            topic,
            market_data,
            script
        )
    except Exception as e:
        print("❌ Render lỗi:", e)
        return

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
