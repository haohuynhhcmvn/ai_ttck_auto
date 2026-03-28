# ==============================
# SCRIPT → SOCIAL CONTENT (PRO MAX VIRAL)
# ==============================

import random


def script_to_content(script, topic=None):
    lines = script.split("...")

    content = []

    # ==============================
    # HEADER (HOOK)
    # ==============================
    if topic:
        content.append(f"🚨 {topic.upper()}")

    content.append("📊 BẢN TIN CHỨNG KHOÁN HÔM NAY\n")

    # ==============================
    # CLEAN LINES
    # ==============================
    clean_lines = []

    for line in lines:
        line = line.strip()

        if not line or len(line) < 5:
            continue

        line = line.replace("  ", " ")

        clean_lines.append(line)

    # ==============================
    # BODY (TĂNG NHỊP)
    # ==============================
    for i, line in enumerate(clean_lines):

        if i == 0:
            # 🔥 hook mạnh hơn
            content.append(f"🔥 {line.upper()}")

        elif i == 1:
            content.append(f"⚠️ {line}")

        elif i == 2:
            content.append(f"🚀 {line}")

        elif i < 5:
            content.append(f"⚡ {line}")

        else:
            content.append(f"👉 {line}")

    # ==============================
    # CTA (STRONG)
    # ==============================
    ctas = [
        "📈 Follow ngay trước khi quá muộn",
        "🚀 Đừng bỏ lỡ nhịp tăng tiếp theo",
        "⚠️ Người biết sớm đang vào lệnh",
        "🔥 Bạn đã sẵn sàng cho cơ hội này?"
    ]

    content.append("\n⚠️ Cơ hội luôn đi kèm rủi ro")
    content.append(random.choice(ctas))

    # ==============================
    # HASHTAG (ALGO TỐI ƯU)
    # ==============================
    content.append(
        "\n#chungkhoan #stock #dautu #vnstock #fomo #investing #taichinh"
    )

    return "\n".join(content)
