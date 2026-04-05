# ==============================
# RENDER ENGINE PRO (FIXED ENCODING & HOOK LAYER)
# ==============================

import subprocess
import os
import random
import glob
import uuid
import textwrap
from moviepy.editor import AudioFileClip
from PIL import Image, ImageDraw, ImageFont

# --- [FIX]: HÀM VẼ ẢNH HOOK (ĐẢM BẢO CHỮ KHÔNG LỖI) ---
def create_hook_image(hook_text, output_path):
    """Tạo ảnh nền đỏ chữ trắng. Fix lỗi xuống dòng và font chữ."""
    width, height = 720, 1280
    img = Image.new("RGB", (width, height), (180, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # [QUAN TRỌNG]: Đảm bảo font này có tồn tại, nếu không dùng font hệ thống
    try:
        font = ImageFont.truetype("assets/fonts/Roboto-Black.ttf", 80)
        sub_font = ImageFont.truetype("assets/fonts/Roboto-Medium.ttf", 40)
    except:
        font = ImageFont.load_default()
        sub_font = ImageFont.load_default()

    # Tự động xuống dòng
    lines = textwrap.wrap(hook_text, width=15)
    
    current_h = 500
    for line in lines:
        # Sử dụng textbbox để tính toán căn giữa chuẩn xác
        bbox = draw.textbbox((0, 0), line, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((width - w) / 2, current_h), line, font=font, fill=(255, 255, 255))
        current_h += h + 30

    cta_text = "CHI TIẾT TRONG VIDEO 👇"
    bbox_cta = draw.textbbox((0, 0), cta_text, font=sub_font)
    sw = bbox_cta[2] - bbox_cta[0]
    draw.text(((width - sw) / 2, 1050), cta_text, font=sub_font, fill=(255, 255, 0))

    img.save(output_path)
    return output_path

# ... [Các hàm get_random_bg_music và create_random_slideshow giữ nguyên] ...

def render_video(audio_path, subtitles, output, topic=None, market_data=None, script=None, video_hook=None):
    print(f"🎬 [RENDER]: Đang xử lý Hook: {video_hook}")
    
    # Khởi tạo các đường dẫn tạm
    u_id = uuid.uuid4().hex[:5]
    overlay_path = f"ovl_{u_id}.png"
    hook_img_path = f"hook_{u_id}.png"
    
    # 1. Lấy duration audio
    voice_clip = AudioFileClip(audio_path)
    duration = voice_clip.duration
    voice_clip.close()

    # 2. Tạo ảnh Hook & Overlay
    has_hook = False
    if video_hook:
        create_hook_image(video_hook, hook_img_path)
        has_hook = True

    # [GIỮ NGUYÊN LOGIC OVERLAY CỦA ÔNG]
    has_overlay = False
    # ... (đoạn gọi draw_overlay của ông)

    # --- CẤU HÌNH FFMPEG ---
    cmd = ["ffmpeg", "-y"]
    
    # Input 0: Background
    # Input 1: Hook Image (2.5s)
    # Input 2: Overlay Image
    # Input 3: Audio MC
    # Input 4: Music
    
    # [PHẦN INPUTS]
    cmd += ["-f", "lavfi", "-i", f"color=c=black:s=720x1280:r=24:d={duration}"] # Nền dự phòng
    if has_hook: cmd += ["-loop", "1", "-t", "2.5", "-i", hook_img_path]
    else: cmd += ["-f", "lavfi", "-i", "color=c=black:s=2x2:d=0.1"] # Input giả nếu ko có hook

    # --- [FIX QUAN TRỌNG]: FILTER COMPLEX DÙNG INDEX CHUẨN ---
    # Giả sử ông có 5 inputs như trên
    filters = []
    
    # Lớp nền (Background) - Index [0:v]
    filters.append("[0:v]scale=720:1280,eq=saturation=1.2:contrast=1.1[bg]")
    
    # Nếu có Hook, cho nó đè lên nền trong 2.5s đầu
    if has_hook:
        filters.append(f"[1:v]scale=720:1280[hook_v];[bg][hook_v]overlay=0:0:enable='between(t,0,2.5)'[v_with_hook]")
        last_v = "[v_with_hook]"
    else:
        last_v = "[bg]"

    # Thêm phụ đề ASS (Nếu có)
    if subtitles:
        safe_sub = subtitles.replace("\\", "/").replace(":", "\\:")
        filters.append(f"{last_v}ass='{safe_sub}'[final_v]")
    else:
        filters.append(f"{last_v}copy[final_v]")

    # Mix Audio (Giọng đọc + Nhạc nền)
    # [GIỮ NGUYÊN LOGIC MIXING CỦA ÔNG]
    filters.append(f"[3:a]volume=1.0[voice];[4:a]volume=0.08[bg_music];[voice][bg_music]amix=inputs=2:duration=first[final_a]")

    cmd += ["-filter_complex", ";".join(filters)]
    cmd += ["-map", "[final_v]", "-map", "[final_a]", "-c:v", "libx264", "-preset", "ultrafast", output]

    # --- [THUỐC ĐẶC TRỊ LỖI LATIN-1] ---
    try:
        # Ép Python dùng UTF-8 để nói chuyện với FFmpeg
        process = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            encoding="utf-8", # <--- DÒNG CỨU SINH
            errors="ignore"
        )
        
        if process.returncode != 0:
            print(f"❌ [FFMPEG STDERR]: {process.stderr}")
        else:
            print(f"✅ [RENDER OK]: {output}")
            
    except Exception as e:
        print(f"❌ Lỗi hệ thống khi gọi FFmpeg: {e}")
    finally:
        # Dọn dẹp rác
        if os.path.exists(hook_img_path): os.remove(hook_img_path)

    return output
