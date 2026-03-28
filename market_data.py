# ==============================
# MARKET DATA (FAST BATCH PROCESSING)
# ==============================

import yfinance as yf
import pandas as pd
import time

# ==============================
# DANH SÁCH MÃ VN-INDEX (HOSE)
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
    "NVL.VN", "PDR.VN", "DIG.VN", "DXG.VN", "NLG.VN", "KDH.VN", "KBC.VN", "ITA.VN",
    "SZC.VN", "VGC.VN", "TCH.VN", "HDC.VN", "CII.VN", "HHV.VN", "LCG.VN", "VCG.VN", "CTD.VN",

    # Nhóm Thép - Sản xuất - Năng lượng
    "HSG.VN", "NKG.VN", "DGC.VN", "CSV.VN", "DCM.VN", "DPM.VN", "PVD.VN", "PVT.VN", 
    "PVS.VN", "REE.VN", "HDG.VN", "NT2.VN", "FRT.VN", "DGW.VN", "PNJ.VN", "GMD.VN", "VHC.VN"
]

# ==============================
# SAFE DOWNLOAD (CHO TỪNG MÃ RIÊNG LẺ)
# ==============================
def safe_download(ticker):
    """Fallback nếu tải batch bị lỗi"""
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="3d") # Lấy 3 ngày để chắc chắn có đủ dữ liệu so sánh
        if df is None or len(df) < 2:
            return None
        return df
    except:
        return None

# ==============================
# LẤY TOP TĂNG/GIẢM (TỐI ƯU TỐC ĐỘ)
# ==============================
def get_top_stocks(limit=5):
    results = []
    
    print(f"📊 Đang tải dữ liệu {len(VNINDEX_ALL)} mã cổ phiếu...")
    
    try:
        # Tải toàn bộ danh sách trong 1 request (Batch)
        raw = yf.download(
            tickers=VNINDEX_ALL,
            period="3d",
            group_by="ticker",
            auto_adjust=True,
            threads=True,
            progress=False
        )

        for s in VNINDEX_ALL:
            try:
                # Xử lý dữ liệu từ MultiIndex DataFrame
                df = raw[s].dropna()
                
                if len(df) < 2:
                    continue

                last_price = df["Close"].iloc[-1]
                prev_price = df["Close"].iloc[-2]

                if prev_price == 0: continue
                
                pct_change = (last_price - prev_price) / prev_price * 100

                results.append({
                    "symbol": s.replace(".VN", ""),
                    "change": round(pct_change, 2),
                    "price": round(last_price, 2)
                })
            except:
                continue

    except Exception as e:
        print(f"⚠️ Batch download gặp sự cố: {e}. Đang chuyển sang chế độ tải từng mã...")

    # --- FALLBACK: Nếu batch download không có kết quả ---
    if not results:
        for s in VNINDEX_ALL:
            df = safe_download(s)
            if df is not None:
                try:
                    last_price = df["Close"].iloc[-1]
                    prev_price = df["Close"].iloc[-2]
                    pct_change = (last_price - prev_price) / prev_price * 100
                    results.append({
                        "symbol": s.replace(".VN", ""),
                        "change": round(pct_change, 2),
                        "price": round(last_price, 2)
                    })
                except: continue
            time.sleep(0.01)

    if not results:
        return [], []

    # Chuyển thành DataFrame để sắp xếp
    df_res = pd.DataFrame(results)
    
    # Lấy Top tăng và Top giảm
    gainers = df_res.sort_values("change", ascending=False).head(limit)
    losers = df_res.sort_values("change", ascending=True).head(limit)

    # Convert sang format list tuple cho dễ đọc: [('Mã', %_tăng), ...]
    gainers_list = list(zip(gainers["symbol"], gainers["change"]))
    losers_list = list(zip(losers["symbol"], losers["change"]))

    return gainers_list, losers_list

# ==============================
# HÀM CHÍNH ĐỂ PIPELINE GỌI
# ==============================
def get_market_data():
    """
    Trả về dictionary chứa dữ liệu thị trường.
    Cấu trúc được giữ nguyên để không làm crash các bước sau trong pipeline.
    """
    try:
        gainers, losers = get_top_stocks(limit=5)
        
        # Format lại chuỗi văn bản để AI dễ đọc
        gain_text = ", ".join([f"{m} tăng {c}%" for m, c in gainers])
        lose_text = ", ".join([f"{m} giảm {c}%" for m, c in losers])

        return {
            "vnindex": {},           # Chỗ trống cho dữ liệu Index nếu cần sau này
            "gainers": gainers,      # Dạng list tuple để render video
            "losers": losers,        # Dạng list tuple để render video
            "gain_text": gain_text,  # Dạng chuỗi để AI viết script
            "lose_text": lose_text   # Dạng chuỗi để AI viết script
        }
    except Exception as e:
        print(f"❌ Lỗi nghiêm trọng tại market_data: {e}")
        return {
            "vnindex": {},
            "gainers": [],
            "losers": [],
            "gain_text": "Không có dữ liệu",
            "lose_text": "Không có dữ liệu"
        }

# --- TEST ---
if __name__ == "__main__":
    data = get_market_data()
    print("Top tăng:", data["gain_text"])
    print("Top giảm:", data["lose_text"])
