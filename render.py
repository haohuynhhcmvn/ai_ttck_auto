# ==============================
# RENDER ENGINE PRO (MUSIC & GHA OPTIMIZED)
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

def get_random_bg_music(music_dir="assets/music"):
    """Quét thư mục và chọn ngẫu nhiên 1 file nhạc mp3/wav"""
    if not os.path.exists(music_dir):
        return None
    valid_extensions = ('*.mp3', '*.wav', '*.m4a')
    music_files = []
    for ext in valid_extensions:
        music_files.extend(glob.glob(os.path.join(music_dir, ext)))
    
    if not music_files:
        return None
    return random.choice(music_files)

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
            with Image.open(img_p) as img:
                img = img.convert("RGB")
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
                
                temp_img_path = f"temp_img_{uuid.uuid4().hex[:5]}.jpg"
                img.save(temp_img_path, quality=85)

            clip = ImageClip(temp_img_path).set_duration(img_display_dur).set_fps(24)
            clip = clip.set_position("center").crossfadein(transition_dur)
            clips.append(clip)
            
            current_total_dur += (img_display_dur - transition_dur)
            i += 1
            if i > 50: break 
            
        except Exception as e:
            print(f"❌ Lỗi ảnh: {e}")
            i += 1
            continue

    if not clips: return None

    final_video = concatenate_videoclips(clips, method="compose", padding=-transition_dur)
    final_video = final_video.subclip(0, target_duration)
    
    temp_bg_name = f"bg_{uuid.uuid4().hex[:5]}.mp4"
    
    final_video.write_videofile(
        temp_bg_name, 
        fps=24, 
        codec="libx264", 
        audio=False, 
        logger=None,
        preset="ultrafast",
        threads=2 
    )
    
    for f in glob.glob("temp_img_*.jpg"): 
        try: os.remove(f)
        except: pass
    
    return temp_bg_name

def render_video(audio_path, subtitles, output, topic=None, market_data=None, script=None):
    """
    Hàm Render chính - Tích hợp Nhạc nền Random và Audio Mixing chuyên nghiệp.
    """
    print(f"🎬 [RENDER]: Pipeline 9:16 đang chạy...")
    temp_bg_file = None
    overlay_path = f"ovl_{uuid.uuid4().hex[:5]}.png"
    has_overlay = False

    # 1. Lấy thông tin Audio MC (Giọng đọc)
    voice_clip = AudioFileClip(audio_path)
    duration = voice_clip.duration
    voice_clip.close()

    # 2. Chọn nhạc nền ngẫu nhiên
    bg_music_file = get_random_bg_music("assets/music")

    # 3. Tạo Overlay (Biểu đồ/Tin tức)
    if market_data:
        try:
            img_array = draw_overlay(market_data)
            if img_array is not None:
                ovl_img = Image.fromarray(img_array).resize((720, 1280))
                ovl_img.save(overlay_path)
                has_overlay = True
        except: print("⚠️ [SKIP]: Overlay không khả dụng")

    # 4. Chuẩn hóa đường dẫn Subtitle
    safe_sub_path = subtitles.replace("\\", "/").replace(":", "\\:") if subtitles else None

    # 5. Tạo Slideshow Background
    picture_folder = "assets/picture"
    if os.path.exists(picture_folder):
        temp_bg_file = create_random_slideshow(picture_folder, duration)

    # --- KHỞI TẠO LỆNH FFMPEG ---
    cmd = ["ffmpeg", "-y"]
    
    # Input 0: Video Background
    if temp_bg_file:
        cmd += ["-i", temp_bg_file]
    else:
        cmd += ["-f", "lavfi", "-i", f"color=c=black:s=720x1280:r=24:d={duration}"]

    # Input 1: Overlay (PNG)
    if has_overlay:
        cmd += ["-loop", "1", "-t", str(duration), "-i", overlay_path]

    # Input 2: Giọng đọc (MC Voice)
    cmd += ["-i", audio_path]

    # Input 3: Nhạc nền (Background Music) - Tự động Loop
    if bg_music_file:
        cmd += ["-stream_loop", "-1", "-i", bg_music_file]

    # --- FILTER COMPLEX ---
    filters = []
    # Xử lý hình ảnh
    filters.append("[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,eq=saturation=1.2:contrast=1.1[bg]")
    last_v = "[bg]"

    if has_overlay:
        filters.append(f"[1:v]scale=720:1280[ovl];{last_v}[ovl]overlay=0:0:shortest=1[v_over]")
        last_v = "[v_over]"

    if safe_sub_path:
        filters.append(f"{last_v}ass='{safe_sub_path}'[final_v]")
    else:
        filters.append(f"{last_v}copy[final_v]")

    # Xử lý âm thanh (Mixing)
    # [2:a] là giọng MC, [3:a] là nhạc nền
    if bg_music_file:
        # Giảm âm lượng nhạc nền xuống 0.08 (8%) và trộn với giọng MC
        filters.append(f"[3:a]volume=0.08,atrim=0:{duration},afade=t=out:st={duration-2}:d=2[bg_a]")
        filters.append(f"[2:a][bg_a]amix=inputs=2:duration=first:dropout_transition=2[final_a]")
    else:
        filters.append("[2:a]copy[final_a]")

    cmd += ["-filter_complex", ";".join(filters)]

    # --- OUTPUT SETTINGS ---
    cmd += [
        "-map", "[final_v]",
        "-map", "[final_a]",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ [SUCCESS]: Video hoàn tất với nhạc nền -> {output}")
        else:
            print(f"❌ [FFMPEG ERROR]: {result.stderr}")
    finally:
        if has_overlay and os.path.exists(overlay_path): os.remove(overlay_path)
        if temp_bg_file and os.path.exists(temp_bg_file): os.remove(temp_bg_file)

    return output
