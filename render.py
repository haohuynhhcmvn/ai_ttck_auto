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
    """Tạo video nền từ ảnh PNG ngẫu nhiên với hiệu ứng chuyển cảnh mờ dần"""
    print(f"🖼️ Đang tạo slideshow từ: {folder_path}")
    # ĐỔI THÀNH .PNG THEO YÊU CẦU
    search_path = os.path.join(folder_path, "*.png")
    all_images = glob.glob(search_path)
    
    if not all_images:
        print("⚠️ Không tìm thấy ảnh PNG trong asset/picture!")
        return None

    random.shuffle(all_images)
    
    clips = []
    current_total_dur = 0
    img_display_dur = 4 
    transition_dur = 1  

    for img_p in all_images:
        try:
            # ÉP CỨNG kích thước ngay từ bước tạo clip để tránh sai lệch
            clip = ImageClip(img_p).set_duration(img_display_dur)
            
            # Sử dụng phương pháp resize và crop chuẩn 9:16
            clip = clip.resize(height=1280)
            if clip.w > 720:
                clip = clip.crop(x_center=clip.w/2, width=720)
            else:
                clip = clip.resize(width=720) # Trường hợp ảnh quá hẹp
                
            clip = clip.set_fps(30).set_position("center")
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

    # Ghép clip và ÉP SIZE lần cuối cho video tạm
    final_video = concatenate_videoclips(clips, method="compose")
    temp_bg_name = f"temp_bg_{random.randint(100,999)}.mp4"
    
    # Chỉ định size=(720, 1280) ngay khi xuất file từ MoviePy
    final_video.write_videofile(temp_bg_name, fps=30, codec="libx264", 
                                audio=False, logger=None, size=(720, 1280))
    return temp_bg_name

def render_video(audio_path, subtitles, output, topic=None, market_data=None, script=None):
    print(f"🎬 Bắt đầu Render hệ thống (9:16): {output}...")
    temp_bg_file = None

    # --- 1. LẤY THỜI LƯỢNG AUDIO ---
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    audio.close()

    # --- 2. TẠO OVERLAY TĨNH ---
    overlay_path = f"temp_overlay_{random.randint(100,999)}.png"
    has_overlay = False
    if market_data:
        try:
            img_array = draw_overlay(market_data)
            if img_array is not None:
                # Ép kích thước overlay đúng 720x1280
                ovl_img = Image.fromarray(img_array).resize((720, 1280))
                ovl_img.save(overlay_path)
                has_overlay = True
        except Exception as e:
            print(f"⚠️ Lỗi vẽ overlay: {e}")

    # --- 3. CHUẨN HÓA ĐƯỜNG DẪN SUBTITLE ---
    safe_sub_path = subtitles.replace("\\", "/").replace(":", "\\:") if subtitles else None

    # --- 4. CẤU HÌNH INPUTS ---
    cmd = ["ffmpeg", "-y"]

    picture_folder = "assets/picture"
    if os.path.exists(picture_folder):
        temp_bg_file = create_random_slideshow(picture_folder, duration)

    if temp_bg_file:
        cmd += ["-i", temp_bg_file]
    elif os.path.exists("background.mp4"):
        cmd += ["-stream_loop", "-1", "-i", "background.mp4"]
    else:
        cmd += ["-f", "lavfi", "-i", f"color=c=black:s=720x1280:r=30:d={duration}"]

    if has_overlay:
        cmd += ["-loop", "1", "-t", str(duration), "-i", overlay_path]

    cmd += ["-i", audio_path]
    audio_idx = 2 if has_overlay else 1

    # --- 5. FILTER COMPLEX (RÀ SOÁT KỸ PHẦN NÀY) ---
    filter_parts = []
    
    # Đảm bảo đầu vào background luôn là 720x1280, setsar=1 để pixel là hình vuông
    filter_parts.append("[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1[bg]")
    last_v = "[bg]"

    if has_overlay:
        # Overlay phải được scale đúng trước khi đè
        filter_parts.append(f"[1:v]scale=720:1280[ovl];{last_v}[ovl]overlay=0:0:shortest=1[v_over]")
        last_v = "[v_over]"

    if safe_sub_path:
        # Thêm scale=720:1280 một lần nữa sau khi áp subtitle để "chốt" kích thước
        filter_parts.append(f"{last_v}ass='{safe_sub_path}',scale=720:1280[final_v]")
    else:
        filter_parts.append(f"{last_v}scale=720:1280[final_v]")

    cmd += ["-filter_complex", ";".join(filter_parts)]

    # --- 6. XUẤT FILE (OUTPUT SETTINGS) ---
    cmd += [
        "-map", "[final_v]",
        "-map", f"{audio_idx}:a",
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "21",
        "-aspect", "9:16",     # Ép Metadata
        "-pix_fmt", "yuv420p", # Quan trọng để hiển thị trên điện thoại
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        output
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Render hoàn tất chuẩn 9:16: {output}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi FFmpeg: {e.stderr}")
    finally:
        for f in [overlay_path, temp_bg_file]:
            if f and os.path.exists(f):
                os.remove(f)

    return output
