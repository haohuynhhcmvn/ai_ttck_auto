# ==============================
# MARKET DATA - SSI (BEST)
# ==============================

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# ==============================
# VNINDEX / VN30
# ==============================
def get_index(symbol="VNINDEX"):
    try:
        url = f"https://iboard.ssi.com.vn/dchart/api/index/{symbol}"

        res = requests.get(url, headers=HEADERS, timeout=5)
        data = res.json()

        return {
            "close": round(float(data["close"]), 2),
            "change": round(float(data["change"]), 2)
        }

    except Exception as e:
        print(f"❌ {symbol} lỗi:", e)
        return {"close": "N/A", "change": "N/A"}


# ==============================
# TOP STOCKS
# ==============================
def get_top_stocks(limit=10):
    try:
        url = "https://iboard.ssi.com.vn/dchart/api/stocklist"

        res = requests.get(url, headers=HEADERS, timeout=5)
        data = res.json()

        stocks = []

        for item in data:
            try:
                symbol = item["stockSymbol"]
                change = float(item["percentChange"])

                stocks.append((symbol, round(change, 2)))
            except:
                continue

        gainers = sorted(stocks, key=lambda x: x[1], reverse=True)[:limit]
        losers = sorted(stocks, key=lambda x: x[1])[:limit]

        return gainers, losers

    except Exception as e:
        print("❌ SSI lỗi:", e)
        return [], []


# ==============================
# MAIN
# ==============================
def get_market_data():
    vnindex = get_index("VNINDEX")
    vn30 = get_index("VN30")
    gainers, losers = get_top_stocks()

    return {
        "vnindex": vnindex,
        "vn30": vn30,
        "gainers": gainers,
        "losers": losers
    }
