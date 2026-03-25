# ==============================
# MARKET DATA - YAHOO FAST
# ==============================

import yfinance as yf

VN_STOCKS = [
    "SSI.VN","VND.VN","HPG.VN","MWG.VN","FPT.VN",
    "VCB.VN","BID.VN","CTG.VN","TCB.VN","VPB.VN",
    "NVL.VN","PDR.VN","DIG.VN","DXG.VN","KBC.VN",
    "GEX.VN","VIC.VN","VHM.VN","VRE.VN","STB.VN"
]


def get_vnindex():
    try:
        df = yf.download("VNM", period="1d", progress=False)

        if df.empty:
            return {"close": "N/A", "change": "N/A"}

        close = float(df["Close"].iloc[-1])
        open_price = float(df["Open"].iloc[-1])

        return {
            "close": round(close, 2),
            "change": round(close - open_price, 2)
        }

    except Exception as e:
        print("❌ VNINDEX lỗi:", e)
        return {"close": "N/A", "change": "N/A"}


def get_top_stocks(limit=10):
    try:
        df = yf.download(VN_STOCKS, period="1d", group_by="ticker", threads=True, progress=False)

        results = []

        for symbol in VN_STOCKS:
            try:
                data = df[symbol]
                close = data["Close"].iloc[-1]
                open_price = data["Open"].iloc[-1]

                change = ((close - open_price) / open_price) * 100

                results.append((symbol.replace(".VN",""), round(change,2)))
            except:
                continue

        gainers = sorted(results, key=lambda x:x[1], reverse=True)[:limit]
        losers = sorted(results, key=lambda x:x[1])[:limit]

        return gainers, losers

    except:
        return [], []


def get_market_data():
    vnindex = get_vnindex()
    gainers, losers = get_top_stocks()

    return {
        "vnindex": vnindex,
        "gainers": gainers,
        "losers": losers
    }
