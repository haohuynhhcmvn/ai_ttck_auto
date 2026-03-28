# ==============================
# RENDER VIDEO PRO MAX (ULTRA FAST)
# ==============================

import subprocess
import os
import random
from moviepy.editor import AudioFileClip
from PIL import Image

# Giả định bạn đã có file overlay.py với hàm draw_overlay
try:
    from overlay import draw_overlay
except ImportError:
    print("⚠️ Không tìm thấy module overlay. Hãy đảm bảo file overlay.py tồn tại.")
    def draw_overlay(data): return None

def render_video(audio_path, subtitles, output, topic=None, market_data=None, script=None):
    print(f"🎬 Đang render video: {output}...")

    # Lấy thời lượng audio chính xác
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    audio.close() # Giải phóng file để FFmpeg truy cập

    # ==========================
    # 1. TẠO OVERLAY (PNG)
    # ==========================
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

    # ==========================
    # 2. CẤU HÌNH INPUT BACKGROUND
    # ==========================
    # Nếu có background.mp4 thì loop, nếu không thì dùng màu đen
    if os.path.exists("background.mp4"):
        start_time = random.uniform(0, 10) # Random đoạn bắt đầu cho đỡ trùng lặp
        bg_input = ["-ss", str(start_time), "-stream_loop", "-1", "-i", "background.mp4"]
    else:
        bg_input = ["-f", "lavfi", "-i", f"color=c=black:s=720x1280:r=30"]

    # ==========================
    # 3. XỬ LÝ ĐƯỜNG DẪN SUBTITLE (QUAN TRỌNG)
    # ==========================
    # FFmpeg filter 'ass' rất kén đường dẫn trên Windows (cần double escape)
    safe_sub_path = subtitles.replace("\\", "/").replace(":", "\\:") if subtitles else None

    # ==========================
    # 4. BUILD FILTER COMPLEX
    # ==========================
    # Input 0: Background
    # Input 1: Overlay PNG (nếu có)
    # Input 2 hoặc 1: Audio
    
    filter_parts = []
    # Scale và Crop background về chuẩn 9:16 (720x1280)
    filter_parts.append("[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280[bg]")
    
    last_v = "[bg]"
    audio_idx = 1

    if has_overlay:
        # Đè overlay lên background
        filter_parts.append(f"{last_v}[1:v]overlay=0:0[tmp_v]")
        last_v = "[tmp_v]"
        audio_idx = 2 # Audio sẽ là input thứ 3 (index 2)

    if safe_sub_path:
        # Add Subtitles
        filter_parts.append(f"{last_v}ass='{safe_sub_path}'[v]")
    else:
        filter_parts.append(f"{last_v}copy[v]")

    filter_complex = ";".join(filter_parts)

    # ==========================
    # 5. EXECUTE FFMPEG
    # ==========================
    cmd = ["ffmpeg", "-y"]
    cmd += bg_input # Input 0
    
    if has_overlay:
        cmd += ["-loop", "1", "-i", overlay_path] # Input 1

    cmd += ["-i", audio_path] # Input 1 hoặc 2

    cmd += [
        "-filter_complex", filter_complex,
        "-map", "[v]",
        "-map", f"{audio_idx}:a",
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "ultrafast", # Tốc độ tối đa
        "-crf", "23",           # Cân bằng chất lượng/dung lượng
        "-pix_fmt", "yuv420p",  # Đảm bảo xem được trên mọi điện thoại
        "-c:a", "aac",
        "-b:a", "128k",
        "-shortest",            # Kết thúc khi audio hết
        output
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✅ Render thành công: {output}")
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg Render Error: {e.stderr.decode()}")
    finally:
        # Dọn dẹp file tạm
        if os.path.exists(overlay_path):
            os.remove(overlay_path)

    return output
