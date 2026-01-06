import ccxt
import pandas as pd
import time
import requests
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread
import os

# --- 1. RENDER SERVER (බොට්ව පණපිටින් තබා ගැනීමට) ---
app = Flask('')

@app.route('/')
def home():
    return "Thili Project 1 (Triple TF Mode) is Running Live!"

def run_web_server():
    # Render මගින් ලබාදෙන Port එක ලබා ගැනීම
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. BOT LOGIC ---
exchange = ccxt.kraken()
sri_lanka_tz = pytz.timezone('Asia/Colombo')

TELEGRAM_TOKEN = '8332489688:AAEsjcVC2AHRVCeKMb6oBGddk1_1BwwZCX0'
CHAT_ID = '1164598763'

# ඔයා තීරණය කළ කාසි 50 ලැයිස්තුව
symbols = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 'DOT/USDT', 'LINK/USDT', 'DOGE/USDT', 'MATIC/USDT', 'SHIB/USDT',
    'AVAX/USDT', 'LTC/USDT', 'TRX/USDT', 'UNI/USDT', 'ATOM/USDT', 'XLM/USDT', 'BCH/USDT', 'ETC/USDT', 'NEAR/USDT', 'FIL/USDT',
    'ICP/USDT', 'LDO/USDT', 'HBAR/USDT', 'APT/USDT', 'ARB/USDT', 'OP/USDT', 'GRT/USDT', 'AAVE/USDT', 'STX/USDT', 'QNT/USDT',
    'EGLD/USDT', 'THETA/USDT', 'FLOW/USDT', 'AXS/USDT', 'SAND/USDT', 'MANA/USDT', 'CHZ/USDT', 'EOS/USDT', 'KAVA/USDT', 'SNX/USDT',
    'IMX/USDT', 'FTM/USDT', 'ALGO/USDT', 'MKR/USDT', 'CRV/USDT', 'RNDR/USDT', 'INJ/USDT', 'MINA/USDT', 'GALA/USDT', 'PEPE/USDT'
]

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&parse_mode=Markdown"
    try:
        requests.get(url)
    except:
        pass

def get_volume_data(symbol, timeframe):
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=30)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df['vol_ma'] = df['volume'].rolling(window=20).mean()
        last_row = df.iloc[-1]
        ratio = last_row['volume'] / last_row['vol_ma']
        side = "Buy" if last_row['close'] > last_row['open'] else "Sell"
        return ratio, last_row['close'], side
    except:
        return 0, 0, "None"

def monitor_market():
    print("Whale Monitoring Started (Triple TF Mode)...")
    send_telegram_msg("Thili Project 1: Triple Confirmation Mode Started!")
    
    while True:
        try:
            for symbol in symbols:
                # 1. 4H පරීක්ෂාව
                ratio_4h, price, side_4h = get_volume_data(symbol, '4h')
                
                if ratio_4h > 2.0:
                    # 2. 1H තහවුරු කිරීම
                    ratio_1h, _, side_1h = get_volume_data(symbol, '1h')
                    
                    if ratio_1h > 1.8:
                        # 3. 5M තහවුරු කිරීම
                        ratio_5m, _, _ = get_volume_data(symbol, '5m')
                        
                        if ratio_5m > 1.5:
                            time_sl = datetime.now(sri_lanka_tz).strftime('%Y-%m-%d %I:%M %p')
                            
                            # Emoji ඉවත් කළ පිරිසිදු මැසේජ් එක
                            msg = (f"*EXTREME WHALE SIGNAL FROM RENDER*\n\n"
                                   f"*Coin:* {symbol}\n"
                                   f"*Trend (4H):* {side_4h}\n"
                                   f"*Price:* ${price}\n"
                                   f"*4H Ratio:* {ratio_4h:.2f}x\n"
                                   f"*1H Ratio:* {ratio_1h:.2f}x\n"
                                   f"*5M Ratio:* {ratio_5m:.2f}x\n"
                                   f"*Time:* {time_sl}\n\n"
                                   f"*Triple Confirmation Success!*")
                            
                            send_telegram_msg(msg)
                            print(f"Signal sent for {symbol}")
                
                # API Limit නොවීමට තත්පර 1ක විවේකයක්
                time.sleep(1)
            
            # සම්පූර්ණ ලිස්ට් එක පරීක්ෂා කර අවසන් වූ පසු විනාඩි 3ක විවේකයක්
            time.sleep(180)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

# --- 3. EXECUTION ---
if __name__ == "__main__":
    # බොට් එක වෙනම Thread එකක රන් කිරීම
    t = Thread(target=monitor_market)
    t.start()
    
    # සර්වර් එක ප්‍රධාන Thread එකේ රන් කිරීම
    run_web_server()
