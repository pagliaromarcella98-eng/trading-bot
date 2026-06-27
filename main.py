import MetaTrader5 as mt5
import pandas as pd
import requests
import time

# =====================
# CONFIG
# =====================
SYMBOLS = ["XAUUSD", "BTCUSD"]
TIMEFRAME = mt5.TIMEFRAME_M5
BARS = 200

TELEGRAM_TOKEN = "7701307731:AAHxfIEeJOZhy3M86WEcgo5jSpOjc7jmpAs"
TELEGRAM_CHAT_ID = "404088203"

last_signal = {}

# =====================
# TELEGRAM
# =====================
def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    except:
        pass

# =====================
# MT5 INIT
# =====================
def init():
    if not mt5.initialize():
        print("MT5 init failed")
        quit()

# =====================
# DATA
# =====================
def get_data(symbol):
    rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, BARS)
    df = pd.DataFrame(rates)

    if df.empty:
        return df

    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df

# =====================
# INDICATORS
# =====================
def ema(series, n):
    return series.ewm(span=n, adjust=False).mean()

def atr(df, n=14):
    return (df["high"] - df["low"]).rolling(n).mean()

# =====================
# STRATEGY
# =====================
def analyze(df):
    price = df["close"].iloc[-1]

    ema50 = ema(df["close"], 50)
    ema200 = ema(df["close"], 200)
    a = atr(df).iloc[-1]

    if pd.isna(a):
        return None

    if ema50.iloc[-1] > ema200.iloc[-1]:
        return ("BUY", price, price - a*1.5, price + a*3)

    if ema50.iloc[-1] < ema200.iloc[-1]:
        return ("SELL", price, price + a*1.5, price - a*3)

    return None

# =====================
# LOOP
# =====================
def run():
    init()
    print("🚀 MT5 PRO CLEAN BOT AVVIATO")

    while True:
        try:
            for sym in SYMBOLS:

                df = get_data(sym)

                if df.empty or len(df) < 100:
                    continue

                result = analyze(df)

                if result:
                    signal, entry, sl, tp = result

                    if last_signal.get(sym) != signal:
                        msg = f"""
📊 {sym} (MT5 REAL)

SIGNAL: {signal}
ENTRY: {round(entry,2)}
SL: {round(sl,2)}
TP: {round(tp,2)}
"""
                        print(msg)
                        send(msg)
                        last_signal[sym] = signal

            time.sleep(60)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(5)

if __name__ == "__main__":
    run()