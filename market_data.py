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
        df = yf.download("^VNINDEX", period="1d", progress=False)
        close = df["Close"].iloc[-1]
        open_price = df["Open"].iloc[-1]
        return round(close,2), round(close-open_price,2)
    except:
        return "N/A", "N/A"

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
                close = data["Close"].iloc[-1]
                open_price = data["Open"].iloc[-1]
                change = ((close-open_price)/open_price)*100
                results.append((symbol.replace(".VN",""), round(change,2)))
            except:
                continue

        gainers = sorted(results, key=lambda x:x[1], reverse=True)[:limit]
        losers = sorted(results, key=lambda x:x[1])[:limit]

        gainers = [(s, f"+{v}%") for s,v in gainers]
        losers = [(s, f"{v}%") for s,v in losers]

        return gainers, losers

    except:
        return [], []

def get_market_data():
    vnindex_val, vnindex_change = get_vnindex()
    gainers, losers = get_top_stocks()

    return {
        "vnindex": (vnindex_val, vnindex_change),
        "vn30": (vnindex_val, vnindex_change),  # fallback
        "gainers": gainers,
        "losers": losers
    }
