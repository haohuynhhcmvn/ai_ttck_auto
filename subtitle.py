# ==============================
# SUBTITLE (ASS PRO MAX++)
# ==============================

import unicodedata
import re


# ==============================
# NORMALIZE TEXT (VIETNAMESE SAFE)
# ==============================
def normalize_text(text):
    text = unicodedata.normalize("NFC", text)

    # fix spacing
    text = text.replace(" ,", ",").replace(" .", ".")
    text = re.sub(r"\s+", " ", text)

    # 🔥 xử lý số cho đẹp khi hiển thị
    text = text.replace("%", " %")

    return text.strip()


# ==============================
# FORMAT TIME
# ==============================
def format_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02}:{s:05.2f}"


# ==============================
# GROUP WORDS
# ==============================
def group_words(words, max_words=6):
    lines = []
    current = []

    for w in words:
        word = w.get("word", "").strip()

        if not word:
            continue

        current.append(w)

        # 🔥 break thông minh hơn
        if (
            len(current) >= max_words
            or word.endswith((".", ",", "!", "?"))
        ):
            lines.append(current)
            current = []

    if current:
        lines.append(current)

    return lines


# ==============================
# MAIN EXPORT ASS
# ==============================
def create_subtitles(words, filename="sub.ass"):
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV

Style: Default,DejaVu Sans,70,&H00FFFFFF,&H0000FFFF,&H00000000,1,3,0,5,10,10,320

[Events]
Format: Start, End, Style, Text
"""

    lines = [header]

    groups = group_words(words)

    for group in groups:
        start = format_time(group[0]["start"])
        end = format_time(group[-1]["end"])

        text = ""

        for w in group:
            word = normalize_text(w["word"])

            # 🔥 chống lỗi duration = 0
            duration = max(1, int((w["end"] - w["start"]) * 100))

            # 🔥 PRO EFFECT:
            # - highlight vàng
            # - phóng to nhẹ khi đọc
            effect = (
                f"{{\\k{duration}"
                f"\\fscx110\\fscy110"      # zoom nhẹ
                f"\\bord3\\shad0"
                f"}}{word}"
            )

            text += effect + " "

        line = f"Dialogue: {start},{end},Default,{text.strip()}"
        lines.append(line)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filename
