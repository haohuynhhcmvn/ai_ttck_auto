# ==============================================================
# 🎬 RENDER ENGINE PRO (OPTIMIZED FOR GITHUB ACTIONS)
# Bản sửa lỗi: Khớp tham số Pipeline + Progress Bar + Anti-Crash
# ==============================================================

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
import numpy as np

# --- 0. DUMMY OVERLAY (Tránh sập nếu thiếu file overlay.py) ---
try:
    from overlay import draw_overlay
except ImportError:
    def draw_overlay(data): return None

# --- 1. HÀM TẠO ẢNH HOOK (Chống lỗi Font trên GHA) ---
def create_hook_image(hook_text, output_path):
    """Tạo ảnh nền đỏ chữ trắng làm Hook 2.5s đầu."""
    width, height = 720, 1280
    img = Image.new("RGB", (width, height), (180, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_dir = "assets/fonts"
    os.makedirs(font_dir, exist_ok=True)
    font_path = os.path.join(font_dir, "Roboto-Black.ttf")
    
    # Tải font tự động nếu môi trường GHA chưa có
    if not os.path.exists(font_path):
        try:
            url = "https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Black.ttf"
            urllib.request.urlretrieve(url, font_path)
        except: pass

    try:
        font = ImageFont.truetype(font_path, 80)
        # Chuẩn hóa Unicode NFC để hiển thị tiếng Việt chuẩn
        text_to_draw = unicodedata.normalize('NFC', str(hook_text))
    except:
        # Chế độ sinh tồn: Dùng font mặc định và bỏ dấu tiếng Việt
        font = ImageFont.load_default()
        raw_text = unicodedata.normalize('NFKD', str(hook_text))
        text_to_draw = "".join([c for c in raw_text if not unicodedata.combining(c)]).replace('Đ', 'D')

    # Vẽ chữ tự động xuống dòng
    lines = textwrap.wrap(text_to_draw, width=15)
    current_h = 450
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((width - w) / 2, current_h), line, font=font, fill="white")
        current_h += h + 30

    img.save(output_path)
    return output_path

# --- 2. HÀM TẠO SLIDESHOW (Tối ưu RAM cho GHA) ---
def create_random_slideshow(folder_path, target_duration):
    """
    Tạo video nền từ ảnh JPG. 
    Nếu thiếu ảnh: Tự động lặp ngẫu nhiên cho đến khi đủ thời gian.
    """
    all_imgs = glob.glob(os.path.join(folder_path, "*.jpg"))
    if not all_imgs: 
        print("⚠️ [WARN]: Không tìm thấy ảnh trong assets/picture!")
        return None
    
    clips = []
    total_d = 0
    used_imgs = []

    # --- LOGIC LẶP NGẪU NHIÊN ---
    # Chạy vòng lặp cho đến khi tích lũy đủ thời gian yêu cầu
    while total_d < target_duration + 2: # Cộng dư 2s để cắt cho mượt
        # Trộn danh sách ảnh để lấy ngẫu nhiên mỗi vòng
        pool = all_imgs.copy()
        random.shuffle(pool)
        
        for p in pool:
            if total_d >= target_duration + 2: break
            
            try:
                # Tối ưu: Resize ảnh ngay lập tức để tiết kiệm RAM GHA
                u_id = uuid.uuid4().hex[:5]
                tmp_p = f"tmp_{u_id}.jpg"
                with Image.open(p) as img:
                    img = img.convert("RGB").resize((720, 1280))
                    img.save(tmp_p)
                
                # Tạo clip 5 giây, hiệu ứng mờ dần (crossfade)
                # padding=-1 trong concatenate sẽ làm các clip đè lên nhau 1s
                clip = ImageClip(tmp_p).set_duration(5).set_fps(24).crossfadein(1)
                clips.append(clip)
                
                used_imgs.append(tmp_p) # Để tí nữa dọn rác
                total_d += 4 # Mỗi clip 5s nhưng gối đầu 1s nên thực tế tăng 4s
            except Exception as e:
                print(f"❌ Lỗi xử lý ảnh {p}: {e}")
                continue

    if not clips: return None
    
    # Kết nối các đoạn clip lại với nhau
    final_v = concatenate_videoclips(clips, method="compose", padding=-1)
    temp_name = f"bg_{uuid.uuid4().hex[:5]}.mp4"
    
    # Xuất file nền (Sử dụng ultrafast để GHA chạy nhanh nhất)
    final_v.subclip(0, target_duration).write_videofile(
        temp_name, fps=24, codec="libx264", audio=False, 
        logger=None, preset="ultrafast"
    )
    
    # --- DỌN RÁC TRIỆT ĐỂ ---
    for f in used_imgs:
        if os.path.exists(f): os.remove(f)
        
    return temp_name
    
# --- 3. HÀM RENDER TỔNG HỢP (FIX LỖI PIPELINE) ---
def render_video(audio_path, subtitles, output, topic=None, market_data=None, script=None, video_hook=None, ticker_ass=None):
    """
    HÀM QUAN TRỌNG: Đã thêm đầy đủ 'topic' và 'script' để khớp với lệnh gọi từ main.py.
    Tích hợp Progress Bar + Layering chuẩn.
    """
    print(f"🎬 [RENDER]: Bắt đầu render với Hook: {video_hook}")
    
    u_id = uuid.uuid4().hex[:5]
    h_img = f"hook_{u_id}.png"
    o_img = f"ovl_{u_id}.png"
    
    # Bước 1: Lấy thông số Audio
    v_clip = AudioFileClip(audio_path)
    duration = v_clip.duration
    v_clip.close()

    # Bước 2: Chuẩn bị Hook và Overlay (Yahoo Finance)
    has_h = False
    if video_hook:
        create_hook_image(video_hook, h_img)
        has_h = True
        
    has_o = False
    if market_data:
        arr = draw_overlay(market_data)
        if arr is not None:
            Image.fromarray(arr).save(o_img)
            has_o = True

    # Bước 3: Tạo Background
    bg_v = create_random_slideshow("assets/picture", duration)
    bg_m = glob.glob("assets/music/*.mp3")

    # Bước 4: Khởi tạo lệnh FFmpeg (Dạng List để bảo mật đường dẫn)
    cmd = ["ffmpeg", "-y"]
    
    # --- INPUTS ---
    # Input 0: Nền (Slideshow hoặc Đen)
    if bg_v: cmd += ["-i", bg_v]
    else: cmd += ["-f", "lavfi", "-i", f"color=c=black:s=720x1280:d={duration}"]
    
    # Input 1: Hook (2.5s)
    cmd += ["-loop", "1", "-t", "2.5", "-i", h_img] if has_h else ["-f", "lavfi", "-i", "color=c=black:s=2x2:d=0.1"]
    
    # Input 2: Market Data (Yahoo Finance)
    cmd += ["-loop", "1", "-t", str(duration), "-i", o_img] if has_o else ["-f", "lavfi", "-i", "color=c=black:s=2x2:d=0.1"]
    
    # Input 3: Giọng đọc MC
    cmd += ["-i", audio_path]
    
    # Input 4: Nhạc nền (Loop)
    if bg_m: cmd += ["-stream_loop", "-1", "-i", random.choice(bg_m)]

    # --- FILTERS (XẾP LỚP VIDEO) ---
    filters = []
    filters.append("[0:v]scale=720:1280,setpts=PTS-STARTPTS[base]")
    l_v = "[base]"
    
    # Layer: Bảng điện
    if has_o:
        filters.append(f"{l_v}[2:v]overlay=0:0[v_ovl]")
        l_v = "[v_ovl]"
        
    # Layer: Hook (Chỉ hiện 2.5s đầu)
    if has_h:
        filters.append(f"{l_v}[1:v]overlay=0:0:enable='between(t,0,2.5)'[v_hook]")
        l_v = "[v_hook]"

    # Layer: Subtitles MC
    if subtitles and os.path.exists(subtitles):
        s_sub = subtitles.replace("\\", "/").replace(":", "\\:")
        filters.append(f"{l_v}ass='{s_sub}'[v_sub]")
        l_v = "[v_sub]"

    # Layer: Ticker (Nếu có)
    if ticker_ass and os.path.exists(ticker_ass):
        s_tick = ticker_ass.replace("\\", "/").replace(":", "\\:")
        filters.append(f"{l_v}ass='{s_tick}'[v_tick]")
        l_v = "[v_tick]"

    # LAYER CUỐI: PROGRESS BAR (Thanh tiến trình màu Cam)
    filters.append(f"{l_v}drawbox=y=ih-5:w=iw:h=5:color=gray@0.5:t=fill[v_pb_bg]")
    filters.append(f"[v_pb_bg]drawbox=y=ih-5:w=iw*t/{duration}:h=5:color=0xFF9900:t=fill[final_v]")

    # --- AUDIO MIXING ---
    if bg_m:
        filters.append(f"[4:a]volume=0.07,atrim=0:{duration},afade=t=out:st={duration-2}:d=2[bg_a]")
        filters.append(f"[3:a][bg_a]amix=inputs=2:duration=first[a_final]")
    else:
        filters.append("[3:a]copy[a_final]")

    # --- THỰC THI LỆNH ---
    cmd += ["-filter_complex", ";".join(filters), "-map", "[final_v]", "-map", "[a_final]"]
    cmd += ["-c:v", "libx264", "-preset", "ultrafast", "-crf", "28", "-pix_fmt", "yuv420p", output]

    # Convert list to string for shell=True (Xử lý UTF-8 tốt hơn trên Server)
    full_cmd_str = " ".join([f'"{c}"' if ' ' in str(c) or 'ass' in str(c) else str(c) for c in cmd])
    
    try:
        subprocess.run(full_cmd_str, shell=True, check=True, capture_output=True)
        print(f"✅ [SUCCESS]: Xuất video thành công -> {output}")
    except subprocess.CalledProcessError as e:
        print(f"❌ [FFMPEG ERROR]: {e.stderr.decode('utf-8', errors='ignore')}")
    finally:
        # Dọn rác hệ thống
        for f in [h_img, o_img, bg_v]:
            if f and os.path.exists(f): 
                try: os.remove(f)
                except: pass

    return output
