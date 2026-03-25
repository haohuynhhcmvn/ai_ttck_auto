# ==============================
# GET REALTIME STOCK DATA (VIETNAM)
# ==============================

from vnstock import *

def get_vnindex():
    try:
        df = stock_historical_data(
            symbol="VNINDEX",
            start_date="2024-01-01",
            end_date="2026-12-31",
            resolution="1D"
        )

        latest = df.iloc[-1]

        return {
            "close": round(latest["close"], 2),
            "change": round(latest["close"] - latest["open"], 2),
            "volume": int(latest["volume"])
        }

    except Exception as e:
        print("❌ Lỗi lấy data:", e)
        return None
