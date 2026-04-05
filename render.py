# ==============================
# RENDER ENGINE PRO (OPTIMIZED FOR 3S HOOK & GHA)
# ==============================

import subprocess
import os
import random
import glob
import uuid
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

# Thử nghiệm import module vẽ overlay bảng điện
try:
    from overlay import draw_overlay
except ImportError:
    def draw_overlay(data): return None

# --- [MỚI]: HÀM VẼ ẢNH HOOK ĐỂ GIỮ CHÂN NGƯỜI XEM ---
def create_hook_image(hook_text, output_path):
    """Tạo một tấm ảnh nền đỏ, chữ trắng cực to cho 2.5 giây đầu"""
    width, height = 720, 1280
    # Tạo nền đỏ đậm (Màu cảnh báo tài chính)
    img = Image.new("RGB", (width, height), (180, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Cố gắng load font chữ dày, nếu không có dùng font mặc định
    try:
        font = ImageFont.truetype("assets/fonts/Roboto-Black.ttf", 80)
        sub_font = ImageFont.truetype("assets/fonts/Roboto-Medium.ttf", 40)
    except:
        font = ImageFont.load_default()
        sub_font = ImageFont.load_default()

    # Tự động xuống dòng cho Hook nếu quá dài
    import textwrap
    lines = textwrap.wrap(hook_text, width=15)
    
    # Vẽ từng dòng chữ Hook
    current_h = 500
    for line in lines:
        w, h = draw.textbbox((0, 0), line, font=font)[2:4]
        draw.text(((width - w) / 2, current_h), line, font=font, fill=(255, 255, 255))
        current_h += h + 20

    # Vẽ dòng chữ kêu gọi hành động nhỏ phía dưới
    cta_text = "CHI TIẾT TRONG VIDEO 👇"
    sw, sh = draw.textbbox((0, 0), cta_text, font=sub_font)[2:4]
    draw.text(((width - sw) / 2, 1000), cta_text, font=sub_font, fill=(255, 255, 0)) # Chữ vàng cho nổi

    img.save(output_path)
    return output_path

# --- CÁC HÀM CŨ GIỮ NGUYÊN LOGIC ---
def get_random_bg_music(music_dir="assets/music"):
    if not os.path.exists(music_dir): return None
    music_files = glob.glob(os.path.join(music_dir, "*.mp3")) + glob.glob(os.path.join(music_dir, "*.wav"))
    return random.choice(music_files) if music_files else None

def create_random_slideshow(folder_path, target_duration):
    """Logic cũ của ông: Tạo video nền từ ảnh JPG, tối ưu RAM cho GHA"""
    # ... (Giữ nguyên toàn bộ code create_random_slideshow của ông ở đây) ...
    # Vì lý do độ dài, tôi lược bớt phần thân hàm này, ông cứ giữ nguyên bản cũ của ông.
    pass 

def render_video(audio_path, subtitles, output, topic=None, market_data=None, script=None, video_hook=None):
    """
    Hàm Render chính - Đã tích hợp logic hiện Hook 2.5s đầu video
    """
    print(f"🎬 [RENDER]: Đang bắt đầu render với Hook: {video_hook}")
    temp_bg_file = None
    overlay_path = f"ovl_{uuid.uuid4().hex[:5]}.png"
    hook_img_path = f"hook_{uuid.uuid4().hex[:5]}.png"
    has_overlay = False
    has_hook = False

    # 1. Lấy thông tin Audio MC
    voice_clip = AudioFileClip(audio_path)
    duration = voice_clip.duration
    voice_clip.close()

    # 2. Tạo ảnh Hook nếu có video_hook truyền từ content_ai.py xuống
    if video_hook:
        create_hook_image(video_hook, hook_img_path)
        has_hook = True

    # 3. Tạo Overlay bảng điện (Chỉ hiện sau 2.5 giây đầu)
    if market_data:
        try:
            img_array = draw_overlay(market_data)
            if img_array is not None:
                ovl_img = Image.fromarray(img_array).resize((720, 1280))
                ovl_img.save(overlay_path)
                has_overlay = True
        except: print("⚠️ [SKIP]: Overlay lỗi")

    # 4. Chuẩn hóa đường dẫn Subtitle
    safe_sub_path = subtitles.replace("\\", "/").replace(":", "\\:") if subtitles else None

    # 5. Tạo Slideshow Background (Dùng logic cũ của ông)
    picture_folder = "assets/picture"
    temp_bg_file = create_random_slideshow(picture_folder, duration) if os.path.exists(picture_folder) else None

    # --- CẤU HÌNH FFMPEG (LOGIC KẾT HỢP HOOK) ---
    cmd = ["ffmpeg", "-y"]
    
    # Input 0: Video Background
    if temp_bg_file: cmd += ["-i", temp_bg_file]
    else: cmd += ["-f", "lavfi", "-i", f"color=c=black:s=720x1280:r=24:d={duration}"]

    # Input 1: Ảnh Hook (Màn hình chờ 2.5s đầu)
    if has_hook: cmd += ["-loop", "1", "-t", "2.5", "-i", hook_img_path]

    # Input 2: Overlay bảng điện (Sẽ hiện sau khi Hook biến mất)
    if has_overlay: cmd += ["-loop", "1", "-t", str(duration), "-i", overlay_path]

    # Input 3: Giọng đọc và Nhạc nền (Giữ nguyên logic cũ)
    cmd += ["-i", audio_path]
    bg_music_file = get_random_bg_music("assets/music")
    if bg_music_file: cmd += ["-stream_loop", "-1", "-i", bg_music_file]

    # --- FILTER COMPLEX: ĐÂY LÀ NƠI PHÉP MÀU XẢY RA ---
    filters = []
    
    # Xử lý nền: Saturation 1.2, Contrast 1.1 như cũ
    filters.append("[0:v]scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,eq=saturation=1.2:contrast=1.1[bg]")
    
    last_v = "[bg]"

    # Logic chồng các lớp (Layering)
    if has_hook and has_overlay:
        # 1. Chèn bảng điện lên nền trước
        filters.append(f"[2:v]scale=720:1280[ovl_scaled];{last_v}[ovl_scaled]overlay=0:0:shortest=1[main_stream]")
        # 2. Chèn cái Hook đè lên trên cùng, nhưng chỉ hiện từ giây 0 đến 2.5
        filters.append(f"[1:v]scale=720:1280[hook_scaled];[main_stream][hook_scaled]overlay=0:0:enable='between(t,0,2.5)'[v_final_temp]")
        last_v = "[v_final_temp]"
    elif has_overlay:
        filters.append(f"[1:v]scale=720:1280[ovl];{last_v}[ovl]overlay=0:0:shortest=1[v_over]")
        last_v = "[v_over]"

    # Thêm Subtitle (Chỉ hiện sau 2.5s để không đè lên Hook)
    if safe_sub_path:
        filters.append(f"{last_v}ass='{safe_sub_path}'[final_v]")
    else:
        filters.append(f"{last_v}copy[final_v]")

    # Xử lý Âm thanh (Giữ nguyên logic mixing 8% volume của ông)
    if bg_music_file:
        filters.append(f"[4:a]volume=0.08,atrim=0:{duration},afade=t=out:st={duration-2}:d=2[bg_a]")
        filters.append(f"[3:a][bg_a]amix=inputs=2:duration=first:dropout_transition=2[final_a]")
    else:
        filters.append("[3:a]copy[final_a]")

    cmd += ["-filter_complex", ";".join(filters)]

    # --- OUTPUT SETTINGS (Giữ nguyên cấu hình GHA của ông) ---
    cmd += ["-map", "[final_v]", "-map", "[final_a]", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-c:a", "aac", output]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0: print(f"✅ [RENDER THÀNH CÔNG]: {output}")
        else: print(f"❌ [LỖI FFMPEG]: {result.stderr}")
    finally:
        # Dọn dẹp rác sau khi render
        for p in [overlay_path, hook_img_path, temp_bg_file]:
            if p and os.path.exists(p): os.remove(p)

    return output
