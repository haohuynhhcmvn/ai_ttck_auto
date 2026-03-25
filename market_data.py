# ==============================
# MARKET DATA - PRO VERSION
# ==============================

import requests
import yfinance as yf

VN_STOCKS = [
    "SSI.VN","VND.VN","HPG.VN","MWG.VN","FPT.VN",
    "VCB.VN","BID.VN","CTG.VN","TCB.VN","VPB.VN",
    "NVL.VN","PDR.VN","DIG.VN","DXG.VN","KBC.VN",
    "GEX.VN","VIC.VN","VHM.VN","VRE.VN","STB.VN"
]


# ==============================
# VNINDEX (REAL DATA - VNDIRECT)
# ==============================
def get_vnindex():
    try:
        url = "https://priceboard.vndirect.com.vn/graph/day?symbol=VNINDEX"
        res = requests.get(url, timeout=10)
        data = res.json()

        if "data" not in data or not data["data"]:
            return {"close": "N/A", "change": "N/A"}

        last = data["data"][-1]

        close = float(last["close"])
        open_price = float(last["open"])

        return {
            "close": round(close, 2),
            "change": round(close - open_price, 2)
        }

    except Exception as e:
        print("❌ VNINDEX lỗi:", e)
        return {"close": "N/A", "change": "N/A"}


# ==============================
# TOP STOCKS (YAHOO - FAST)
# ==============================
def get_top_stocks(limit=10):
    try:
        df = yf.download(
            VN_STOCKS,
            period="1d",
            group_by="ticker",
            threads=True,
            progress=False
        )

        results = []

        for symbol in VN_STOCKS:
            try:
                data = df[symbol]

                if data.empty:
                    continue

                close = float(data["Close"].iloc[-1])
                open_price = float(data["Open"].iloc[-1])

                if open_price == 0:
                    continue

                change = ((close - open_price) / open_price) * 100

                results.append((symbol.replace(".VN",""), round(change,2)))

            except:
                continue

        gainers = sorted(results, key=lambda x: x[1], reverse=True)[:limit]
        losers = sorted(results, key=lambda x: x[1])[:limit]

        return gainers, losers

    except Exception as e:
        print("❌ TOP STOCK lỗi:", e)
        return [], []


# ==============================
# COMBINE
# ==============================
def get_market_data():
    vnindex = get_vnindex()
    gainers, losers = get_top_stocks()

    return {
        "vnindex": vnindex,
        "gainers": gainers,
        "losers": losers
    }
