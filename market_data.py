# ==============================
# MARKET DATA PRO - YAHOO STABLE
# ==============================

import yfinance as yf
import pandas as pd
import time

# ==============================
# DANH SÁCH VN30 (CHUẨN)
# ==============================
VN30 = [
    "ACB.VN","BCM.VN","BID.VN","BVH.VN","CTG.VN","FPT.VN","GAS.VN","GVR.VN",
    "HDB.VN","HPG.VN","MBB.VN","MSN.VN","MWG.VN","PLX.VN","POW.VN","SAB.VN",
    "SHB.VN","SSB.VN","SSI.VN","STB.VN","TCB.VN","TPB.VN","VCB.VN","VHM.VN",
    "VIB.VN","VIC.VN","VJC.VN","VNM.VN","VPB.VN","VRE.VN"
]

# ==============================
# SAFE DOWNLOAD (TRÁNH DIE API)
# ==============================
def safe_download(ticker):
    try:
        df = yf.Ticker(ticker).history(period="2d")

        if df is None or df.empty or len(df) < 2:
            return None

        return df

    except Exception as e:
        print(f"❌ Lỗi tải {ticker}:", e)
        return None


# ==============================
# VNINDEX (GIẢ LẬP TỪ VNM)
# ==============================
def get_vnindex():
    """
    ⚠️ Yahoo KHÔNG có VNINDEX thật
    → dùng proxy từ VNM (ổn định nhất)
    """

    df = safe_download("VNM.VN")

    if df is None:
        return {"close": "N/A", "change": "N/A"}

    try:
        last = float(df["Close"].iloc[-1])
        prev = float(df["Close"].iloc[-2])

        change = last - prev

        return {
            "close": round(last, 2),
            "change": round(change, 2)
        }

    except:
        return {"close": "N/A", "change": "N/A"}


# ==============================
# VN30 INDEX (GIẢ LẬP)
# ==============================
def get_vn30(df):
    """
    Lấy trung bình VN30 → giả lập index
    """

    try:
        avg = df["Change"].mean()

        return {
            "close": "N/A",
            "change": round(avg, 2)
        }

    except:
        return {"close": "N/A", "change": "N/A"}


# ==============================
# TOP STOCKS
# ==============================
def get_top_stocks(limit=10):
    results = []

    for s in VN30:
        df = safe_download(s)

        if df is None:
            continue

        try:
            last = float(df["Close"].iloc[-1])
            prev = float(df["Close"].iloc[-2])

            pct = (last - prev) / prev * 100

            results.append({
                "symbol": s.replace(".VN", ""),
                "change": round(pct, 2)
            })

        except:
            continue

        # ⚡ tránh rate limit
        time.sleep(0.05)

    if not results:
        return [], [], pd.DataFrame()

    df = pd.DataFrame(results)

    gainers = df.sort_values("change", ascending=False).head(limit)
    losers = df.sort_values("change").head(limit)

    gainers_list = list(zip(gainers["symbol"], gainers["change"]))
    losers_list = list(zip(losers["symbol"], losers["change"]))

    return gainers_list, losers_list, df


# ==============================
# MAIN FUNCTION
# ==============================
def get_market_data():
    """
    Output chuẩn cho toàn pipeline
    """

    # 🔥 lấy top cổ phiếu
    gainers, losers, df = get_top_stocks()

    # 🔥 lấy index
    vnindex = get_vnindex()
    vn30 = get_vn30(df)

    return {
        "vnindex": vnindex,
        "vn30": vn30,
        "gainers": gainers,
        "losers": losers
    }
