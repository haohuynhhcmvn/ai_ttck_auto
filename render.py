# ==============================
# RENDER ENGINE PRO (MUSIC & GHA OPTIMIZED)
# BẢN TÍCH HỢP HOOK 3S ĐẦU + FIX UNICODE
# ==============================

import subprocess
import os
import random
import glob
import uuid
import textwrap
import urllib.request
import unicodedata
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

# Dummy overlay nếu không tìm thấy module draw_overlay
try:
    from overlay import draw_overlay
except ImportError:
    def draw_overlay(data): return None

# --- [MỚI]: HÀM VẼ ẢNH HOOK ĐỂ GIỮ CHÂN NGƯỜI XEM ---
def create_hook_image(hook_text, output_path):
    """Tạo ảnh nền đỏ chữ trắng. Tự động tải Font nếu thiếu để chống sập Pillow."""
    width, height = 720, 1280
    img = Image.new("RGB", (width, height), (180, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 1. Tạo thư mục chứa font nếu chưa có
    font_dir = "assets/fonts"
    os.makedirs(font_dir, exist_ok=True)
    
    main_font_path = os.path.join(font_dir, "Roboto-Black.ttf")
    sub_font_path = os.path.join(font_dir, "Roboto-Medium.ttf")
    
    # 2. Tự động tải Font chuẩn từ kho Google Fonts nếu GHA bị thiếu file
    if not os.path.exists(main_font_path):
        print("📥 [Pillow]: Không tìm thấy Font, đang tải Roboto-Black...")
        urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Black.ttf", main_font_path)
        
    if not os.path.exists(sub_font_path):
        print("📥 [Pillow]: Không tìm thấy Font, đang tải Roboto-Medium...")
        urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Medium.ttf", sub_font_path)

    # 3. Load font và chuẩn hóa text
    try:
        font = ImageFont.truetype(main_font_path, 80)
        sub_font = ImageFont.truetype(sub_font_path, 40)
        # Chuẩn hóa Unicode NFC để nét chữ hiển thị mượt nhất
        text_to_draw = unicodedata.normalize('NFC', str(hook_text))
    except Exception as e:
        print(f"⚠️ [CẢNH BÁO]: Tải font thất bại. Kích hoạt chế độ sinh tồn: {e}")
        font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        
        # [QUAN TRỌNG]: Dùng font mặc định thì BẮT BUỘC PHẢI BỎ DẤU tiếng Việt để không bị lỗi latin-1
        raw_text = unicodedata.normalize('NFKD', str(hook_text))
        text_to_draw = "".join([c for c in raw_text if not unicodedata.combining(c)])
        text_to_draw = text_to_draw.replace('Đ', 'D').replace('đ', 'd') # Xử lý riêng chữ Đ

    # 4. Vẽ chữ (Tự động xuống dòng)
    lines = textwrap.wrap(text_to_draw, width=15)
    current_h = 500
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((width - w) / 2, current_h), line, font=font, fill=(255, 255, 255))
        current_h += h + 30

    # 5. Vẽ CTA
    cta_text = "CHI TIET TRONG VIDEO" if font == ImageFont.load_default() else "CHI TIẾT TRONG VIDEO 👇"
    bbox_cta = draw.textbbox((0, 0), cta_text, font=sub_font)
    sw = bbox_cta[2] - bbox_cta[0]
    draw.text(((width - sw) / 2, 1050), cta_text, font=sub_font, fill=(255, 255, 0))

    img.save(output_path)
    return output_path
# --- HÀM LẤY NHẠC (GIỮ NGUYÊN) ---
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

# --- HÀM TẠO SLIDESHOW (GIỮ NGUYÊN, ĐÃ TỐI ƯU GHA) ---
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
    img_display_dur = 4    
    transition_dur = 1     
    
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

# --- HÀM RENDER CHÍNH (ĐÃ FIX LỖI LATIN-1 VÀ CHÈN LAYER HOOK) ---
def render_video(audio_path, subtitles, output, topic=None, market_data=None, script=None, video_hook=None):
    """
    Hàm Render chính - Tích hợp Nhạc nền Random, Overlay và Hook ảnh tĩnh.
    """
    # Chuẩn hóa hook chống lỗi latin-1 ngay lập tức
    safe_hook = unicodedata.normalize('NFC', str(video_hook or "TIN CHỨNG KHOÁN MỚI NHẤT"))
    print(f"🎬 [RENDER]: Pipeline 9:16 đang chạy với Hook: '{safe_hook}'")
    
    temp_bg_file = None
    u_id = uuid.uuid4().hex[:5]
    overlay_path = f"ovl_{u_id}.png"
    hook_img_path = f"hook_{u_id}.png"
    
    has_overlay = False
    has_hook = False

    # 1. Lấy thông tin Audio MC
    voice_clip = AudioFileClip(audio_path)
    duration = voice_clip.duration
    voice_clip.close()

    # 2. Tạo ảnh Hook 
    if video_hook:
        create_hook_image(safe_hook, hook_img_path)
        has_hook = True

    # 3. Chọn nhạc nền ngẫu nhiên
    bg_music_file = get_random_bg_music("assets/music")

    # 4. Tạo Overlay (Biểu đồ/Tin tức)
    if market_data:
        try:
            img_array = draw_overlay(market_data)
            if img_array is not None:
                ovl_img = Image.fromarray(img_array).resize((720, 1280))
                ovl_img.save(overlay_path)
                has_overlay = True
        except: print("⚠️ [SKIP]: Overlay không khả dụng")

    # 5. Chuẩn hóa đường dẫn Subtitle cho FFmpeg
    safe_sub_path = subtitles.replace("\\", "/").replace(":", "\\:") if subtitles else None

    # 6. Tạo Slideshow Background
    picture_folder = "assets/picture"
    if os.path.exists(picture_folder):
        temp_bg_file = create_random_slideshow(picture_folder, duration)

    # --- KHỞI TẠO LỆNH FFMPEG (CHUYỂN SANG LIST CHUẨN) ---
    cmd = ["ffmpeg", "-y"]
    
    # [Input 0]: Video Background
    if temp_bg_file:
        cmd += ["-i", temp_bg_file]
    else:
        cmd += ["-f", "lavfi", "-i", f"color=c=black:s=720x1280:r=24:d={duration}"]

    # [Input 1]: Ảnh Hook (Tĩnh, đè lên đầu)
    if has_hook:
        cmd += ["-loop", "1", "-t", "2.5", "-i", hook_img_path]
    else:
        cmd += ["-f", "lavfi", "-i", "color=c=black:s=2x2:d=0.1"] # Dummy input cho đủ index

    # [Input 2]: Overlay (PNG bảng điện)
    if has_overlay:
        cmd += ["-loop", "1", "-t", str(duration), "-i", overlay_path]
    else:
        cmd += ["-f", "lavfi", "-i", "color=c=black:s=2x2:d=0.1"]

    # [Input 3]: Giọng đọc (MC Voice)
    cmd += ["-i", audio_path]

    # [Input 4]: Nhạc nền (Tự động Loop)
    if bg_music_file:
        cmd += ["-stream_loop", "-1", "-i", bg_music_file]

    # --- FILTER COMPLEX ---
    filters = []
    
    # A. Xử lý nền
    filters.append("[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,eq=saturation=1.2:contrast=1.1[bg]")
    last_v = "[bg]"

    # B. Xử lý Overlay Bảng điện (Đè lên nền)
    if has_overlay:
        filters.append(f"[2:v]scale=720:1280[ovl];{last_v}[ovl]overlay=0:0:shortest=1[v_over]")
        last_v = "[v_over]"

    # C. Xử lý Hook (Đè lên tất cả, nhưng chỉ hiện 2.5s đầu)
    if has_hook:
        filters.append(f"[1:v]scale=720:1280[hook_v];{last_v}[hook_v]overlay=0:0:enable='between(t,0,2.5)'[v_hooked]")
        last_v = "[v_hooked]"

    # D. Xử lý Subtitle
    if safe_sub_path:
        filters.append(f"{last_v}ass='{safe_sub_path}'[final_v]")
    else:
        filters.append(f"{last_v}copy[final_v]")

    # E. Xử lý âm thanh (Mixing)
    if bg_music_file:
        # [3:a] là MC, [4:a] là nhạc nền
        filters.append(f"[4:a]volume=0.08,atrim=0:{duration},afade=t=out:st={duration-2}:d=2[bg_a]")
        filters.append(f"[3:a][bg_a]amix=inputs=2:duration=first:dropout_transition=2[final_a]")
    else:
        filters.append("[3:a]copy[final_a]")

    cmd += ["-filter_complex", ";".join(filters)]

    # --- OUTPUT SETTINGS ---
    cmd += [
        "-map", "[final_v]",
        "-map", "[final_a]",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "28",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output
    ]

    # [FIX CỐT LÕI]: CHẠY FFMPEG VỚI ĐỊNH DẠNG CHUỖI ĐỂ TRÁNH LỖI LATIN-1
    # Bằng cách chuyển mảng thành một chuỗi duy nhất và dùng shell=True, 
    # ta bỏ qua cơ chế mã hóa tham số lằng nhằng của Python trên môi trường Server
    full_command = " ".join([f'"{c}"' if ' ' in c or 'ass=' in c else c for c in cmd])

    try:
        process = subprocess.run(
            full_command, 
            shell=True,
            capture_output=True, 
            text=True,
            encoding="utf-8", 
            errors="ignore"
        )
        if process.returncode == 0:
            print(f"✅ [SUCCESS]: Video hoàn tất với nhạc nền và Hook -> {output}")
        else:
            print(f"❌ [FFMPEG ERROR]: {process.stderr}")
    except Exception as e:
        print(f"❌ Render sập: {e}")
    finally:
        # Dọn rác
        if has_overlay and os.path.exists(overlay_path): os.remove(overlay_path)
        if has_hook and os.path.exists(hook_img_path): os.remove(hook_img_path)
        if temp_bg_file and os.path.exists(temp_bg_file): os.remove(temp_bg_file)

    return output
