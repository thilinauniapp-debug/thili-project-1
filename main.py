import ccxt
import pandas as pd
import time
import requests
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread
import os

# --- FLASK SERVER FOR RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Thili Project 1 is Running Live!"

def run_web_server():
    # Render එකෙන් ලබාදෙන Port එක භාවිතා කිරීම
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT SETUP ---
exchange = ccxt.binance()
symbols = ['BTC/USDT', 'ETH/USDT']
timeframe = '1h'
sri_lanka_tz = pytz.timezone('Asia/Colombo')

TELEGRAM_TOKEN = '8296607302:AAHckjcz6zHYNFlgU0AarV1hqrgzarpCgFM'
CHAT_ID = '1164598763'

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
    try:
        requests.get(url)
    except Exception as e:
        print(f"Telegram Error: {e}")

def monitor_market():
    print("Checking Market...")
    for symbol in symbols:
        try:
            bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=50)
            df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
            
            df['vol_ma'] = df['volume'].rolling(window=20).mean()
            last_row = df.iloc[-1]
            
            vol_ratio = last_row['volume'] / last_row['vol_ma']
            price_move = (abs(last_row['close'] - last_row['open']) / last_row['open']) * 100

            if vol_ratio > 2.5 and price_move > 0.5:
                side = "Whale Buying 🟢" if last_row['close'] > last_row['open'] else "Whale Selling 🔴"
                time_sl = datetime.now(sri_lanka_tz).strftime('%Y-%m-%d %I:%M %p')
                
                msg = (f"🚨 --- WHALE ALERT ({symbol}) --- 🚨\n\n"
                       f"ක්‍රියාව: {side}\n"
                       f"මිල: ${last_row['close']}\n"
                       f"පරිමාව (Ratio): {vol_ratio:.2f}x\n"
                       f"වේලාව: {time_sl}")
                
                send_telegram_msg(msg)
                print(f"✅ Signal sent for {symbol}")

        except Exception as e:
            print(f"Error scanning {symbol}: {e}")
        time.sleep(1)

def bot_loop():
    send_telegram_msg("🚀 Thili Project 1 (BTC/ETH) Render මත ආරම්භ විය!")
    while True:
        monitor_market()
        time.sleep(300)

# --- START BOTH ---
if __name__ == "__main__":
    # වෙබ් සර්වර් එක වෙනම thread එකක පණ ගැන්වීම
    t = Thread(target=run_web_server)
    t.start()
    # බොට් එක ක්‍රියාත්මක කිරීම
    bot_loop()
