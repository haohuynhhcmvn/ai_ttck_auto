# ==============================
# MARKET DATA PRO - SSI (ANTI BLOCK + STABLE)
# ==============================

import requests
import random
import time


# ==============================
# HEADER GIẢ LẬP TRÌNH DUYỆT (TRÁNH BỊ CHẶN BOT)
# ==============================
def get_headers():
    return {
        # Random user agent để tránh bị detect bot
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (X11; Linux x86_64)"
        ]),
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://iboard.ssi.com.vn/",
        "Origin": "https://iboard.ssi.com.vn"
    }


# ==============================
# SAFE REQUEST (RETRY + CHỐNG DIE API)
# ==============================
def safe_request(url, max_retry=3):
    """
    Gửi request an toàn:
    - Có retry nếu lỗi
    - Tránh crash khi API trả rỗng
    """

    for i in range(max_retry):
        try:
            res = requests.get(
                url,
                headers=get_headers(),
                timeout=5
            )

            # 🔥 Check response hợp lệ
            if res.status_code == 200 and res.text.strip():
                return res.json()

            print(f"⚠️ API rỗng hoặc lỗi status: {res.status_code}")

        except Exception as e:
            print(f"⚠️ Lỗi request lần {i+1}: {e}")

        # ⏳ Delay tăng dần (tránh bị block)
        time.sleep(1 + i)

    return None  # ❌ nếu fail toàn bộ


# ==============================
# LẤY CHỈ SỐ (VNINDEX / VN30)
# ==============================
def get_index(symbol="VNINDEX"):
    """
    Lấy dữ liệu chỉ số:
    - VNINDEX
    - VN30
    """

    url = f"https://iboard.ssi.com.vn/dchart/api/index/{symbol}"

    data = safe_request(url)

    if not data:
        print(f"❌ {symbol} lỗi")
        return {
            "close": "N/A",
            "change": "N/A"
        }

    try:
        return {
            "close": round(float(data.get("close", 0)), 2),
            "change": round(float(data.get("change", 0)), 2)
        }
    except:
        return {
            "close": "N/A",
            "change": "N/A"
        }


# ==============================
# LẤY TOP CỔ PHIẾU TĂNG / GIẢM
# ==============================
def get_top_stocks(limit=10):
    """
    Lấy danh sách:
    - Top tăng
    - Top giảm
    """

    url = "https://iboard.ssi.com.vn/dchart/api/stocklist"

    data = safe_request(url)

    if not data:
        print("❌ Không lấy được danh sách cổ phiếu")
        return [], []

    stocks = []

    for item in data:
        try:
            # Mã cổ phiếu
            symbol = item.get("stockSymbol")

            # % thay đổi
            change = float(item.get("percentChange", 0))

            stocks.append((symbol, round(change, 2)))

        except:
            continue  # bỏ qua nếu lỗi

    # 🔥 Sắp xếp top tăng
    gainers = sorted(stocks, key=lambda x: x[1], reverse=True)[:limit]

    # 🔥 Sắp xếp top giảm
    losers = sorted(stocks, key=lambda x: x[1])[:limit]

    return gainers, losers


# ==============================
# MAIN FUNCTION (DÙNG TOÀN PIPELINE)
# ==============================
def get_market_data():
    """
    Hàm chính trả về toàn bộ data:
    - VNINDEX
    - VN30
    - Top tăng
    - Top giảm
    """

    # 📊 Lấy chỉ số
    vnindex = get_index("VNINDEX")
    vn30 = get_index("VN30")

    # 📈 Lấy top cổ phiếu
    gainers, losers = get_top_stocks()

    return {
        "vnindex": vnindex,
        "vn30": vn30,
        "gainers": gainers,
        "losers": losers
    }
