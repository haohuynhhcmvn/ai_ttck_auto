# ==============================
# MARKET DATA (FROM COLAB - PRODUCTION)
# ==============================

import yfinance as yf
import pandas as pd

# ==============================
# VN30 LIST (CHUẨN NHƯ COLAB)
# ==============================
VN30 = [
    "ACB.VN","BCM.VN","BID.VN","BVH.VN","CTG.VN","FPT.VN","GAS.VN","GVR.VN",
    "HDB.VN","HPG.VN","MBB.VN","MSN.VN","MWG.VN","PLX.VN","POW.VN","SAB.VN",
    "SHB.VN","SSB.VN","SSI.VN","STB.VN","TCB.VN","TPB.VN","VCB.VN","VHM.VN",
    "VIB.VN","VIC.VN","VJC.VN","VNM.VN","VPB.VN","VRE.VN"
]


# ==============================
# LẤY DATA VN30 (CHUẨN NHƯ COLAB)
# ==============================
def get_vn30_data():
    data = []

    for s in VN30:
        try:
            h = yf.Ticker(s).history(period="2d")

            if len(h) >= 2:
                last = float(h["Close"].iloc[-1])
                prev = float(h["Close"].iloc[-2])

                pct = (last - prev) / prev * 100

                data.append({
                    "symbol": s.replace(".VN", ""),
                    "change": round(pct, 2)
                })

        except:
            continue

    return pd.DataFrame(data)


# ==============================
# VNINDEX (PROXY NHƯ COLAB)
# ==============================
def get_vnindex():
    try:
        h = yf.Ticker("VNM.VN").history(period="2d")

        if len(h) < 2:
            return {"close": "N/A", "change": "N/A"}

        last = float(h["Close"].iloc[-1])
        prev = float(h["Close"].iloc[-2])

        pct = (last - prev) / prev * 100

        return {
            "close": round(last, 2),
            "change": round(pct, 2)
        }

    except Exception as e:
        print("❌ VNINDEX lỗi:", e)
        return {"close": "N/A", "change": "N/A"}


# ==============================
# TOP TĂNG / GIẢM
# ==============================
def get_top_stocks(df, limit=10):
    if df.empty:
        return [], []

    df_sorted = df.sort_values("change", ascending=False)

    gainers = df_sorted.head(limit)
    losers = df_sorted.tail(limit)

    gainers_list = [
        (row["symbol"], round(row["change"], 2))
        for _, row in gainers.iterrows()
    ]

    losers_list = [
        (row["symbol"], round(row["change"], 2))
        for _, row in losers.iterrows()
    ]

    return gainers_list, losers_list


# ==============================
# MAIN FUNCTION (PIPELINE)
# ==============================
def get_market_data():
    try:
        df = get_vn30_data()

        vnindex = get_vnindex()

        gainers, losers = get_top_stocks(df)

        return {
            "vnindex": vnindex,
            "vn30": {
                "close": "VN30",
                "change": "N/A"
            },
            "gainers": gainers,
            "losers": losers,
            "raw": df.to_dict(orient="records")  # 🔥 cho AI dùng
        }

    except Exception as e:
        print("❌ market_data lỗi:", e)

        return {
            "vnindex": {"close": "N/A", "change": "N/A"},
            "vn30": {"close": "N/A", "change": "N/A"},
            "gainers": [],
            "losers": [],
            "raw": []
        }
