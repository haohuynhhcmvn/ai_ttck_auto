# ==============================
# MARKET DATA PRO (CLEAN & RELIABLE)
# ==============================

import yfinance as yf
import pandas as pd
import time
import os

# ==============================
# DANH SÁCH MÃ VN-INDEX (HOSE/HNX)
# ==============================
VNINDEX_ALL = [
    # VN30
    "ACB.VN", "BCM.VN", "BID.VN", "BVH.VN", "CTG.VN", "FPT.VN", "GAS.VN", "GVR.VN",
    "HDB.VN", "HPG.VN", "MBB.VN", "MSN.VN", "MWG.VN", "PLX.VN", "POW.VN", "SAB.VN",
    "SHB.VN", "SSB.VN", "SSI.VN", "STB.VN", "TCB.VN", "TPB.VN", "VCB.VN", "VHM.VN",
    "VIB.VN", "VIC.VN", "VJC.VN", "VNM.VN", "VPB.VN", "VRE.VN",
    # Chứng khoán & Thép & BĐS hot
    "VND.VN", "VCI.VN", "HCM.VN", "VIX.VN", "FTS.VN", "BSI.VN",
    "HSG.VN", "NKG.VN", "DGC.VN", "NVL.VN", "PDR.VN", "DIG.VN", "DXG.VN"
]

# ==============================
# LẤY DỮ LIỆU INDEX (VN-INDEX)
# ==============================
def get_index_data():
    """Lấy trạng thái chung của thị trường (VN-Index)"""
    try:
        idx = yf.Ticker("^VNINDEX.VN") # Một số API dùng mã này
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
# LẤY TOP TĂNG/GIẢM (OPTIMIZED BATCH)
# ==============================
def get_top_stocks(limit=5):
    results = []
    print(f"📊 Đang quét dữ liệu thị trường ({len(VNINDEX_ALL)} mã)...")
    
    try:
        # Tải batch dữ liệu 2 ngày gần nhất
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
                # Xử lý trường hợp yf.download trả về dữ liệu rỗng hoặc lỗi mã
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
    # Lọc bỏ các mã không có biến động (0.0) để dữ liệu AI 'đậm đà' hơn
    df_res = df_res[df_res["change"] != 0]
    
    gainers = df_res.sort_values("change", ascending=False).head(limit)
    losers = df_res.sort_values("change", ascending=True).head(limit)

    return list(zip(gainers["symbol"], gainers["change"])), \
           list(zip(losers["symbol"], losers["change"]))

# ==============================
# HÀM CHÍNH CHO PIPELINE
# ==============================
def get_market_data():
    """
    Kết hợp Index và Stock data để cung cấp context đầy đủ nhất cho AI.
    """
    try:
        index_info = get_index_data()
        gainers, losers = get_top_stocks(limit=5)
        
        # Tạo văn bản chất lượng cho AI Scripting
        # Ví dụ: 'SSI tăng 3.5%, HPG tăng 2.1%'
        gain_text = ", ".join([f"{m} tăng {c}%" for m, c in gainers]) if gainers else "không có mã tăng nổi bật"
        lose_text = ", ".join([f"{m} giảm {c}%" for m, c in losers]) if losers else "không có mã giảm sâu"

        # Tổng hợp câu thông báo thị trường chung
        market_status = f"VN-Index hiện ở mức {index_info['point']} điểm, {index_info['status']} {abs(index_info['change'])} điểm, tương đương {abs(index_info['pct'])}%."

        return {
            "index_summary": market_status, # Dùng cái này cho Hook của AI
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
    print("\n🚀 TOP TĂNG:", data["gain_text"])
    print("📉 TOP GIẢM:", data["lose_text"])
