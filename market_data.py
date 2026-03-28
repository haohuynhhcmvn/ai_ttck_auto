# ==============================
# MARKET DATA (CLEAN - NO INDEX)
# ==============================

import yfinance as yf
import pandas as pd
import time

# ==============================
# VNINDEX_ALL LIST
# ==============================
VNINDEX_ALL = [
    # Nhóm VN30 (Bluechips)
    "ACB.VN", "BCM.VN", "BID.VN", "BVH.VN", "CTG.VN", "FPT.VN", "GAS.VN", "GVR.VN",
    "HDB.VN", "HPG.VN", "MBB.VN", "MSN.VN", "MWG.VN", "PLX.VN", "POW.VN", "SAB.VN",
    "SHB.VN", "SSB.VN", "SSI.VN", "STB.VN", "TCB.VN", "TPB.VN", "VCB.VN", "VHM.VN",
    "VIB.VN", "VIC.VN", "VJC.VN", "VNM.VN", "VPB.VN", "VRE.VN",

    # Nhóm Ngân hàng & Tài chính khác
    "LPB.VN", "MSB.VN", "OCB.VN", "EIB.VN", "VDS.VN", "HCM.VN", "VCI.VN", "VND.VN",
    "VIX.VN", "FTS.VN", "BSI.VN", "CTS.VN", "AGR.VN", "ORS.VN", "TVB.VN",

    # Nhóm Bất động sản & Xây dựng
    "NVL.VN", "PDR.VN", "DIG.VN", "DXG.VN", "NLG.VN", "KDH.VN", "KBC.VN", "ITA.VN",
    "SZC.VN", "VGC.VN", "TCH.VN", "HDC.VN", "CRE.VN", "IJC.VN", "CII.VN", "HHV.VN",
    "LCG.VN", "VCG.VN", "HT1.VN", "BCC.VN", "PC1.VN", "CTD.VN", "HBC.VN",

    # Nhóm Thép & Tài nguyên
    "HSG.VN", "NKG.VN", "SMC.VN", "TLH.VN", "TVN.VN", "VGS.VN", "DGC.VN", "CSV.VN",
    "DCM.VN", "DPM.VN", "LAS.VN", "BFC.VN",

    # Nhóm Dầu khí & Năng lượng
    "PVD.VN", "PVT.VN", "PVS.VN", "GEG.VN", "REE.VN", "HDG.VN", "NT2.VN", "QTP.VN",

    # Nhóm Sản xuất, Bán lẻ & Cảng biển
    "VHC.VN", "ANV.VN", "IDI.VN", "MPC.VN", "FMC.VN", "PAN.VN", "DBC.VN", "BAF.VN",
    "FRT.VN", "DGW.VN", "PET.VN", "PNJ.VN", "GMD.VN", "HAH.VN", "VSC.VN", "SGP.VN",

    # Nhóm Cao su, Gỗ & Khác
    "PHR.VN", "DPR.VN", "TRC.VN", "DRI.VN", "TTF.VN", "PTB.VN", "RAL.VN", "BMP.VN",
    "NTP.VN", "TLG.VN", "GIL.VN", "TNG.VN", "MSH.VN", "VGT.VN"
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
            tickers=" ".join(VNINDEX_ALL),
            period="2d",
            group_by="ticker",
            auto_adjust=True,
            threads=True,
            progress=False
        )

        results = []

        for s in VNINDEX_ALL:
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

            for s in VNINDEX_ALL:
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
        "VNINDEX_ALL": {},      # 🔥 giữ để không crash pipeline
        "gainers": gainers,
        "losers": losers
    }
