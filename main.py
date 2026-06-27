import yfinance as yf
import pandas as pd
import requests
import time

# =========================
# CONFIG
# =========================
SYMBOLS = ["XAUUSD=X", "BTC-USD"]
INTERVAL = "5m"
PERIOD = "5d"

TELEGRAM_TOKEN = "7701307731:AAHxfIEeJOZhy3M86WEcgo5jSpOjc7jmpAs"
TELEGRAM_CHAT_ID = "404088203"

last_signal = {}

# =========================
# TELEGRAM
# =========================
def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    except:
        pass

# =========================
# INDICATORS
# =========================
def ema(series, n):
    return series.ewm(span=n, adjust=False).mean()

def atr(df, n=14):
    high_low = df["High"] - df["Low"]
    return high_low.rolling(n).mean()

# =========================
# STRATEGY
# =========================
def analyze(df):
    df = df.dropna()

    price = df["Close"].iloc[-1]

    ema50 = ema(df["Close"], 50)
    ema200 = ema(df["Close"], 200)
    a = atr(df).iloc[-1]

    trend_up = ema50.iloc[-1] > ema200.iloc[-1]
    trend_down = ema50.iloc[-1] < ema200.iloc[-1]

    # filtro volatilità (evita mercato morto)
    if a is None or a == 0:
        return None

    # BUY
    if trend_up:
        sl = price - (a * 1.5)
        tp = price + (a * 3)

        return ("BUY", price, sl, tp)

    # SELL
    if trend_down:
        sl = price + (a * 1.5)
        tp = price - (a * 3)

        return ("SELL", price, sl, tp)

    return None

# =========================
# LOOP
# =========================
def run():
    print("🚀 PRO TRADING BOT AVVIATO")

    while True:
        try:
            for sym in SYMBOLS:

                df = yf.download(sym, interval=INTERVAL, period=PERIOD, progress=False)

                # fix colonne multi-index
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)

                if len(df) < 100:
                    continue

                result = analyze(df)

                if result:
                    signal, entry, sl, tp = result

                    if last_signal.get(sym) != signal:
                        msg = f"""
📊 {sym}

SIGNAL: {signal}

ENTRY: {round(entry, 2)}
SL: {round(sl, 2)}
TP: {round(tp, 2)}
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