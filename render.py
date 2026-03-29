import subprocess
import os
import random
import glob
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips, vfx
import moviepy.video.fx.all as vfx_all # Import tất cả fx để dùng resize, crop
from PIL import Image

try:
    from overlay import draw_overlay
except ImportError:
    def draw_overlay(data): return None

# ==============================
# HÀM KEN BURNS EFFECT (ZOOM & PAN)
# ==============================
def apply_ken_burns(clip, duration, zoom_ratio=0.1):
    """
    Áp dụng hiệu ứng Ken Burns (Zoom nhẹ) vào clip ảnh.
    zoom_ratio=0.1 nghĩa là ảnh sẽ phóng đại thêm 10% trong suốt thời gian hiển thị.
    """
    w, h = clip.size
    
    # Hàm tính toán kích thước resize theo thời gian t (phóng đại dần)
    # t chạy từ 0 đến duration của clip
    def my_resize(t):
        return 1 + zoom_ratio * (t / duration)

    # Áp dụng resize theo thời gian, giữ nguyên SAR
    # Dùng resizer='bilinear' để chất lượng ảnh mượt hơn khi zoom
    clip_zoomed = clip.resize(my_resize, resizer='bilinear')
    
    # Cắt (Crop) lại đúng khung 720x1280 từ tâm ảnh sau khi zoom
    clip_final = clip_zoomed.crop(x_center=w/2, y_center=h/2, width=720, height=1280)
    
    return clip_final.set_duration(duration)

# ==============================
# TẠO SLIDESHOW MƯỢT MÀ PRO
# ==============================
def create_random_slideshow(folder_path, target_duration):
    """
    Tạo video nền từ ảnh PNG ngẫu nhiên, áp dụng Ken Burns và Crossfade dài.
    Tự động LOOP nếu thiếu ảnh.
    """
    print(f"🖼️ Đang tạo slideshow SIÊU MƯỢT từ: {folder_path}")
    search_path = os.path.join(folder_path, "*.png")
    all_images = glob.glob(search_path)
    
    if not all_images:
        print(f"⚠️ Không tìm thấy ảnh PNG trong {folder_path}!")
        return None

    # Xáo trộn danh sách ảnh gốc
    random.shuffle(all_images)
    
    clips = []
    current_total_dur = 0
    # --- THÔNG SỐ ĐỂ CHUYỂN CẢNH MƯỢT ---
    img_display_dur = 6  # Tăng thời gian hiển thị mỗi ảnh lên 6 giây để kịp zoom
    transition_dur = 2   # Tăng thời gian mờ dần lên 2 giây (siêu mượt)
    
    # --- LOGIC LOOP ẢNH ---
    i = 0
    while current_total_dur < target_duration:
        img_p = all_images[i % len(all_images)] # Loop quay vòng
        try:
            # Bước A: Load ảnh gốc
            raw_clip = ImageClip(img_p).set_fps(30)
            
            # Bước B: Resize sơ bộ để ép chiều cao về 1280, chuẩn bị cho Ken Burns
            # (Ta nắn Sar ở đây để Ken Burns không bị méo)
            w, h = raw_clip.size
            if h != 1280:
                raw_clip = raw_clip.resize(height=1280)
            
            # Bước C: Áp dụng Ken Burns (Zoom & Pan)
            # Dùng fail-safe nếu ảnh lỡ bị lỗi size sau khi resize
            if raw_clip.w < 720: raw_clip = raw_clip.resize(width=720)
                
            kb_clip = apply_ken_burns(raw_clip, img_display_dur, zoom_ratio=0.15)
            
            # Bước D: Thêm hiệu ứng chuyển cảnh mờ dần (Crossfade) dài
            kb_clip = kb_clip.set_position("center").crossfadein(transition_dur).crossfadeout(transition_dur)
            
            clips.append(kb_clip)
            
            # Tính toán thời lượng thực tế (trừ đi phần chồng lấp chuyển cảnh)
            current_total_dur += (img_display_dur - transition_dur)
            i += 1
            
            # Tránh vòng lặp vô tận (Fail-safe)
            if i > 150: break 
            
        except Exception as e:
            print(f"❌ Lỗi xử lý ảnh {img_p}: {e}")
            i += 1
            continue

    if not clips:
        return None

    # Ghép các clip (method="compose" để giữ hiệu ứng crossfade)
    # Dùng padding để tránh lỗi tiếng nhanh hơn hình ở cuối video
    final_video = concatenate_videoclips(clips, method="compose", padding=-transition_dur)
    
    # Cắt đúng thời lượng audio để không bị dư
    final_video = final_video.subclip(0, target_duration)
    
    temp_bg_name = f"temp_bg_{random.randint(100,999)}.mp4"
    
    # Xuất file nền tạm với kích thước chuẩn và chất lượng cao
    # Dùng bit rate cao hơn một chút vì có chuyển động zoom
    final_video.write_videofile(
        temp_bg_name, 
        fps=30, 
        codec="libx264", 
        audio=False, 
        logger=None,
        preset="ultrafast",
        ffmpeg_params=["-crf", "18"] # Tăng chất lượng file tạm
    )
    return temp_bg_name

