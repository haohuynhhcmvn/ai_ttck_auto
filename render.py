# ==============================
# RENDER ENGINE PRO (GITHUB ACTIONS OPTIMIZED)
# ==============================

import subprocess
import os
import random
import glob
import uuid
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
from PIL import Image

# Dummy overlay nếu không tìm thấy module draw_overlay
try:
    from overlay import draw_overlay
except ImportError:
    def draw_overlay(data): return None

def create_random_slideshow(folder_path, target_duration):
    """
    Tạo video nền từ ảnh JPG. 
    Tối ưu cực hạn RAM để chạy mượt trên GitHub Actions 7GB RAM.
    """
    print(f"🖼️ [SLIDESHOW]: Đang xử lý ảnh tại {folder_path}")
    search_path = os.path.join(folder_path, "*.jpg")
    all_images = glob.glob(search_path)
    
    if not all_images:
        return None

    random.shuffle(all_images)
    
    clips = []
    current_total_dur = 0
    img_display_dur = 4    # Giảm xuống 4s để video năng động hơn
    transition_dur = 1     # Giảm transition để tiết kiệm CPU khi render
    
    # Chỉ lấy tối đa 20 ảnh để tránh tràn RAM khi concatenate
    max_imgs = min(len(all_images), 20)
    selected_images = all_images[:max_imgs]

    i = 0
    while current_total_dur < target_duration:
        img_p = selected_images[i % len(selected_images)]
        try:
            # Resize ngay lập tức bằng PIL trước khi đưa vào MoviePy để tiết kiệm RAM
            with Image.open(img_p) as img:
                img = img.convert("RGB")
                # Resize chuẩn 720x1280 (Crop Center)
                w, h = img.size
                aspect_target = 720/1280
                aspect_img = w/h
                
                if aspect_img > aspect_target:
                    new_w = int(aspect_img * 1280)
                    img = img.resize((new_w, 1280), Image.LANCZOS)
                    left = (new_w - 720) / 2
                    img = img.crop((left, 0, left + 720, 1280))
                else:
                    new_h = int(720 / aspect_img)
                    img = img.resize((720, new_h), Image.LANCZOS)
                    top = (new_h - 1280) / 2
                    img = img.crop((0, top, 720, top + 1280))
                
                # Lưu tạm ảnh đã resize để ImageClip load nhẹ hơn
                temp_img_path = f"temp_img_{i}.jpg"
                img.save(temp_img_path, quality=85)

            clip = ImageClip(temp_img_path).set_duration(img_display_dur).set_fps(24)
            clip = clip.set_position("center").crossfadein(transition_dur)
            clips.append(clip)
            
            current_total_dur += (img_display_dur - transition_dur)
            i += 1
            if i > 50: break # Giới hạn số lượng clip gộp
            
        except Exception as e:
            print(f"❌ Lỗi ảnh: {e}")
            i += 1
            continue

    if not clips: return None

    final_video = concatenate_videoclips(clips, method="compose", padding=-transition_dur)
    final_video = final_video.subclip(0, target_duration)
    
    temp_bg_name = f"bg_{uuid.uuid4().hex[:5]}.mp4"
    
    # Xuất file nền cực nhanh (ultrafast) để FFmpeg tổng hợp lại sau
    final_video.write_videofile(
        temp_bg_name, 
        fps=24, 
        codec="libx264", 
        audio=False, 
        logger=None,
        preset="ultrafast",
        threads=2 # Giới hạn thread để ổn định RAM trên GHA
    )
    
    # Dọn dẹp ảnh tạm
    for f in glob.glob("temp_img_*.jpg"): os.remove(f)
    
    return temp_bg_name

def render_video(audio_path, subtitles, output, topic=None, market_data=None, script=None):
    """
    Hàm Render chính - Kết hợp Background, Overlay, Subtitle và Audio.
    Tối ưu Filter Complex để FFmpeg xử lý trong 1 luồng duy nhất.
    """
    print(f"🎬 [RENDER]: Pipeline 9:16 đang chạy...")
    temp_bg_file = None
    overlay_path = f"ovl_{uuid.uuid4().hex[:5]}.png"
    has_overlay = False

    # 1. Lấy thông tin Audio
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    audio_clip.close()

    # 2. Tạo Overlay (Biểu đồ/Tin tức)
    if market_data:
        try:
            img_array = draw_overlay(market_data)
            if img_array is not None:
                ovl_img = Image.fromarray(img_array).resize((720, 1280))
                ovl_img.save(overlay_path)
                has_overlay = True
        except: print("⚠️ [SKIP]: Overlay không khả dụng")

    # 3. Chuẩn hóa đường dẫn Subtitle (Fix lỗi path trên Linux)
    safe_sub_path = subtitles.replace("\\", "/").replace(":", "\\:") if subtitles else None

    # 4. Cấu hình FFmpeg
    picture_folder = "assets/picture"
    if os.path.exists(picture_folder):
        temp_bg_file = create_random_slideshow(picture_folder, duration)

    cmd = ["ffmpeg", "-y"]
    
    # Input 0: Background
    if temp_bg_file:
        cmd += ["-i", temp_bg_file]
    elif os.path.exists("background.mp4"):
        cmd += ["-stream_loop", "-1", "-i", "background.mp4"]
    else:
        cmd += ["-f", "lavfi", "-i", f"color=c=black:s=720x1280:r=24:d={duration}"]

    # Input 1: Overlay (nếu có)
    if has_overlay:
        cmd += ["-loop", "1", "-t", str(duration), "-i", overlay_path]

    # Input cuối: Audio
    cmd += ["-i", audio_path]
    audio_idx = 2 if has_overlay else 1

    # 5. Filter Complex (Tối ưu hóa màu sắc & độ nét)
    filters = []
    # Xử lý Background: Thêm chút bão hòa màu (saturation) cho video TikTok bắt mắt
    filters.append("[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,eq=saturation=1.2:contrast=1.1[bg]")
    last_v = "[bg]"

    if has_overlay:
        filters.append(f"[1:v]scale=720:1280[ovl];{last_v}[ovl]overlay=0:0:shortest=1[v_over]")
        last_v = "[v_over]"

    # Chèn Subtitle (ASS) - Sử dụng 'fix_sub_duration' để tránh nhấp nháy
    if safe_sub_path:
        filters.append(f"{last_v}ass='{safe_sub_path}'[final_v]")
    else:
        filters.append(f"{last_v}copy[final_v]")

    cmd += ["-filter_complex", ";".join(filters)]

    # 6. Xuất bản (Cấu hình Mobile-Friendly)
    cmd += [
        "-map", "[final_v]",
        "-map", f"{audio_idx}:a",
        "-c:v", "libx264",
        "-preset", "slow",     # Chậm hơn nhưng nén cực tốt cho Telegram/TikTok
        "-crf", "22",          # Độ nét cao (CRF 18-24 là dải tốt nhất)
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p", # Bắt buộc để chạy được trên mọi điện thoại
        "-movflags", "+faststart", # Cho phép video phát ngay khi đang tải (Streaming)
        output
    ]

    try:
        # Chạy FFmpeg và bắt lỗi chi tiết
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ [SUCCESS]: Video hoàn tất -> {output}")
        else:
            print(f"❌ [FFMPEG ERROR]: {result.stderr}")
    finally:
        # Dọn dẹp tài nguyên
        if has_overlay and os.path.exists(overlay_path): os.remove(overlay_path)
        if temp_bg_file and os.path.exists(temp_bg_file): os.remove(temp_bg_file)

    return output
