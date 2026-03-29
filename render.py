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
    """Tạo video nền từ ảnh PNG ngẫu nhiên, tự động LOOP nếu thiếu ảnh"""
    print(f"🖼️ Đang tạo slideshow từ: {folder_path}")
    search_path = os.path.join(folder_path, "*.png")
    all_images = glob.glob(search_path)
    
    if not all_images:
        print(f"⚠️ Không tìm thấy ảnh PNG trong {folder_path}!")
        return None

    # Xáo trộn danh sách ảnh gốc
    random.shuffle(all_images)
    
    clips = []
    current_total_dur = 0
    img_display_dur = 4 
    transition_dur = 1  
    
    # --- LOGIC LOOP ẢNH ---
    # Nếu chạy hết danh sách ảnh mà chưa đủ thời gian, nó sẽ lặp lại từ đầu
    i = 0
    while current_total_dur < target_duration:
        img_p = all_images[i % len(all_images)] # Dùng phép chia lấy dư để quay vòng (Loop)
        try:
            clip = ImageClip(img_p).set_duration(img_display_dur).set_fps(30)
            
            # Resize và Crop chuẩn 9:16 ngay tại đây
            clip = clip.resize(height=1280)
            w, h = clip.size
            if w > 720:
                clip = clip.crop(x_center=w/2, width=720)
            elif w < 720:
                clip = clip.resize(width=720)
                
            clip = clip.set_position("center").crossfadein(transition_dur).crossfadeout(transition_dur)
            clips.append(clip)
            
            # Tính toán thời lượng thực tế (trừ đi phần chồng lấp chuyển cảnh)
            current_total_dur += (img_display_dur - transition_dur)
            i += 1
            
            # Tránh vòng lặp vô tận nếu có lỗi cực nặng (Fail-safe)
            if i > 100: break 
            
        except Exception as e:
            print(f"❌ Lỗi xử lý ảnh {img_p}: {e}")
            i += 1
            continue

    if not clips:
        return None

    final_video = concatenate_videoclips(clips, method="compose")
    temp_bg_name = f"temp_bg_{random.randint(100,999)}.mp4"
    
    # Xuất file nền tạm với kích thước chuẩn
    final_video.write_videofile(
        temp_bg_name, 
        fps=30, 
        codec="libx264", 
        audio=False, 
        logger=None,
        preset="ultrafast"
    )
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

    # --- 5. FILTER COMPLEX (ÉP DAR 9:16 CHO TELEGRAM) ---
    filter_parts = []
    
    # Thêm setdar=9/16 để ép tỉ lệ hiển thị vào Header video
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

    # --- 6. XUẤT FILE (TỐI ƯU MOBILE) ---
    cmd += [
        "-map", "[final_v]",
        "-map", f"{audio_idx}:a",
        "-t", str(duration),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "21",
        "-aspect", "9:16",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        output
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Render hoàn tất chuẩn 9:16 cho Telegram: {output}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi FFmpeg: {e.stderr}")
    finally:
        if has_overlay and os.path.exists(overlay_path):
            os.remove(overlay_path)
        if temp_bg_file and os.path.exists(temp_bg_file):
            os.remove(temp_bg_file)

    return output
