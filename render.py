import subprocess
import os
import random
from moviepy.editor import AudioFileClip
from PIL import Image

try:
    from overlay import draw_overlay
except ImportError:
    def draw_overlay(data): return None

def render_video(audio_path, subtitles, output, topic=None, market_data=None, script=None):
    print(f"🎬 Đang render video chuẩn 9:16: {output}...")

    # --- 1. LẤY THỜI LƯỢNG AUDIO ---
    # Mục đích: Biết chính xác video dài bao nhiêu giây để khớp hình và chữ.
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    audio.close()

    # --- 2. TẠO OVERLAY TĨNH (DANH SÁCH MÃ CP) ---
    # Dữ liệu: Cần 'market_data' từ hàm lấy tin chứng khoán.
    overlay_path = f"temp_overlay_{random.randint(100,999)}.png"
    has_overlay = False
    if market_data:
        try:
            img_array = draw_overlay(market_data)
            if img_array is not None:
                Image.fromarray(img_array).save(overlay_path)
                has_overlay = True
        except Exception as e:
            print(f"⚠️ Lỗi vẽ overlay: {e}")

    # --- 3. CHUẨN HÓA ĐƯỜNG DẪN SUBTITLE ---
    # Cần thiết: Giúp FFmpeg trên Windows không bị lỗi dấu gạch chéo.
    safe_sub_path = subtitles.replace("\\", "/").replace(":", "\\:") if subtitles else None

    # --- 4. CẤU HÌNH INPUTS ---
    cmd = ["ffmpeg", "-y"]

    # Input 0: Background. Buộc phải xử lý loop và resize về 720x1280 (9:16).
    if os.path.exists("background.mp4"):
        start_time = random.uniform(0, 5)
        cmd += ["-ss", str(start_time), "-stream_loop", "-1", "-i", "background.mp4"]
    else:
        # Nếu thiếu file, tự tạo nền đen chuẩn 9:16.
        cmd += ["-f", "lavfi", "-i", "color=c=black:s=720x1280:r=30"]

    # Input 1: Overlay PNG (Lớp biểu đồ/danh sách mã)
    if has_overlay:
        cmd += ["-loop", "1", "-t", str(duration), "-i", overlay_path]

    # Input 2: Audio (Tiếng MC đọc)
    cmd += ["-i", audio_path]
    
    # Chỉ số để map audio chuẩn xác
    audio_idx = 2 if has_overlay else 1

    # --- 5. FILTER COMPLEX (TRÁI TIM CỦA RENDER) ---
    # Ép mọi thứ về chuẩn 9:16 và chồng lớp.
    filter_parts = []
    
    # BƯỚC A: Ép Background về 720x1280. Dùng 'force_original_aspect_ratio' để không bị méo hình.
    filter_parts.append("[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280[bg]")
    last_v = "[bg]"

    # BƯỚC B: Chèn Overlay PNG lên trên Background.
    if has_overlay:
        filter_parts.append(f"{last_v}[1:v]overlay=0:0:shortest=1[v_over]")
        last_v = "[v_over]"

    # BƯỚC C: Chèn Ticker chạy ngang (File .ass từ sub_utils).
    # Lớp này nằm trên cùng để chạy xuyên qua giữa bảng danh sách mã.
    if safe_sub_path:
        filter_parts.append(f"{last_v}ass='{safe_sub_path}'[final_v]")
    else:
        filter_parts.append(f"{last_v}copy[final_v]")

    cmd += ["-filter_complex", ";".join(filter_parts)]

    # --- 6. XUẤT FILE (OUTPUT SETTINGS) ---
    cmd += [
        "-map", "[final_v]",           # Lấy luồng video đã trộn
        "-map", f"{audio_idx}:a",      # Lấy luồng âm thanh MC
        "-t", str(duration),           # Cắt video đúng bằng độ dài tiếng
        "-c:v", "libx264",             # Codec phổ biến cho điện thoại
        "-preset", "ultrafast",        # Ưu tiên tốc độ
        "-crf", "23",                  # Chất lượng rõ nét
        "-pix_fmt", "yuv420p",         # Tương thích TikTok/Facebook
        "-c:a", "aac", "-b:a", "128k", # Nén âm thanh chuẩn
        "-movflags", "+faststart",     # Tối ưu upload
        output
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Đã xuất video 9:16 thành công: {output}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi Render FFmpeg: {e.stderr}")
    finally:
        if os.path.exists(overlay_path):
            os.remove(overlay_path)

    return output
