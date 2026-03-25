# ==============================
# REAL MARKET DATA - VNINDEX
# ==============================

from datetime import datetime
import time


# ==============================
# GET VNINDEX DATA (SAFE + REALTIME)
# ==============================
def get_vnindex(retry=3):
    """
    Lấy dữ liệu VN-Index mới nhất
    Có retry + fallback → không crash pipeline
    """

    for attempt in range(retry):
        try:
            # 🔥 import bên trong để tránh lỗi môi trường
            from vnstock import Vnstock

            # 🔥 ngày hiện tại (dynamic)
            today = datetime.now().strftime("%Y-%m-%d")

            # 🔥 init API
            stock = Vnstock().stock(symbol="VNINDEX", source="VCI")

            # 🔥 lấy dữ liệu lịch sử
            df = stock.quote.history(
                start="2024-01-01",
                end=today,
                interval="1D"
            )

            # 🔥 check dữ liệu
            if df is None or df.empty:
                raise Exception("Data rỗng")

            latest = df.iloc[-1]

            close = float(latest["close"])
            open_price = float(latest["open"])
            volume = int(latest["volume"])

            change = round(close - open_price, 2)
            change_pct = round((change / open_price) * 100, 2)

            print(f"📊 VNINDEX: {close} ({change} | {change_pct}%)")

            return {
                "close": round(close, 2),
                "change": change,
                "change_pct": change_pct,
                "volume": volume
            }

        except Exception as e:
            print(f"⚠️ Lỗi lấy data (lần {attempt+1}):", e)
            time.sleep(2)

    # ==============================
    # FALLBACK (KHÔNG CRASH)
    # ==============================
    print("❌ Không lấy được dữ liệu VNINDEX → dùng fallback")

    return {
        "close": "N/A",
        "change": "N/A",
        "change_pct": "N/A",
        "volume": "N/A"
    }
