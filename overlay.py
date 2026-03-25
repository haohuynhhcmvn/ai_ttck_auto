from moviepy.editor import TextClip

def create_market_overlay(data, duration):
    clips = []

    # 📊 VNINDEX
    vnindex_text = f"VN-Index: {data['vnindex']['value']} ({data['vnindex']['change']})"

    clips.append(
        TextClip(
            vnindex_text,
            fontsize=40,
            color="white",
            font="assets/fonts/NotoSans-Bold.ttf"
        )
        .set_position(("center", 50))
        .set_duration(duration)
    )

    # 📊 VN30
    vn30_text = f"VN30: {data['vn30']['value']} ({data['vn30']['change']})"

    clips.append(
        TextClip(
            vn30_text,
            fontsize=35,
            color="yellow",
            font="assets/fonts/NotoSans-Bold.ttf"
        )
        .set_position(("center", 100))
        .set_duration(duration)
    )

    # 🔥 TOP GAINERS
    y = 200
    for stock, val in data["top_gainers"][:5]:
        clips.append(
            TextClip(
                f"↑ {stock}: {val}",
                fontsize=30,
                color="green",
                font="assets/fonts/NotoSans-Regular.ttf"
            )
            .set_position((50, y))
            .set_duration(duration)
        )
        y += 40

    # 🔻 TOP LOSERS
    y = 200
    for stock, val in data["top_losers"][:5]:
        clips.append(
            TextClip(
                f"↓ {stock}: {val}",
                fontsize=30,
                color="red",
                font="assets/fonts/NotoSans-Regular.ttf"
            )
            .set_position((400, y))
            .set_duration(duration)
        )
        y += 40

    return clips
