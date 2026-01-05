import ccxt
import pandas as pd
import time
import requests
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread
import os

# --- 1. RENDER SERVER SETUP ---
app = Flask('')
@app.route('/')
def home(): return "Thili Project 1 (Top 50 + CVD) is Running Live!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. BOT LOGIC ---
exchange = ccxt.kraken()
sri_lanka_tz = pytz.timezone('Asia/Colombo')

TELEGRAM_TOKEN = '8332489688:AAEsjcVC2AHRVCeKMb6oBGddk1_1BwwZCX0'
CHAT_ID = '1164598763'

# ඔයා ඉල්ලපු Top 50 Coins ලැයිස්තුව
symbols = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 'DOT/USDT', 'LINK/USDT', 'DOGE/USDT', 'MATIC/USDT', 'SHIB/USDT',
    'AVAX/USDT', 'LTC/USDT', 'TRX/USDT', 'UNI/USDT', 'ATOM/USDT', 'XLM/USDT', 'BCH/USDT', 'ETC/USDT', 'NEAR/USDT', 'FIL/USDT',
    'ICP/USDT', 'LDO/USDT', 'HBAR/USDT', 'APT/USDT', 'ARB/USDT', 'OP/USDT', 'GRT/USDT', 'AAVE/USDT', 'STX/USDT', 'QNT/USDT',
    'EGLD/USDT', 'THETA/USDT', 'FLOW/USDT', 'AXS/USDT', 'SAND/USDT', 'MANA/USDT', 'CHZ/USDT', 'EOS/USDT', 'KAVA/USDT', 'SNX/USDT',
    'IMX/USDT', 'FTM/USDT', 'ALGO/USDT', 'MKR/USDT', 'CRV/USDT', 'RNDR/USDT', 'INJ/USDT', 'MINA/USDT', 'GALA/USDT', 'PEPE/USDT'
]

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=Markdown"
    try: requests.get(url)
    except: pass

def get_advanced_signals(symbol):
    try:
        # 1h දත්ත ලබා ගැනීම
        bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=50)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        
        # 1. Whale Ratio
        df['vol_ma'] = df['volume'].rolling(window=20).mean()
        ratio = df['volume'].iloc[-1] / df['vol_ma'].iloc[-1]
        
        # 2. CVD (Cumulative Volume Delta) Logic
        # මිල ඉහළ යනවා නම් Volume එක ධන (+) ලෙසත්, මිල පහළ යනවා නම් සෘණ (-) ලෙසත් ගනී.
        df['delta'] = df.apply(lambda x: x['volume'] if x['close'] > x['open'] else -x['volume'], axis=1)
        df['cvd'] = df['delta'].cumsum()
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 3. Buy/Sell Direction
        side = "BUY 🟢" if last['close'] > last['open'] else "SELL 🔴"
        
        # 4. Trap Detection (Divergence)
        trap_status = "Safe ✅"
        if last['close'] > prev['close'] and last['cvd'] < prev['cvd']:
            trap_status = "⚠️ FAKE PUMP (CVD Divergence)"
        elif last['close'] < prev['close'] and last['cvd'] > prev['cvd']:
            trap_status = "⚠️ FAKE DUMP (CVD Divergence)"
            
        return ratio, last['close'], side, trap_status
    except:
        return 0, 0, "None", "Error"

def monitor_market():
    print("Whale Monitoring Started for Top 50 with Buy/Sell & CVD...")
    send_telegram_msg("🚀 *Thili Project 1 (Top 50 Mode) ආරම්භ විය!* \nBuy/Sell සහ Trap Detection සක්‍රීයයි.")
    
    while True:
        try:
            for symbol in symbols:
                ratio, price, side, trap = get_advanced_signals(symbol)
                
                # Whale Ratio 2.5 ට වැඩිනම් පමණක් ඇලර්ට් කරයි
                if ratio > 2.5:
                    time_now = datetime.now(sri_lanka_tz).strftime('%I:%M %p')
                    msg = (f"🚨 *WHALE SIGNAL DETECTED* 🚨\n\n"
                           f"💎 *කාසිය:* {symbol}\n"
                           f"🔥 *Action:* {side}\n"
                           f"💰 *මිල:* ${price}\n"
                           f"📊 *Whale Ratio:* {ratio:.2f}x\n"
                           f"🛡️ *CVD Status:* {trap}\n"
                           f"⏰ *වේලාව:* {time_now}\n\n"
                           f"🔗 [Chart](https://www.tradingview.com/chart/?symbol=KRAKEN:{symbol.replace('/','')})")
                    send_telegram_msg(msg)
                
                time.sleep(1.2) # API Limit වැළැක්වීමට
            
            time.sleep(300) # විනාඩි 5කට වරක් සම්පූර්ණ ලිස්ට් එකම පරීක්ෂා කරයි
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    t = Thread(target=monitor_market)
    t.start()
    run_web_server()
