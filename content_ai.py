# ==============================
# SCRIPT → SOCIAL CONTENT
# ==============================

def script_to_content(script, topic=None):
    lines = script.split("...")

    content = []

    # 🔥 HOOK (dòng đầu cực quan trọng)
    if topic:
        content.append(f"🚨 {topic.upper()}")

    content.append("📊 BẢN TIN CHỨNG KHOÁN HÔM NAY")

    for i, line in enumerate(lines):
        line = line.strip()

        if not line:
            continue

        # dòng đầu làm nổi bật
        if i == 0:
            content.append(f"\n🔥 {line}")
        else:
            content.append(f"👉 {line}")

    # 🔥 CTA + HASHTAG
    content.append("\n⚠️ Cơ hội luôn đi kèm rủi ro")
    content.append("📈 Follow để không bỏ lỡ tín hiệu quan trọng")

    content.append("\n#chungkhoan #vnindex #dautu #taichinh")

    return "\n".join(content)
