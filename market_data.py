# ==============================
# MARKET DATA (CLEAN - NO INDEX)
# ==============================

import yfinance as yf
import pandas as pd
import time

# ==============================
# VN30 LIST
# ==============================
VN30 = [
    "ACB.VN","BCM.VN","BID.VN","BVH.VN","CTG.VN","FPT.VN","GAS.VN","GVR.VN",
    "HDB.VN","HPG.VN","MBB.VN","MSN.VN","MWG.VN","PLX.VN","POW.VN","SAB.VN",
    "SHB.VN","SSB.VN","SSI.VN","STB.VN","TCB.VN","TPB.VN","VCB.VN","VHM.VN",
    "VIB.VN","VIC.VN","VJC.VN","VNM.VN","VPB.VN","VRE.VN"
]

# ==============================
# SAFE DOWNLOAD (FALLBACK)
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
# TOP STOCKS (BATCH FAST)
# ==============================
def get_top_stocks(limit=20):
    try:
        raw = yf.download(
            tickers=" ".join(VN30),
            period="2d",
            group_by="ticker",
            auto_adjust=True,
            threads=True,
            progress=False
        )

        results = []

        for s in VN30:
            try:
                df = raw[s]

                if df is None or len(df) < 2:
                    continue

                last = float(df["Close"].iloc[-1])
                prev = float(df["Close"].iloc[-2])

                pct = (last - prev) / prev * 100

                results.append({
                    "symbol": s.replace(".VN", ""),
                    "change": round(pct, 2)
                })

            except:
                continue

        # 🔥 fallback nếu batch fail
        if not results:
            print("⚠️ Batch fail → fallback từng mã")

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

                time.sleep(0.05)

        if not results:
            return [], [], pd.DataFrame()

        df_res = pd.DataFrame(results)

        gainers = df_res.sort_values("change", ascending=False).head(limit)
        losers = df_res.sort_values("change").head(limit)

        gainers_list = list(zip(gainers["symbol"], gainers["change"]))
        losers_list = list(zip(losers["symbol"], losers["change"]))

        return gainers_list, losers_list, df_res

    except Exception as e:
        print("❌ Lỗi get_top_stocks:", e)
        return [], [], pd.DataFrame()


# ==============================
# MAIN FUNCTION (GIỮ FORMAT)
# ==============================
def get_market_data():
    gainers, losers, _ = get_top_stocks()

    return {
        "vnindex": {},   # 🔥 giữ để không crash pipeline
        "vn30": {},      # 🔥 giữ để không crash pipeline
        "gainers": gainers,
        "losers": losers
    }
