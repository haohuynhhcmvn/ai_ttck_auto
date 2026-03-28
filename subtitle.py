# ==============================
# SUBTITLE (ASS PRO MAX++ FIXED)
# ==============================

import unicodedata
import re

# ==============================
# NORMALIZE TEXT (VIETNAMESE SAFE)
# ==============================
def normalize_text(text):
    """Đảm bảo tiếng Việt không bị lỗi font và chuẩn hóa dấu"""
    text = unicodedata.normalize("NFC", text)
    # Loại bỏ các ký tự lạ AI có thể gen ra
    text = re.sub(r'[<>{}\[\]/\\*^$#@~_]', '', text)
    return text.strip()

# ==============================
# FORMAT TIME (ASS STANDARD)
# ==============================
def format_time(t):
    """Chuyển đổi giây sang định dạng H:MM:SS.cc của ASS"""
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    cs = int((t % 1) * 100) # Centiseconds (1/100 giây)
    return f"{h}:{m:02}:{s:02}.{cs:02}"

# ==============================
# GROUP WORDS (SMART BREAK)
# ==============================
def group_words(words, max_words=4):
    """
    Gom nhóm từ để hiển thị trên 1 dòng. 
    max_words=4 giúp chữ to, dễ đọc trên điện thoại.
    """
    lines = []
    current = []

    for w in words:
        word = w.get("word", "").strip()
        if not word: continue

        current.append(w)

        # Ngắt dòng khi đủ số từ hoặc gặp dấu ngắt câu
        if (len(current) >= max_words or word.endswith((".", "!", "?"))):
            lines.append(current)
            current = []

    if current:
        lines.append(current)
    return lines

# ==============================
# MAIN EXPORT ASS
# ==============================
def create_subtitles(words, filename="sub.ass"):
    # Cấu hình Style TikTok: Chữ trắng, viền đen, highlight vàng rực
    # Alignment 5 = Chính giữa màn hình
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,65,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,3,0,5,10,10,450,1
"""
    # PrimaryColour: &H00FFFFFF (Trắng) - Màu chữ lúc chưa đọc đến
    # SecondaryColour: &H0000FFFF (Vàng) - Màu chữ khi đang đọc đến (Karaoke)

    lines = [header, "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]

    groups = group_words(words)

    for group in groups:
        start_ts = format_time(group[0]["start"])
        end_ts = format_time(group[-1]["end"])

        full_text = ""
        for w in group:
            word = normalize_text(w["word"])
            
            # Tính duration theo Centiseconds (1/100s) cho hiệu ứng \k
            # Duration = (End - Start) * 100
            duration = max(1, int(round((w["end"] - w["start"]) * 100)))

            # HIỆU ỨNG KARAOKE NÂNG CAO:
            # \k: Highlight màu từ trái sang phải
            # \fscx115\fscy115: Phóng to 115% khi đang đọc
            effect = f"{{\\k{duration}\\fscx115\\fscy115}}{word}{{\\fscx100\\fscy100}}"
            full_text += effect + " "

        line = f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{full_text.strip()}"
        lines.append(line)

    with open(filename, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(lines))

    print(f"🎬 Subtitle generated: {filename}")
    return filename
