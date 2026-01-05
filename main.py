import ccxt
import pandas as pd
import time
import requests
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread
import os

# --- 1. RENDER සර්වර් එක (බොට්ව පණපිටින් තියාගැනීමට) ---
app = Flask('')

@app.route('/')
def home():
    return "Thili Project 1 (Multi-TF Mode) is Running Live!"

def run_web_server():
    # Render එකට අවශ්‍ය Port එක ලබා ගැනීම
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. 'thili project 1' ප්‍රධාන කේතය ---
exchange = ccxt.kraken()
sri_lanka_tz = pytz.timezone('Asia/Colombo')

# කරුණාකර ඔයාගේ නිවැරදි විස්තර මෙතනට ඇතුළත් කරන්න
TELEGRAM_TOKEN = '8332489688:AAEsjcVC2AHRVCeKMb6oBGddk1_1BwwZCX0'
CHAT_ID = '1164598763'

# පරීක්ෂා කරන කාසි වර්ග
symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'LINK/USDT', 'ADA/USDT']

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=Markdown"
    try:
        requests.get(url)
    except:
        pass

def get_volume_ratio(symbol, timeframe):
    try:
        # ඉටිපන්දම් (Candlesticks) 30ක් ලබා ගැනීම
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=30)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        
        # සාමාන්‍ය පරිමාව (Volume Moving Average) ගණනය කිරීම
        df['vol_ma'] = df['volume'].rolling(window=20).mean()
        
        last_vol = df['volume'].iloc[-1]
        last_ma = df['vol_ma'].iloc[-1]
        
        ratio = last_vol / last_ma
        return ratio, df['close'].iloc[-1]
    except:
        return 0, 0

def monitor_market():
    print("Whale Monitoring Started (Multi-TF)...")
    send_telegram_msg("🐋 *Thili Project 1: Whale Detector පණගැන්වුණා!* \n(1h සහ 5m දෙකම පරීක්ෂා කරයි)")
    
    while True:
        try:
            for symbol in symbols:
                # පියවර 1: පැයේ කාලරාමුව (1h) පරීක්ෂා කිරීම
                ratio_1h, price = get_volume_ratio(symbol, '1h')
                
                if ratio_1h > 2.5:
                    # පියවර 2: විනාඩි 5 කාලරාමුව (5m) පරීක්ෂා කිරීම
                    ratio_5m, _ = get_volume_ratio(symbol, '5m')
                    
                    # කාලරාමු දෙකම තහවුරු වුවහොත් පමණක් ඇලර්ට් කරයි
                    if ratio_5m > 2.0:
                        time_now = datetime.now(sri_lanka_tz).strftime('%I:%M %p')
                        msg = (f"🚨 *CONFIRMED WHALE MOVEMENT* 🚨\n\n"
                               f"💎 *කාසිය:* {symbol}\n"
                               f"💰 *මිල:* ${price}\n"
                               f"📊 *1h Volume Ratio:* {ratio_1h:.2f}x\n"
                               f"⚡ *5m Volume Ratio:* {ratio_5m:.2f}x\n"
                               f"⏰ *වේලාව:* {time_now}\n\n"
                               f"🔗 [TradingView Chart](https://www.tradingview.com/chart/?symbol=KRAKEN:{symbol.replace('/','')})")
                        
                        send_telegram_msg(msg)
            
            # API එකට විවේකයක් ලබා දීම සහ නැවත පරීක්ෂා කිරීම (විනාඩි 2කින්)
            time.sleep(120)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

# --- 3. බොට් පණගැන්වීම ---
if __name__ == "__main__":
    # බොට් ක්‍රියාවලිය වෙනම Thread එකක ආරම්භ කිරීම
    t = Thread(target=monitor_market)
    t.start()
    
    # සර්වර් එක ප්‍රධාන Thread එකේ ආරම්භ කිරීම (Render සඳහා අත්‍යවශ්‍යයි)
    run_web_server()
