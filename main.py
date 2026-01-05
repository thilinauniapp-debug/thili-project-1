import ccxt
import pandas as pd
import time
import requests
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread
import os

# --- 1. RENDER එක සඳහා පොඩි සර්වර් එකක් ---
app = Flask('')

@app.route('/')
def home():
    return "Thili Project 1 is Running 24/7!"

def run_web_server():
    # Render සාමාන්‍යයෙන් පාවිච්චි කරන්නේ Port 10000 හෝ 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. ඔයාගේ ප්‍රධාන බොට් කේතය (MAIN BOT CODE) ---
exchange = ccxt.kraken()
sri_lanka_tz = pytz.timezone('Asia/Colombo')

TELEGRAM_TOKEN = 'ඔයාගේ_TOKEN_එක_මෙතනට'
CHAT_ID = 'ඔයාගේ_CHAT_ID_එක_මෙතනට'
symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'LINK/USDT']

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=Markdown&disable_web_page_preview=false"
    try: requests.get(url)
    except: pass

def get_advanced_data(symbol, timeframe):
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=50)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['vol_ma'] = df['volume'].rolling(window=20).mean()
        df['ratio'] = df['volume'] / df['vol_ma']
        df['delta'] = df.apply(lambda x: x['volume'] if x['close'] > x['open'] else -x['volume'], axis=1)
        df['cvd'] = df['delta'].cumsum()
        last = df.iloc[-1]
        prev = df.iloc[-2]
        direction = "Buy 🟢" if last['close'] > last['open'] else "Sell 🔴"
        trap = "Safe ✅"
        if last['close'] > prev['close'] and last['cvd'] < prev['cvd']:
            trap = "⚠️ FAKE PUMP (Trap)"
        elif last['close'] < prev['close'] and last['cvd'] > prev['cvd']:
            trap = "⚠️ FAKE DUMP (Trap)"
        return last['ratio'], last['close'], trap, direction
    except:
        return 0, 0, "Error", "None"

def monitor_market():
    print("Market Monitoring Started...")
    send_telegram_msg("🚀 *Thili Project 1 (Server Mode) ආරම්භ විය!*")
    while True:
        try:
            for symbol in symbols:
                ratio_1h, price, trap_1h, side_1h = get_advanced_data(symbol, '1h')
                if ratio_1h > 0.01:
                    ratio_5m, _, trap_5m, side_5m = get_advanced_data(symbol, '5m')
                    if ratio_5m > 0.01:
                        time_now = datetime.now(sri_lanka_tz).strftime('%I:%M %p')
                        msg = (f"🚨 *ADVANCED WHALE ALERT* 🚨\n\n"
                               f"💎 *කාසිය:* {symbol}\n"
                               f"📈 *ක්‍රියාව:* {side_1h}\n"
                               f"💰 *මිල:* ${price}\n"
                               f"📊 *1h Ratio:* {ratio_1h:.2f}x\n"
                               f"🛡️ *CVD Status:* {trap_1h}\n"
                               f"⏰ *වේලාව:* {time_now}")
                        send_telegram_msg(msg)
            time.sleep(120)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

# --- 3. බොට් සහ සර්වර් එකවර ක්‍රියාත්මක කිරීම ---
if __name__ == "__main__":
    # බොට් එක වෙනම "නූලක" (Thread) රන් කිරීම
    bot_thread = Thread(target=monitor_market)
    bot_thread.start()
    
    # Flask සර්වර් එක ප්‍රධාන නූලේ රන් කිරීම (Render එකට මෙය අවශ්‍ය වේ)
    run_web_server()
