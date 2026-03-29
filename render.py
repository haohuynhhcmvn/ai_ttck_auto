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
    """Tạo video nền từ ảnh JPG, lặp ảnh nếu thiếu, tối ưu dung lượng và độ mượt"""
    print(f"🖼️ Đang tạo slideshow JPG từ: {folder_path}")
    # Đã chuyển sang quét file .jpg
    search_path = os.path.join(folder_path, "*.jpg")
    all_images = glob.glob(search_path)
    
    if not all_images:
        print(f"⚠️ Không tìm thấy ảnh JPG trong {folder_path}!")
        return None

    random.shuffle(all_images)
    
    clips = []
    current_total_dur = 0
    img_display_dur = 5    # Mỗi ảnh hiện 5 giây
    transition_dur = 2     # Chuyển cảnh mờ dần trong 2 giây (rất mượt)
    
    i = 0
    while current_total_dur < target_duration:
        img_p = all_images[i % len(all_images)]
        try:
            # Load ảnh JPG - ép về 24 FPS để giảm tải CPU và dung lượng
            clip = ImageClip(img_p).set_duration(img_display_dur).set_fps(24)
            
            # Resize và Crop chuẩn 9:16 (720x1280)
            clip = clip.resize(height=1280)
            w, h = clip.size
            if w > 720:
                clip = clip.crop(x_center=w/2, width=720)
            elif w < 720:
                clip = clip.resize(width=720)
                
            # Hiệu ứng mờ dần (Crossfade)
            clip = clip.set_position("center").crossfadein(transition_dur).crossfadeout(transition_dur)
            clips.append(clip)
            
            # Tính toán thời lượng thực tế khi có chồng lấn transition
            current_total_dur += (img_display_dur - transition_dur)
            i += 1
            if i > 150: break # Fail-safe
            
        except Exception as e:
            print(f"❌ Lỗi xử lý ảnh {img_p}: {e}")
            i += 1
            continue

    if not clips:
        return None

    # Ghép các clip gối đầu lên nhau (padding âm)
    final_video = concatenate_videoclips(clips, method="compose", padding=-transition_dur)
    final_video = final_video.subclip(0, target_duration)
    
    temp_bg_name = f"temp_bg_{random.randint(100,999)}.mp4"
    
    # Xuất file nền tạm với Bitrate khống chế để không bị phình to dung lượng
    final_video.write_videofile(
        temp_bg_name, 
        fps=24, 
        codec="libx264", 
        audio=False, 
        logger=None,
        preset="ultrafast", # Bước tạm dùng nhanh, bước cuối mới nén kỹ
        bitrate="2500k"
    )
    return temp_bg_name

def render_video(audio_path, subtitles, output, topic=None, market_data=None, script=None):
    print(f"🎬 Bắt đầu Render hệ thống (9:16): {output}...")
    temp_bg_file = None

    # 1. Thời lượng Audio
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    audio.close()

    # 2. Tạo Overlay tĩnh
    overlay_path = f"temp_overlay_{random.randint(100,999)}.png"
    has_overlay = False
    if market_data:
        try:
            img_array = draw_overlay(market_data)
            if img_array is not None:
                ovl_img = Image.fromarray(img_array).resize((720, 1280))
                ovl_img.save(overlay_path)
                has_overlay = True
        except Exception as e:
            print(f"⚠️ Lỗi vẽ overlay: {e}")

    # 3. Chuẩn hóa subtitle
    safe_sub_path = subtitles.replace("\\", "/").replace(":", "\\:") if subtitles else None

    # 4. FFmpeg Command
    cmd = ["ffmpeg", "-y"]
    picture_folder = "assets/picture" 
    
    if os.path.exists(picture_folder):
        temp_bg_file = create_random_slideshow(picture_folder, duration)

    if temp_bg_file:
        cmd += ["-i", temp_bg_file]
    elif os.path.exists("background.mp4"):
        cmd += ["-stream_loop", "-1", "-i", "background.mp4"]
    else:
        cmd += ["-f", "lavfi", "-i", f"color=c=black:s=720x1280:r=24:d={duration}"]

    if has_overlay:
        cmd += ["-loop", "1", "-t", str(duration), "-i", overlay_path]

    cmd += ["-i", audio_path]
    audio_idx = 2 if has_overlay else 1

    # 5. Filter Complex (Nắn 9:16 cho Telegram)
    filter_parts = []
    filter_parts.append("[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,setdar=9/16[bg]")
    last_v = "[bg]"

    if has_overlay:
        filter_parts.append(f"[1:v]scale=720:1280,setsar=1,setdar=9/16[ovl];{last_v}[ovl]overlay=0:0:shortest=1[v_over]")
        last_v = "[v_over]"

    if safe_sub_path:
        filter_parts.append(f"{last_v}ass='{safe_sub_path}',scale=720:1280,setsar=1,setdar=9/16[final_v]")
    else:
        filter_parts.append(f"{last_v}scale=720:1280,setsar=1,setdar=9/16[final_v]")

    cmd += ["-filter_complex", ";".join(filter_parts)]

    # 6. Xuất Output (Tối ưu nén dung lượng cực tốt)
    cmd += [
        "-map", "[final_v]",
        "-map", f"{audio_idx}:a",
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "medium",    # Nén kỹ hơn, file nhỏ hơn nhiều so với 'ultrafast'
        "-crf", "24",           # CRF 24: Dung lượng thấp nhưng độ nét vẫn rất tốt cho Mobile
        "-maxrate", "2000k",    # Giới hạn băng thông tối đa để file không nặng
        "-bufsize", "4000k",
        "-aspect", "9:16",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "96k", # Giảm nhẹ bitrate audio giúp tiết kiệm dung lượng
        "-movflags", "+faststart",
        output
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Thành công! Video 9:16 nhẹ & mượt: {output}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi FFmpeg: {e.stderr}")
    finally:
        # Dọn dẹp file tạm
        if has_overlay and os.path.exists(overlay_path):
            os.remove(overlay_path)
        if temp_bg_file and os.path.exists(temp_bg_file):
            os.remove(temp_bg_file)

    return output
