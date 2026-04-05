# ==============================================================
# 🚀 MAIN PIPELINE PRO MAX (BẢN CHUẨN - TRỰC QUAN - STABLE)
# ==============================================================

import os
import sys
import time
import uuid
from datetime import datetime, timezone, timedelta

# Fix lỗi MoviePy trên các môi trường server/GHA
os.environ["IMAGEIO_FFMPEG_EXE"] = "ffmpeg" 
from moviepy.editor import AudioFileClip

# --- KIỂM TRA IMPORT MODULES ---
print("🔄 Đang tải các modules hệ thống...")
try:
    from topic_ai import generate_topics
    from generate_script import generate_script, call_gemini
    from content_ai import script_to_content 
    from tts import text_to_speech
    import sub_utils 
    # MỚI: Import thêm create_hook_image từ render.py để chủ động lấy ảnh làm Thumbnail
    from render import render_video, create_hook_image 
    from upload_youtube import upload_video_with_thumbnail
    from telegram import send_message, send_video
    from market_data import get_market_data
    from text_utils import save_text, clean_text_for_tts
    print("✅ Load modules thành công!\n")
except ImportError as e:
    print(f"❌ Thiếu module hệ thống: {e}")
    sys.exit(1)

# ==============================================================
# HÀM XỬ LÝ 1 VIDEO ĐỘC LẬP
# ==============================================================
def process_video(topic, index):
    print("="*60)
    print(f"🎬 BẮT ĐẦU XỬ LÝ VIDEO {index + 1}: {topic}")
    print("="*60)

    # --- BƯỚC 1: MARKET DATA ---
    print("1️⃣ [DỮ LIỆU]: Đang lấy số liệu thị trường (Market Data)...")
    market_data = {}
    try: 
        market_data = get_market_data()
        print("   ✅ Lấy dữ liệu thành công.")
    except Exception as e: 
        print(f"   ⚠️ Lỗi lấy Market Data (Sẽ chạy không có overlay): {e}")

    # --- BƯỚC 2: GENERATE SCRIPT ---
    print("2️⃣ [KỊCH BẢN]: AI đang biên soạn nội dung (Script)...")
    script = generate_script(topic, market_data)
    if not script or len(script) < 20: 
        print("   ❌ Script lỗi hoặc quá ngắn → Hủy bỏ video này.")
        return
    save_text(script, f"raw_v{index}")
    print("   ✅ Kịch bản đã sẵn sàng.")

    # --- BƯỚC 3: CLEAN TEXT ---
    print("3️⃣ [XỬ LÝ CHỮ]: Đang làm sạch văn bản cho giọng đọc AI...")
    clean_script = clean_text_for_tts(script)

    # --- BƯỚC 4: HOOK & SOCIAL POST ---
    print("4️⃣ [MARKETING]: AI đang tạo câu Hook giật gân và bài đăng Social...")
    content_data = script_to_content(script, topic)
    video_hook = content_data.get("video_hook", f"BẢN TIN {topic.upper()}")
    social_post = content_data.get("social_post", "Cập nhật thị trường chứng khoán mới nhất!")
    print(f"   🔥 Hook chốt được: '{video_hook}'")

    # --- BƯỚC 5: TEXT-TO-SPEECH (TTS) ---
    print("5️⃣ [ÂM THANH]: Đang tạo giọng đọc AI MC...")
    audio = text_to_speech(clean_script)
    if not audio or not os.path.exists(audio): 
        print("   ❌ Lỗi tạo file Audio → Hủy bỏ video này.")
        return
    
    audio_clip = AudioFileClip(audio)
    duration = audio_clip.duration
    audio_clip.close()
    print(f"   ✅ File Audio dài: {round(duration, 1)} giây.")

    # --- BƯỚC 6 & 7: TICKER SUBTITLES ---
    print("6️⃣ [PHỤ ĐỀ]: Đang trích xuất tin vắn làm Ticker chạy ngang...")
    ass_file = None
    try:
        summary_text = call_gemini(f"Trích 5 tin vắn cực ngắn, VIẾT HOA từ kịch bản sau: {script}. Ngăn cách bằng ' • '") or topic
        ass_file = sub_utils.create_ticker_sub(summary_text, duration)
        print("   ✅ Đã tạo phụ đề Ticker.")
    except Exception as e: 
        print(f"   ⚠️ Lỗi tạo Ticker: {e}")

    # --- BƯỚC 8: THIẾT LẬP THUMBNAIL (BƯỚC QUAN TRỌNG CHO YOUTUBE) ---
    print("7️⃣ [HÌNH ẢNH]: Đang xuất file ảnh Hook làm Thumbnail YouTube...")
    hook_output = f"thumb_youtube_{index}_{uuid.uuid4().hex[:5]}.png"
    try:
        # Gọi thẳng hàm create_hook_image để chắc chắn ta có 1 file ảnh giữ lại được
        create_hook_image(video_hook, hook_output)
        print(f"   ✅ Đã lưu Thumbnail: {hook_output}")
    except Exception as e:
        print(f"   ⚠️ Không tạo được Thumbnail riêng: {e}")
        hook_output = None

    # --- BƯỚC 9: RENDER VIDEO TỔNG HỢP ---
    video_output = f"final_video_{index}_{uuid.uuid4().hex[:5]}.mp4"
    print(f"8️⃣ [RENDER]: Đang ghép nối Video (Có thể mất vài phút)...")
    try:
        render_result = render_video(
            audio_path=audio,
            subtitles=ass_file,
            output=video_output,
            topic=topic,
            market_data=market_data,
            script=script,
            video_hook=video_hook,
            ticker_ass=ass_file 
        )
        if not os.path.exists(video_output): 
            raise Exception("File video đầu ra không được tạo ra!")
        print(f"   ✅ Render thành công: {video_output}")
    except Exception as e:
        print(f"   ❌ Render sập: {e}")
        return # Nếu render xịt thì dừng luôn video này

    # ==============================================================
    # KHÚC PHÂN PHỐI NỘI DUNG
    # ==============================================================
    vn_tz = timezone(timedelta(hours=7))
    date_str = datetime.now(vn_tz).strftime("%d/%m/%Y")
    header_title = f"BẢN TIN TÀI CHÍNH 247 - NGÀY {date_str}"

    # --- BƯỚC 10: TELEGRAM ---
    print("9️⃣ [TELEGRAM]: Đang gửi thông báo lên Channel...")
    try:
        send_message(f"🚨 **{header_title}**\n\n{social_post}")
        send_video(video_output)
        print("   ✅ Đã gửi Telegram.")
    except Exception as e: 
        print(f"   ⚠️ Lỗi Telegram: {e}")

    # --- BƯỚC 11: YOUTUBE SHORTS ---   
    print("🔟 [YOUTUBE]: Đang đẩy video lên Shorts kèm Thumbnail...")
    try:
        url_youtube = upload_video_with_thumbnail(
            file_path=video_output,
            hook_img_path=hook_output, 
            title_str=header_title,
            description_str=social_post
        )
        if url_youtube:
            print(f"   ✅ Upload YouTube thành công! Link: {url_youtube}")
            send_message(f"📺 **Video đã lên YouTube Shorts:**\n{url_youtube}")
    except Exception as e:
        print(f"   ⚠️ Lỗi upload YouTube: {e}")

    # --- BƯỚC 12: DỌN DẸP ---
    print("🧹 [DỌN DẸP]: Đang xóa rác hệ thống...")
    for f in [audio, ass_file, video_output, hook_output]:
        if f and os.path.exists(f): 
            try: os.remove(f)
            except: pass
    print(f"✅ HOÀN TẤT VIDEO {index + 1}!\n")