# ==============================
# HÀM RENDER CHÍNH (GIỮ NGUYÊN PHẦN TRƯỚC)
# ==============================
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
                # Ép kích thước overlay PNG đúng 720x1280
                ovl_img = Image.fromarray(img_array).resize((720, 1280), Image.Resampling.LANCZOS)
                ovl_img.save(overlay_path)
                has_overlay = True
        except Exception as e:
            print(f"⚠️ Lỗi vẽ overlay: {e}")

    # --- 3. CHUẨN HÓA ĐƯỜNG DẪN SUBTITLE ---
    # Cần thiết để FFmpeg trên Windows không bị lỗi đọc đường dẫn
    safe_sub_path = subtitles.replace("\\", "/").replace(":", "\\:") if subtitles else None

    # --- 4. CẤU HÌNH INPUTS ---
    cmd = ["ffmpeg", "-y"]
    picture_folder = "assets/picture" 
    
    # Ưu tiên tạo Slideshow siêu mượt
    if os.path.exists(picture_folder):
        temp_bg_file = create_random_slideshow(picture_folder, duration)

    if temp_bg_file:
        cmd += ["-i", temp_bg_file]
    elif os.path.exists("background.mp4"):
        # Cờ loop -1 để lặp video nền vô hạn
        cmd += ["-stream_loop", "-1", "-i", "background.mp4"]
    else:
        # Tạo nền đen chuẩn 9:16 nếu thiếu mọi thứ
        cmd += ["-f", "lavfi", "-i", f"color=c=black:s=720x1280:r=30:d={duration}"]

    # Input 1 (Nếu có): Overlay PNG (danh sách mã chứng khoán)
    if has_overlay:
        cmd += ["-loop", "1", "-t", str(duration), "-i", overlay_path]

    # Input Audio
    cmd += ["-i", audio_path]
    
    # Chỉ số để map audio chuẩn
    audio_idx = 2 if has_overlay else 1

    # --- 5. FILTER COMPLEX (ÉP DAR 9:16 VÀ CHỒNG LỚP) ---
    filter_parts = []
    
    # Ép background về chuẩn 9:16, setsar=1, setdar=9/16 để không méo
    filter_parts.append("[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,setsar=1,setdar=9/16[bg]")
    last_v = "[bg]"

    # Đè lớp Overlay PNG
    if has_overlay:
        # Scale lớp overlay đúng kích thước và đè
        filter_parts.append(f"[1:v]scale=720:1280,setsar=1,setdar=9/16[ovl];{last_v}[ovl]overlay=0:0:shortest=1[v_over]")
        last_v = "[v_over]"

    # Đè lớp Ticker chạy ngang ở tâm màn hình
    if safe_sub_path:
        # Thêm Subtitle .ass và ÉP CỨNG size một lần cuối cùng
        filter_parts.append(f"{last_v}ass='{safe_sub_path}',scale=720:1280,setsar=1,setdar=9/16[final_v]")
    else:
        # Nếu thiếu Ticker thì copy
        filter_parts.append(f"{last_v}scale=720:1280,setsar=1,setdar=9/16[final_v]")

    cmd += ["-filter_complex", ";".join(filter_parts)]

    # --- 6. XUẤT FILE (CÀI ĐẶT CHO MOBILE / TELEGRAM) ---
    cmd += [
        "-map", "[final_v]",           # Lấy luồng video đã trộn xong
        "-map", f"{audio_idx}:a",      # Lấy luồng âm thanh MC đọc
        "-t", str(duration),           # Video dài đúng bằng tiếng người nói
        "-c:v", "libx264",             # Codec nén H.264
        "-preset", "ultrafast",        # Tốc độ render cực nhanh
        "-crf", "21",                  # Chất lượng trung bình khá
        "-aspect", "9:16",             # Ép Metadata Header
        "-pix_fmt", "yuv420p",         # Định dạng màu giúp xem được trên mobile
        "-c:a", "aac", "-b:a", "128k", # Âm thanh chuẩn AAC
        "-movflags", "+faststart",     # Tối ưu upload (streaming)
        output
    ]

    # --- 7. THỰC THI LỆNH FFMPEG ---
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Render hoàn tất chuẩn 9:16 SIÊU MƯỢT: {output}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi Render FFmpeg: {e.stderr}")
    finally:
        # Dọn dẹp các file tạm
        if has_overlay and os.path.exists(overlay_path):
            os.remove(overlay_path)
        if temp_bg_file and os.path.exists(temp_bg_file):
            os.remove(temp_bg_file)

    return output
