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
    print(f"🎬 Đang render video: {output}...")

    # Lấy thời lượng audio
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    audio.close()

    # 1. Tạo Overlay PNG
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

    # 2. Xử lý Subtitle Path (Dành cho Ticker .ass)
    safe_sub_path = subtitles.replace("\\", "/").replace(":", "\\:") if subtitles else None

    # 3. Xây dựng Command FFmpeg chuyên nghiệp
    cmd = ["ffmpeg", "-y"]

    # Input 0: Background
    if os.path.exists("background.mp4"):
        start_time = random.uniform(0, 5)
        cmd += ["-ss", str(start_time), "-stream_loop", "-1", "-i", "background.mp4"]
    else:
        cmd += ["-f", "lavfi", "-i", "color=c=black:s=720x1280:r=30"]

    # Input 1 (Nếu có): Overlay PNG
    if has_overlay:
        cmd += ["-loop", "1", "-t", str(duration), "-i", overlay_path]

    # Input Audio (Input cuối cùng)
    cmd += ["-i", audio_path]
    
    # Xác định index của Audio (Nếu có overlay thì audio là 2, không thì là 1)
    audio_input_index = 2 if has_overlay else 1

    # 4. Filter Complex (Xếp chồng các lớp)
    filter_chains = []
    # Lớp 0: Scale/Crop background
    filter_chains.append("[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280[bg]")
    
    last_label = "[bg]"
    if has_overlay:
        # Lớp 1: Đè PNG lên BG
        filter_chains.append(f"{last_label}[1:v]overlay=0:0:shortest=1[v_over]")
        last_label = "[v_over]"

    if safe_sub_path:
        # Lớp 2: Đè Ticker (ASS) lên trên cùng
        filter_chains.append(f"{last_label}ass='{safe_sub_path}'[final_v]")
    else:
        filter_chains.append(f"{last_label}copy[final_v]")

    cmd += ["-filter_complex", ";".join(filter_chains)]

    # 5. Output Settings
    cmd += [
        "-map", "[final_v]",
        "-map", f"{audio_input_index}:a",
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "128k",
        "-movflags", "+faststart",
        output
    ]

    try:
        # Chạy và bắt lỗi chi tiết
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Render thành công: {output}")
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg Error: {e.stderr}")
    finally:
        if os.path.exists(overlay_path):
            os.remove(overlay_path)

    return output
