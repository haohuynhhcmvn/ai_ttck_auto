# ==============================
# SCRIPT → SOCIAL CONTENT (PRO)
# ==============================

def script_to_content(script, topic=None):
    # 🔥 tách câu
    lines = script.split("...")

    content = []

    # ==============================
    # HEADER
    # ==============================
    if topic:
        content.append(f"🚨 {topic.upper()}")

    content.append("📊 BẢN TIN CHỨNG KHOÁN HÔM NAY\n")

    # ==============================
    # BODY
    # ==============================
    clean_lines = []

    for line in lines:
        line = line.strip()

        # bỏ line rác
        if not line or len(line) < 5:
            continue

        # fix spacing
        line = line.replace("  ", " ")

        clean_lines.append(line)

    for i, line in enumerate(clean_lines):
        if i == 0:
            content.append(f"🔥 {line}")  # hook mạnh
        elif i < 3:
            content.append(f"⚡ {line}")  # đoạn giữ người xem
        else:
            content.append(f"👉 {line}")

    # ==============================
    # CTA
    # ==============================
    content.append("\n⚠️ Cơ hội luôn đi kèm rủi ro")
    content.append("📈 Follow ngay để không bỏ lỡ tín hiệu quan trọng")

    # ==============================
    # HASHTAG (TỐI ƯU REACH)
    # ==============================
    content.append(
        "\n#chungkhoan #vnindex #dautu #taichinh #stock #investing"
    )

    return "\n".join(content)