# ==============================================================
# ĐỘNG CƠ CHÍNH (MAIN ENGINE)
# ==============================================================
def main():
    print("\n" + "*"*60)
    print("🔥 HỆ THỐNG AUTO-VIDEO STOCK 2.0 KHỞI ĐỘNG 🔥")
    print("*"*60 + "\n")

    try:
        print("Đang yêu cầu AI định hướng chủ đề hôm nay...")
        topics = generate_topics()
        if not topics: raise ValueError("AI không trả về chủ đề nào.")
    except Exception as e:
        print(f"⚠️ Lỗi sinh Topic: {e} -> Chuyển sang chủ đề dự phòng.")
        topics = ["Tổng hợp diễn biến dòng tiền thị trường chứng khoán hôm nay"]

    # Chạy số lượng video mong muốn (topics[:1] là chạy 1 video)
    total_videos = len(topics[:1])
    for i, topic in enumerate(topics[:1]):
        try:
            process_video(topic, i)
        except Exception as e:
            print(f"❌ Lỗi nghiêm trọng toàn cục tại Video {i+1}: {e}")
        
        if i < total_videos - 1:
            print("⏳ Nghỉ 10 giây trước khi làm video tiếp theo để tránh Limit API...\n")
            time.sleep(10)

    print("\n" + "*"*60)
    print("🎉 CHIẾN DỊCH HÔM NAY ĐÃ HOÀN TẤT TỐT ĐẸP! 🎉")
    print("*"*60)

if __name__ == "__main__":
    main()
