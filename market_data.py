# ==============================
# MARKET DATA PRO (DYNAMIC LIMIT)
# ==============================

import yfinance as yf
import pandas as pd
import time

# ==============================
# DANH SÁCH MÃ VN-INDEX (HOSE/HNX)
# ==============================
# Danh sách mã chứng khoán cập nhật mới nhất cho Yahoo Finance
VNINDEX_ALL = [
    # --- NHÓM VN30 (Cập nhật kỳ cơ cấu Q1/2026) ---
    "ACB.VN", "BID.VN", "CTG.VN", "DGC.VN", "FPT.VN", "GAS.VN", "GVR.VN", "HDB.VN", 
    "HPG.VN", "LPB.VN", "MBB.VN", "MSN.VN", "MWG.VN", "PLX.VN", "SAB.VN", "SHB.VN", 
    "SSB.VN", "SSI.VN", "STB.VN", "TCB.VN", "TPB.VN", "VCB.VN", "VHM.VN", "VIB.VN", 
    "VIC.VN", "VJC.VN", "VNM.VN", "VPB.VN", "VPL.VN", "VRE.VN",

    # --- NHÓM TÀI CHÍNH - NGÂN HÀNG - CHỨNG KHOÁN MỞ RỘNG ---
    "MSB.VN", "OCB.VN", "EIB.VN", "VDS.VN", "HCM.VN", "VCI.VN", "VND.VN", "VIX.VN", 
    "FTS.VN", "BSI.VN", "CTS.VN", "AGR.VN", "ORS.VN", "TCBS.VN", "MBS.VN",

    # --- NHÓM BẤT ĐỘNG SẢN - XÂY DỰNG - KHU CÔNG NGHIỆP ---
    "NVL.VN", "PDR.VN", "DIG.VN", "DXG.VN", "NLG.VN", "KDH.VN", "KBC.VN", "CTD.VN",
    "SZC.VN", "VGC.VN", "TCH.VN", "HDC.VN", "CII.VN", "HHV.VN", "LCG.VN", "VCG.VN",
    "BCM.VN", "IDC.VN",

    # --- NHÓM THÉP - SẢN XUẤT - NĂNG LƯỢNG ---
    "HSG.VN", "NKG.VN", "CSV.VN", "DCM.VN", "DPM.VN", "PVD.VN", "PVT.VN", "REE.VN", 
    "HDG.VN", "NT2.VN", "POW.VN", "HVN.VN",

    # --- NHÓM CÔNG NGHỆ - BÁN LẺ - TIÊU DÙNG & CỔ PHIẾU CÓ VỐN HÓA LỚN ---
    "FRT.VN", "DGW.VN", "PNJ.VN", "GMD.VN", "VHC.VN", "MCH.VN", "CTR.VN", "VGI.VN",
    "ACV.VN", "BSR.VN"
]
def get_market_data():
    try:
        # 1. Lấy dữ liệu VN-Index
        idx = yf.Ticker("^VNINDEX.VN")
        df_idx = idx.history(period="2d")
        index_info = {"point": "---", "change": 0, "pct": 0, "status": "Đi ngang"}
        if len(df_idx) >= 2:
            last = df_idx["Close"].iloc[-1]
            change = last - df_idx["Close"].iloc[-2]
            index_info = {
                "point": round(last, 2),
                "change": round(change, 2),
                "pct": round((change / df_idx["Close"].iloc[-2]) * 100, 2),
                "status": "TĂNG" if change > 0 else "GIẢM"
            }

        # 2. Tải Batch dữ liệu 4 cột
        raw = yf.download(tickers=VNINDEX_ALL, period="2d", group_by="ticker", progress=False, timeout=20)
        results = []
        for s in VNINDEX_ALL:
            try:
                df = raw[s].dropna()
                if len(df) < 2: continue
                last_p = df["Close"].iloc[-1]
                prev_p = df["Close"].iloc[-2]
                pct = ((last_p - prev_p) / prev_p) * 100
                results.append({
                    "symbol": s.split('.')[0],
                    "price": round(last_p, 2),
                    "change": round(pct, 2),
                    "volume": df["Volume"].iloc[-1]
                })
            except: continue

        df_res = pd.DataFrame(results)
        gainers = df_res[df_res["change"] > 0].sort_values("change", ascending=False).head(12).to_dict('records')
        losers = df_res[df_res["change"] < 0].sort_values("change", ascending=True).head(12).to_dict('records')

        return {
            "index_summary": f"VN-Index: {index_info['point']} ({index_info['change']})",
            "gainers": gainers,
            "losers": losers,
            "raw_index": index_info
        }
    except Exception as e:
        print(f"❌ Market Data Error: {e}")
        return {"gainers": [], "losers": [], "index_summary": "Dữ liệu đang cập nhật"}
