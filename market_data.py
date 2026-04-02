# ==============================
# MARKET DATA PRO (DYNAMIC LIMIT)
# ==============================

import yfinance as yf
import pandas as pd
import time

# ==============================
# DANH SÁCH MÃ VN-INDEX (HOSE/HNX)
# ==============================
VNINDEX_ALL = [
    # Nhóm VN30
    "ACB.VN", "BCM.VN", "BID.VN", "BVH.VN", "CTG.VN", "FPT.VN", "GAS.VN", "GVR.VN",
    "HDB.VN", "HPG.VN", "MBB.VN", "MSN.VN", "MWG.VN", "PLX.VN", "POW.VN", "SAB.VN",
    "SHB.VN", "SSB.VN", "SSI.VN", "STB.VN", "TCB.VN", "TPB.VN", "VCB.VN", "VHM.VN",
    "VIB.VN", "VIC.VN", "VJC.VN", "VNM.VN", "VPB.VN", "VRE.VN",
    
    # Nhóm Tài chính - Chứng khoán - Ngân hàng khác
    "LPB.VN", "MSB.VN", "OCB.VN", "EIB.VN", "VDS.VN", "HCM.VN", "VCI.VN", "VND.VN",
    "VIX.VN", "FTS.VN", "BSI.VN", "CTS.VN", "AGR.VN", "ORS.VN",

    # Nhóm Bất động sản - Xây dựng
    "NVL.VN", "PDR.VN", "DIG.VN", "DXG.VN", "NLG.VN", "KDH.VN", "KBC.VN", "CTD.VN",
    "SZC.VN", "VGC.VN", "TCH.VN", "HDC.VN", "CII.VN", "HHV.VN", "LCG.VN", "VCG.VN",

    # Nhóm Thép - Sản xuất - Năng lượng
    "HSG.VN", "NKG.VN", "DGC.VN", "CSV.VN", "DCM.VN", "DPM.VN", "PVD.VN", "PVT.VN", 
    "REE.VN", "HDG.VN", "NT2.VN", "FRT.VN", "DGW.VN", "PNJ.VN", "GMD.VN", "VHC.VN"
    # --- NHÓM HNX (Lưu ý PVS dùng .HN) ---
    "PVS.HN", "CEO.HN", "SHS.HN", "MBS.HN", "IDC.HN", "VCS.HN", "NTP.HN",
]

def get_index_data():
    """Lấy trạng thái chung của thị trường (VN-Index)"""
    try:
        idx = yf.Ticker("^VNINDEX.VN")
        df = idx.history(period="2d")
        if len(df) >= 2:
            last = df["Close"].iloc[-1]
            prev = df["Close"].iloc[-2]
            change = last - prev
            pct = (change / prev) * 100
            status = "TĂNG" if change > 0 else "GIẢM"
            return {
                "point": round(last, 2),
                "change": round(change, 2),
                "pct": round(pct, 2),
                "status": status
            }
    except: pass
    return {"point": "Đang cập nhật", "change": 0, "pct": 0, "status": "Đi ngang"}

# ==============================
# LẤY TOP TĂNG/GIẢM (DYNAMIC FILTER)
# ==============================
def get_top_stocks(limit=12): # <-- Đã tăng lên 12
    results = []
    print(f"📊 Đang quét dữ liệu thị trường ({len(VNINDEX_ALL)} mã)...")
    
    try:
        raw = yf.download(
            tickers=VNINDEX_ALL,
            period="2d",
            group_by="ticker",
            auto_adjust=True,
            threads=True,
            progress=False,
            timeout=30
        )

        for s in VNINDEX_ALL:
            try:
                df = raw[s].dropna()
                if len(df) < 2: continue

                last_p = df["Close"].iloc[-1]
                prev_p = df["Close"].iloc[-2]
                
                if prev_p == 0: continue
                pct = ((last_p - prev_p) / prev_p) * 100

                results.append({
                    "symbol": s.replace(".VN", ""),
                    "change": round(pct, 2),
                    "price": round(last_p, 2)
                })
            except: continue

    except Exception as e:
        print(f"⚠️ Lỗi tải Batch: {e}")

    if not results: return [], []

    df_res = pd.DataFrame(results)
    
    # BƯỚC LỌC THÔNG MINH (CHỐNG LỖI LOGIC)
    # 1. Chỉ lấy những mã thực sự có % > 0 làm gainers
    df_gainers = df_res[df_res["change"] > 0].sort_values("change", ascending=False)
    
    # 2. Chỉ lấy những mã thực sự có % < 0 làm losers
    df_losers = df_res[df_res["change"] < 0].sort_values("change", ascending=True)

    # Dùng .head(limit): Hàm này tự động tùy biến. Nếu df chỉ có 7 mã, nó trả về 7. Nếu có 50, nó lấy đúng 12.
    gainers = df_gainers.head(limit)
    losers = df_losers.head(limit)

    return list(zip(gainers["symbol"], gainers["change"])), \
           list(zip(losers["symbol"], losers["change"]))

# ==============================
# HÀM CHÍNH CHO PIPELINE
# ==============================
def get_market_data():
    try:
        index_info = get_index_data()
        
        # Mặc định gọi giới hạn 12 mã
        gainers, losers = get_top_stocks(limit=12) 
        
        gain_text = ", ".join([f"{m} tăng {c}%" for m, c in gainers]) if gainers else "không có mã tăng"
        lose_text = ", ".join([f"{m} giảm {c}%" for m, c in losers]) if losers else "không có mã giảm"

        market_status = f"VN-Index hiện ở mức {index_info['point']} điểm, {index_info['status']} {abs(index_info['change'])} điểm, tương đương {abs(index_info['pct'])}%."

        return {
            "index_summary": market_status,
            "gainers": gainers,
            "losers": losers,
            "gain_text": gain_text,
            "lose_text": lose_text,
            "raw_index": index_info
        }
    except Exception as e:
        print(f"❌ Market Data sập: {e}")
        return {
            "index_summary": "Thị trường đang có những diễn biến mới.",
            "gainers": [], "losers": [],
            "gain_text": "đang cập nhật", "lose_text": "đang cập nhật",
            "raw_index": {}
        }

# --- TEST ---
if __name__ == "__main__":
    data = get_market_data()
    print("--- TỔNG QUAN ---")
    print(data["index_summary"])
    print(f"\n🚀 TOP TĂNG ({len(data['gainers'])} mã):", data["gain_text"])
    print(f"📉 TOP GIẢM ({len(data['losers'])} mã):", data["lose_text"])
