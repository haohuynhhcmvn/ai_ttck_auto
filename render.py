# ==============================================================
# 🎬 RENDER ENGINE PRO - TỐI ƯU CHO GITHUB ACTIONS & TELEGRAM
# Bản sửa lỗi: Hiện Market Data + Chống lỗi font + Nén video < 50MB
# ==============================================================

import subprocess
import os
import random
import glob
import uuid
import textwrap
import urllib.request
import unicodedata
import pickle
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

# --- [PHẦN 0]: NHẬP MODULE VẼ BIỂU ĐỒ (OVERLAY) ---
try:
    from overlay import draw_overlay
except ImportError:
    # Nếu không tìm thấy file overlay.py, trả về None để không làm sập tiến trình
    def draw_overlay(data): return None

# --- [PHẦN 1]: HÀM TẠO ẢNH HOOK (3 GIÂY ĐẦU) ---
def create_hook_image(hook_text, output_path):
    """
    Tạo một tấm ảnh nền đỏ, chữ trắng để làm Hook giữ chân người xem.
    Tự động tải Font từ Google Fonts nếu môi trường (GHA) bị thiếu.
    """
    width, height = 720, 1280
    # Màu đỏ đậm (Deep Red) cho sự chú ý
    img = Image.new("RGB", (width, height), (180, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_dir = "assets/fonts"
    os.makedirs(font_dir, exist_ok=True)
    
    main_font_path = os.path.join(font_dir, "Roboto-Black.ttf")
    
    # Tự động tải font nếu chưa có
    if not os.path.exists(main_font_path):
        print("📥 [Pillow]: Đang tải font Roboto-Black từ GitHub...")
        url = "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Black.ttf"
        urllib.request.urlretrieve(url, main_font_path)

    # Xử lý Unicode để không bị lỗi "ô, ơ, á, à..."
    try:
        font = ImageFont.truetype(main_font_path, 85)
        text_to_draw = unicodedata.normalize('NFC', str(hook_text))
    except:
        # Nếu font hỏng, dùng font mặc định và bỏ dấu Tiếng Việt (chế độ sinh tồn)
        font = ImageFont.load_default()
        raw_text = unicodedata.normalize('NFKD', str(hook_text))
        text_to_draw = "".join([c for c in raw_text if not unicodedata.combining(c)]).replace('Đ', 'D')

    # Vẽ chữ tự động xuống dòng
    lines = textwrap.wrap(text_to_draw, width=15)
    current_h = 450
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((width - w) / 2, current_h), line, font=font, fill=(255, 255, 255))
        current_h += h + 40

    # Vẽ dòng chữ kêu gọi (CTA)
    sub_font = ImageFont.truetype(main_font_path, 45) if os.path.exists(main_font_path) else font
    cta_text = "CHI TIẾT TRONG VIDEO 👇"
    draw.text((150, 1100), cta_text, font=sub_font, fill=(255, 255, 0))

    img.save(output_path)
    return output_path

# --- [PHẦN 2]: HÀM TẠO SLIDESHOW (HÌNH NỀN CHẠY) ---
def create_random_slideshow(folder_path, target_duration):
    """
    Tạo video từ các ảnh JPG trong thư mục. Tối ưu RAM cho GitHub Actions.
    """
    search_path = os.path.join(folder_path, "*.jpg")
    all_images = glob.glob(search_path)
    if not all_images: return None

    random.shuffle(all_images)
    clips = []
    current_total_dur = 0
    
    # Giới hạn số lượng ảnh để không bị tràn RAM
    for img_p in all_images[:15]: 
        if current_total_dur >= target_duration: break
        try:
            with Image.open(img_p) as img:
                # Resize và Crop về khung 9:16 (720x1280)
                img = img.convert("RGB")
                w, h = img.size
                if w/h > 720/1280:
                    new_w = int((h * 720) / 1280)
                    img = img.crop(((w - new_w)//2, 0, (w + new_w)//2, h))
                img = img.resize((720, 1280), Image.LANCZOS)
                
                tmp_name = f"tmp_{uuid.uuid4().hex[:5]}.jpg"
                img.save(tmp_name, quality=80)
                
                clip = ImageClip(tmp_name).set_duration(5).crossfadein(1)
                clips.append(clip)
                current_total_dur += 4 # Trừ đi phần transition
        except: continue

    if not clips: return None
    final_video = concatenate_videoclips(clips, method="compose", padding=-1)
    temp_mp4 = f"bg_{uuid.uuid4().hex[:5]}.mp4"
    final_video.subclip(0, target_duration).write_videofile(temp_mp4, fps=24, codec="libx264", audio=False, logger=None, preset="ultrafast")
    
    # Dọn dẹp ảnh tạm
    for f in glob.glob("tmp_*.jpg"): os.remove(f)
    return temp_mp4

# --- [PHẦN 3]: HÀM RENDER CHÍNH (SỬ DỤNG FFMPEG) ---
def render_video(audio_path, subtitles, output, market_data=None, video_hook=None):
    """
    Kết hợp tất cả thành phần: Nền + Market Data + Hook + Subtitle + Nhạc
    """
    print(f"🚀 [RENDER]: Đang chuẩn bị Pipeline cho: {video_hook}")
    
    u_id = uuid.uuid4().hex[:5]
    hook_path = f"hook_{u_id}.png"
    ovl_path = f"ovl_{u_id}.png"
    
    # 1. Đo độ dài âm thanh
    voice_clip = AudioFileClip(audio_path)
    dur = voice_clip.duration
    voice_clip.close()

    # 2. Chuẩn bị ảnh Hook (2.5 giây đầu)
    has_hook = False
    if video_hook:
        create_hook_image(video_hook, hook_path)
        has_hook = True

    # 3. Chuẩn bị Market Data Overlay (Bảng điện)
    has_ovl = False
    if market_data:
        img_arr = draw_overlay(market_data)
        if img_arr is not None:
            # Lưu dạng RGBA để có thể đè lên nền (Transparent)
            Image.fromarray(img_arr).convert("RGBA").resize((720, 1280)).save(ovl_path)
            has_ovl = True

    # 4. Tạo video nền (Slideshow)
    bg_video = create_random_slideshow("assets/picture", dur)
    
    # 5. Nhạc nền
    bg_music = None
    music_files = glob.glob("assets/music/*.mp3")
    if music_files: bg_music = random.choice(music_files)

    # 6. Xây dựng lệnh FFmpeg
    # Dùng list để an toàn, sau đó nối thành string để shell=True xử lý UTF-8
    inputs = []
    # Input 0: Nền
    if bg_video: inputs += ["-i", bg_video]
    else: inputs += ["-f", "lavfi", "-i", f"color=c=black:s=720x1280:d={dur}"]
    
    # Input 1: Hook (Lặp lại để làm video tĩnh)
    inputs += ["-loop", "1", "-t", "2.5", "-i", hook_path if has_hook else "color=c=black:s=2x2:d=0.1"]
    
    # Input 2: Market Data
    inputs += ["-loop", "1", "-t", str(dur), "-i", ovl_path if has_ovl else "color=c=black:s=2x2:d=0.1"]
    
    # Input 3: Giọng đọc (MC)
    inputs += ["-i", audio_path]
    
    # Input 4: Nhạc nền
    if bg_music: inputs += ["-stream_loop", "-1", "-i", bg_music]

    # --- FILTER COMPLEX: QUY TRÌNH XẾP LỚP (LAYERING) ---
    # Lớp 1: [bg] là video slideshow
    # Lớp 2: Đè Market Data lên [bg] -> [v_market]
    # Lớp 3: Đè Hook lên [v_market] chỉ trong 2.5s đầu -> [v_hook]
    # Lớp 4: Chèn Subtitle vào [v_hook] -> [final]
    
    f_complex = [
        "[0:v]scale=720:1280,setpts=PTS-STARTPTS[base]"
    ]
    
    last_v = "[base]"
    
    if has_ovl:
        f_complex.append(f"{last_v}[2:v]overlay=0:0[v_ovl]")
        last_v = "[v_ovl]"
        
    if has_hook:
        # enable='between(t,0,2.5)' giúp Hook biến mất sau 2.5 giây để hiện bảng điện bên dưới
        f_complex.append(f"{last_v}[1:v]overlay=0:0:enable='between(t,0,2.5)'[v_hook]")
        last_v = "[v_hook]"

    # Subtitles (Xử lý đường dẫn đặc biệt cho FFmpeg)
    if subtitles:
        safe_ass = subtitles.replace("\\", "/").replace(":", "\\:")
        f_complex.append(f"{last_v}ass='{safe_ass}'[v_sub]")
        last_v = "[v_sub]"

    # Trộn âm thanh: Giọng MC to (1.0), nhạc nền nhỏ (0.07)
    if bg_music:
        f_complex.append(f"[4:a]volume=0.07,atrim=0:{dur}[bg_a];[3:a][bg_a]amix=inputs=2:duration=first[a_final]")
    else:
        f_complex.append("[3:a]copy[a_final]")

    # Kết hợp lệnh
    cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", ";".join(f_complex)] + [
        "-map", last_v, "-map", "[a_final]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "28", # CRF 28 để file nhẹ dưới 50MB
        "-c:a", "aac", "-b:a", "128k", "-pix_fmt", "yuv420p", output
    ]

    # Chạy FFmpeg
    full_cmd_str = " ".join([f'"{arg}"' if ' ' in str(arg) or 'ass' in str(arg) else str(arg) for arg in cmd])
    try:
        subprocess.run(full_cmd_str, shell=True, check=True, capture_output=True)
        print(f"✅ [SUCCESS]: Video đã sẵn sàng -> {output}")
    except subprocess.CalledProcessError as e:
        print(f"❌ [ERROR]: FFmpeg sập! Lỗi: {e.stderr.decode('utf-8', errors='ignore')}")
    finally:
        # Dọn dẹp rác sau khi render
        if os.path.exists(hook_path): os.remove(hook_path)
        if os.path.exists(ovl_path): os.remove(ovl_path)
        if bg_video and os.path.exists(bg_video): os.remove(bg_video)

    return output
