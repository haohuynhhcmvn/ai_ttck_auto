# ==============================
# SUBTITLE (ASS PRO MAX)
# ==============================

import unicodedata


def normalize_text(text):
    text = unicodedata.normalize("NFC", text)
    text = text.replace(" ,", ",").replace(" .", ".")
    text = text.replace("  ", " ")
    return text.strip()


def format_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02}:{s:05.2f}"


def group_words(words, max_words=6):
    lines = []
    current = []

    for w in words:
        current.append(w)

        if len(current) >= max_words or w["word"].endswith((".", ",")):
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
Style: Default,Noto Sans,70,&H00FFFFFF,&H0000FFFF,&H00000000,1,3,0,5,10,10,300

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

            # 🔥 thời gian highlight (centiseconds)
            duration = int((w["end"] - w["start"]) * 100)

            text += f"{{\\k{duration}}}{word} "

        line = f"Dialogue: {start},{end},Default,{text.strip()}"
        lines.append(line)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filename
