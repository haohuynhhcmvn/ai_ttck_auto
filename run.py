
# ==============================
# MAIN PIPELINE FILE
# ==============================

# Import all modules of the system
from topic_ai import generate_topics, pick_best_topic   # AI chọn topic
from viral_clone import generate_variations             # nhân bản topic
from generate_script import generate_script             # tạo script
from tts import text_to_speech                          # tạo giọng đọc
from transcribe import transcribe                       # lấy timestamp
from subtitle import create_subtitles                   # tạo subtitle
from render import render_video                         # render video
from upload_youtube import upload_video                 # upload youtube
from telegram import send_message                       # gửi telegram

# Hàm xử lý 1 video hoàn chỉnh
def process_video(topic, index):
    print(f"Processing video {index}: {topic}")

    print(f"1. AI viết nội dung")
    script = generate_script(topic)  # AI viết nội dung

    print(f"2. Tạo audio")
    audio = text_to_speech(script)   # tạo audio

    print(f"3. Timestamp từng từ")
    words = transcribe(audio)        # timestamp từng từ

    print(f"4. Tạo subtitle")
    subs = create_subtitles(words)   # tạo subtitle

    print(f"5. Render video")   
    output = f"output_{index}.mp4"
    render_video(audio, subs, output)  # render video
    
    print(f"6. Upload youtube")
    #url = upload_video(output)       # upload youtube

    print(f"7. Gửi telegram")
    send_message(f"🔥 {topic}\n{url}")  # gửi telegram


def main():
    topics = generate_topics()                 # lấy topic từ AI
    main_topic = pick_best_topic(topics)       # chọn topic tốt nhất

    variations = generate_variations(main_topic)  # clone topic
    variations = variations[:1]               # giới hạn để tránh timeout

    for i, topic in enumerate(variations):
        process_video(topic, i)

if __name__ == "__main__":
    main()
