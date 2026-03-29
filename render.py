import subprocess
import os
import random
import glob
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
from PIL import Image

try:
    from overlay import draw_overlay
except ImportError:
    def draw_overlay(data): return None

def create_random_slideshow(folder_path, target_duration):
    """Tạo video nền từ ảnh ngẫu nhiên với hiệu ứng chuyển cảnh mờ dần"""
    print(f"🖼️ Đang tạo slideshow từ: {folder_path}")
    search_path = os.path.join(folder_path, "*.jpg")
    all_images = glob.glob(search_path)
    
    if not all_images:
        print("⚠️ Không tìm thấy ảnh trong asset/picture! Sử dụng nền đen.")
        return None

    random.shuffle(all_images)
    
    clips = []
    current_total_dur = 0
    img_display_dur = 4  # Mỗi ảnh hiện 4 giây
    transition_dur = 1   # Chuyển cảnh mờ dần trong 1 giây

    for img_p in all_images:
        try:
            # Load ảnh, resize ép về chiều cao 1280 (9:16)
            clip = ImageClip(img_p).set_duration(img_display_dur).resize(height=1280)
            # Căn giữa và cắt đúng khung 720x1280
            clip = clip.set_position("center").canvas_size((720, 1280))
            # Hiệu ứng mờ dần
            clip = clip.crossfadein(transition_dur).crossfadeout(transition_dur)
            
            clips.append(clip)
            current_total_dur += (img_display_dur - transition_dur)
            
            if current_total_dur >= target_duration:
                break
        except Exception as e:
            print(f"❌ Lỗi xử lý ảnh {img_p}: {e}")
            continue

    if not clips:
        return None

    # Ghép các clip ảnh (method="compose" để giữ hiệu ứng crossfade)
    final_video = concatenate_videoclips(clips, method="compose")
    temp_bg_name = f"temp_bg_{random.randint(100,999)}.mp4"
    
    # Xuất file nền tạm thời (tắt audio, tắt logger để sạch log)
    final_video.write_videofile(temp_bg_name, fps=30, codec="libx264", audio=False, logger=None)
    return temp_bg_name

def render_video(audio_path, subtitles, output, topic=None, market_data=None, script=None):
    print(f"🎬 Bắt đầu Render hệ thống (9:16): {output}...")
    temp_bg_file = None

    # --- 1. LẤY THỜI LƯỢNG AUDIO ---
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    audio.close()

    # --- 2. TẠO OVERLAY TĨNH (DANH SÁCH MÃ CP) ---
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
    safe_sub_path = subtitles.replace("\\", "/").replace(":", "\\:") if subtitles else None

    # --- 4. CẤU HÌNH INPUTS ---
    cmd = ["ffmpeg", "-y"]

    # Ưu tiên tạo Slideshow từ ảnh
    picture_folder = "asset/picture"
    if os.path.exists(picture_folder):
        temp_bg_file = create_random_slideshow(picture_folder, duration)

    if temp_bg_file:
        cmd += ["-i", temp_bg_file]
    elif os.path.exists("background.mp4"):
        start_time = random.uniform(0, 5)
        cmd += ["-ss", str(start_time), "-stream_loop", "-1", "-i", "background.mp4"]
    else:
        cmd += ["-f", "lavfi", "-i", f"color=c=black:s=720x1280:r=30:d={duration}"]

    # Input Overlay PNG
    if has_overlay:
        cmd += ["-loop", "1", "-t", str(duration), "-i", overlay_path]

    # Input Audio
    cmd += ["-i", audio_path]
    
    audio_idx = 2 if has_overlay else 1

    # --- 5. FILTER COMPLEX (ÉP CHUẨN 9:16 VÀ CHỒNG LỚP) ---
    filter_parts = []
    
    # Ép background về chuẩn 9:16, khóa SAR để không méo hình
    filter_parts.append("[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1[bg]")
    last_v = "[bg]"

    # Đè Overlay PNG
    if has_overlay:
        filter_parts.append(f"{last_v}[1:v]overlay=0:0:shortest=1[v_over]")
        last_v = "[v_over]"

    # Đè Ticker chạy ngang ở tâm
    if safe_sub_path:
        filter_parts.append(f"{last_v}ass='{safe_sub_path}'[final_v]")
    else:
        filter_parts.append(f"{last_v}copy[final_v]")

    cmd += ["-filter_complex", ";".join(filter_parts)]

    # --- 6. XUẤT FILE (OUTPUT SETTINGS) ---
    cmd += [
        "-map", "[final_v]",
        "-map", f"{audio_idx}:a",
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "21",          # Tăng chất lượng ảnh một chút vì là slideshow
        "-aspect", "9:16",     # Khóa cứng tỷ lệ 9:16 ở Metadata
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        output
    ]

    # --- 7. THỰC THI ---
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Render hoàn tất: {output}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi FFmpeg: {e.stderr}")
    finally:
        # Dọn dẹp file tạm để giải phóng ổ cứng
        for f in [overlay_path, temp_bg_file]:
            if f and os.path.exists(f):
                os.remove(f)

    return output
