import ccxt
import pandas as pd
import time
import requests
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread
import os

# --- RENDER SERVER SETUP ---
app = Flask('')
@app.route('/')
def home(): return "Thili Project 1 is Running 24/7!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT CONFIGURATION ---
exchange = ccxt.kraken()
sri_lanka_tz = pytz.timezone('Asia/Colombo')

# මෙතනට ඔයාගේ තොරතුරු දාන්න
TELEGRAM_TOKEN = 'ඔයාගේ_TOKEN_එක'
CHAT_ID = 'ඔයාගේ_CHAT_ID_එක'

symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'LINK/USDT', 'ADA/USDT', 'DOT/USDT']

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
        direction = "BUY 🟢" if last['close'] > last['open'] else "SELL 🔴"
        
        trap = "Safe ✅"
        if last['close'] > prev['close'] and last['cvd'] < prev['cvd']:
            trap = "⚠️ FAKE PUMP (Trap)"
        elif last['close'] < prev['close'] and last['cvd'] > prev['cvd']:
            trap = "⚠️ FAKE DUMP (Trap)"
            
        return last['ratio'], last['close'], trap, direction
    except:
        return 0, 0, "Error", "None"

def monitor_market():
    print("Whale Monitoring Started...")
    send_telegram_msg("🐋 *Thili Project 1: Whale Detector පණගැන්වුණා!* \nදැන් මම 24/7 මාර්කට් එක පරීක්ෂා කරනවා.")
    
    while True:
        try:
            for symbol in symbols:
                ratio_1h, price, trap_1h, side_1h = get_advanced_data(symbol, '1h')
                
                # Whale Ratio එක 2.0 ට වඩා වැඩි නම් පමණක් ඇලර්ට් එක එවනවා
                if ratio_1h > 2.0:
                    time_now = datetime.now(sri_lanka_tz).strftime('%I:%M %p')
                    msg = (f"🚨 *WHALE MOVEMENT DETECTED* 🚨\n\n"
                           f"💎 *Coin:* {symbol}\n"
                           f"📊 *Action:* {side_1h}\n"
                           f"💰 *Price:* ${price}\n"
                           f"📈 *Whale Ratio:* {ratio_1h:.2f}x\n"
                           f"🛡️ *CVD Status:* {trap_1h}\n"
                           f"⏰ *Time:* {time_now}\n\n"
                           f"🔗 [View Chart](https://www.tradingview.com/chart/?symbol=KRAKEN:{symbol.replace('/','')})")
                    send_telegram_msg(msg)
            
            time.sleep(120) # විනාඩි 2කට වරක් පරීක්ෂා කරයි
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    t = Thread(target=monitor_market)
    t.start()
    run_web_server()
