# ==============================
# MULTI SCENE VIDEO BUILDER
# ==============================

from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import matplotlib.pyplot as plt


# ==============================
# LOAD FONT
# ==============================
def load_font(size):
    try:
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            size
        )
    except:
        return ImageFont.load_default()


# ==============================
# SCENE 1: HOOK
# ==============================
def scene_hook(topic, duration=3):
    img = Image.new("RGB", (720,1280), (0,0,0))
    draw = ImageDraw.Draw(img)

    font = load_font(60)

    draw.text((50,500), topic, font=font, fill="white")

    return ImageClip(np.array(img)).set_duration(duration).fadein(0.5)


# ==============================
# SCENE 2: MARKET SUMMARY
# ==============================
def scene_market(data, duration=5):
    img = Image.new("RGB", (720,1280), (5,10,25))
    draw = ImageDraw.Draw(img)

    font_big = load_font(70)
    font = load_font(40)

    vn = data.get("vnindex", {})
    close = vn.get("close", "N/A")
    change = vn.get("change", "N/A")

    color = "#00e676" if "+" in str(change) else "#ff4d4f"

    draw.text((50,200), "VN-INDEX", font=font, fill="white")
    draw.text((50,300), str(close), font=font_big, fill=color)
    draw.text((50,400), str(change), font=font, fill=color)

    return ImageClip(np.array(img)).set_duration(duration)


# ==============================
# SCENE 3: CHART
# ==============================
def scene_chart(data, duration=5):
    stocks = []
    values = []

    for s,v in data.get("losers", [])[:10]:
        stocks.append(s)
        try:
            values.append(float(v.replace("%","")))
        except:
            values.append(0)

    plt.figure()
    plt.bar(stocks, values)
    plt.title("Top giảm")

    plt.savefig("chart.png")
    plt.close()

    return ImageClip("chart.png").set_duration(duration)


# ==============================
# SCENE 4: ANALYSIS TEXT
# ==============================
def scene_analysis(script, duration=8):
    img = Image.new("RGB", (720,1280), (10,10,30))
    draw = ImageDraw.Draw(img)

    font = load_font(30)

    y = 100
    for line in script.split(". ")[:10]:
        draw.text((40,y), line, font=font, fill="white")
        y += 40

    return ImageClip(np.array(img)).set_duration(duration)


# ==============================
# SCENE 5: TOP STOCKS
# ==============================
def scene_top(data, duration=5):
    img = Image.new("RGB", (720,1280), (0,0,0))
    draw = ImageDraw.Draw(img)

    font = load_font(35)

    y = 200
    draw.text((50,y), "TOP TĂNG", font=font, fill="#00e676")
    y += 50

    for s,v in data.get("gainers", [])[:5]:
        draw.text((50,y), f"{s} {v}", font=font, fill="#00e676")
        y += 40

    y = 200
    draw.text((400,y), "TOP GIẢM", font=font, fill="#ff4d4f")
    y += 50

    for s,v in data.get("losers", [])[:5]:
        draw.text((400,y), f"{s} {v}", font=font, fill="#ff4d4f")
        y += 40

    return ImageClip(np.array(img)).set_duration(duration)


# ==============================
# BUILD FULL VIDEO
# ==============================
def build_video(topic, data, script, audio_path):
    audio = AudioFileClip(audio_path)

    scenes = [
        scene_hook(topic),
        scene_market(data),
        scene_chart(data),
        scene_analysis(script),
        scene_top(data)
    ]

    video = concatenate_videoclips(scenes)

    video = video.set_audio(audio)

    return video
