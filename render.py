# ==============================
# RENDER ENGINE PRO (ULTIMATE UNICODE FIX)
# ==============================

import subprocess
import os
import random
import glob
import uuid
import textwrap
import unicodedata
from moviepy.editor import AudioFileClip
from PIL import Image, ImageDraw, ImageFont

def create_hook_image(hook_text, output_path):
    """Tạo ảnh nền đỏ chữ trắng. Fix lỗi xuống dòng và font chữ."""
    # Chuẩn hóa Unicode NFC để tránh lỗi ký tự tổ hợp
    hook_text = unicodedata.normalize('NFC', str(hook_text))
    
    width, height = 720, 1280
    img = Image.new("RGB", (width, height), (180, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("assets/fonts/Roboto-Black.ttf", 80)
        sub_font = ImageFont.truetype("assets/fonts/Roboto-Medium.ttf", 40)
    except:
        # Nếu GHA thiếu font, dùng font mặc định nhưng sẽ xấu
        font = ImageFont.load_default()
        sub_font = ImageFont.load_default()

    lines = textwrap.wrap(hook_text, width=15)
    current_h = 500
    for line in lines:
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

# Giả định các hàm phụ trợ của ông ở đây...
def get_random_bg_music(path): return None 
def create_random_slideshow(p, d): return None

def render_video(audio_path, subtitles, output, topic=None, market_data=None, script=None, video_hook=None):
    # Chuẩn hóa hook ngay khi nhận vào
    video_hook = unicodedata.normalize('NFC', str(video_hook or "BẢN TIN CHỨNG KHOÁN"))
    print(f"🎬 [RENDER]: Đang xử lý Hook: {video_hook}")
    
    u_id = uuid.uuid4().hex[:5]
    overlay_path = f"ovl_{u_id}.png"
    hook_img_path = f"hook_{u_id}.png"
    
    voice_clip = AudioFileClip(audio_path)
    duration = voice_clip.duration
    voice_clip.close()

    # 1. Tạo ảnh Hook
    create_hook_image(video_hook, hook_img_path)

    # 2. Xây dựng Command List
    # Để tránh lỗi Latin-1, chúng ta sẽ không để chuỗi Tiếng Việt vào 'cmd' 
    # trừ khi nó là tên file (đã được xử lý bởi OS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    
    # Input 0: Nền
    cmd += ["-f", "lavfi", "-i", f"color=c=black:s=720x1280:r=24:d={duration}"]
    # Input 1: Hook (Ảnh đã được vẽ chữ, FFmpeg không cần quan tâm text là gì nữa)
    cmd += ["-loop", "1", "-t", "2.5", "-i", f'"{hook_img_path}"']
    # Input 3: Audio
    cmd += ["-i", f'"{audio_path}"']
    # Input 4: Music (Nếu có)
    bg_music = "assets/music/bg.mp3" # Giả định
    if os.path.exists(bg_music):
        cmd += ["-stream_loop", "-1", "-i", f'"{bg_music}"']

    # 3. Filter Complex
    # Lưu ý: Các ký tự tiếng Việt trong 'ass' path cần được escape cực kỹ
    filters = []
    filters.append("[0:v]scale=720:1280,eq=saturation=1.2:contrast=1.1[bg]")
    filters.append(f"[1:v]scale=720:1280[hook_v];[bg][hook_v]overlay=0:0:enable='between(t,0,2.5)'[v_hooked]")
    
    if subtitles and os.path.exists(subtitles):
        # Escape dấu hai chấm cho path trên Windows/Linux
        safe_sub = subtitles.replace("\\", "/").replace(":", "\\:")
        filters.append(f"[v_hooked]ass='{safe_sub}'[final_v]")
    else:
        filters.append("[v_hooked]copy[final_v]")

    # Mix Audio
    filters.append("[2:a]volume=1.0[v_a];[3:a]volume=0.1[m_a];[v_a][m_a]amix=inputs=2:duration=first[final_a]")

    cmd += ["-filter_complex", f'"{";".join(filters)}"']
    cmd += ["-map", "[final_v]", "-map", "[final_a]", "-c:v", "libx264", "-preset", "ultrafast", f'"{output}"']

    # --- [CHỐT HẠ]: CHUYỂN TOÀN BỘ SANG STRING ĐỂ BYPASS CODEC ---
    full_cmd = " ".join(cmd)

    try:
        # Chạy lệnh với shell=True và encoding rõ ràng
        process = subprocess.run(
            full_cmd,
            shell=True, # Dùng shell giúp xử lý chuỗi Unicode tốt hơn trên Terminal
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        
        if process.returncode != 0:
            print(f"❌ [FFMPEG STDERR]: {process.stderr}")
        else:
            print(f"✅ [RENDER OK]: {output}")
            
    except Exception as e:
        print(f"❌ Render sập: {e}")
    finally:
        if os.path.exists(hook_img_path): os.remove(hook_img_path)

    return output
