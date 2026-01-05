import ccxt
import pandas as pd
import time
import requests
from datetime import datetime
import pytz

# --- SETUP ---
exchange = ccxt.kraken()

# Kraken හි වැඩිම ගනුදෙනු සිදුවන ප්‍රධාන කාසි ලැයිස්තුව
symbols = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT',
    'DOT/USDT', 'DOGE/USDT', 'LTC/USDT', 'LINK/USDT', 'SHIB/USDT',
    'AVAX/USDT', 'BCH/USDT', 'NEAR/USDT', 'MATIC/USDT', 'PEPE/USDT'
]

# කාලරාමු (Fast Confirmation Mode)
tf_short = '5m'
tf_long = '1h'
sri_lanka_tz = pytz.timezone('Asia/Colombo')

# ඔයාගේ Telegram විස්තර
TELEGRAM_TOKEN = '8332489688:AAEsjcVC2AHRVCeKMb6oBGddk1_1BwwZCX0'
CHAT_ID = '1164598763'

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}&disable_web_page_preview=false"
    try:
        requests.get(url)
    except:
        pass

def get_volume_data(target_symbol, timeframe):
    try:
        bars = exchange.fetch_ohlcv(target_symbol, timeframe=timeframe, limit=30)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        vol_ma = df['volume'].rolling(window=20).mean()
        last_row = df.iloc[-1]
        ratio = last_row['volume'] / vol_ma.iloc[-1]
        side = "Buy" if last_row['close'] > last_row['open'] else "Sell"
        return ratio, side, last_row['close']
    except Exception as e:
        return 0, "None", 0

print(f"--- 🐋 THILI PROJECT 1: MULTI-COIN FAST MONITORING ---")
send_telegram_msg("🚀 Thili Project 1 (Fast Mode): සියලුම ප්‍රධාන කාසි සඳහා සජීවීව ආරම්භ විය!")

def monitor_market():
    for symbol in symbols:
        try:
            # 1. පැය 1ක ප්‍රධාන ට්‍රෙන්ඩ් එක බැලීම
            ratio_1h, side_1h, price = get_volume_data(symbol, tf_long)
            
            # 2. විනාඩි 5ක ක්ෂණික තහවුරු කිරීම බැලීම
            ratio_5m, side_5m, _ = get_volume_data(symbol, tf_short)

            # Confirmation: කාලරාමු දෙකේම Whale Ratio > 2.5 සහ එකම දිශාව
            if ratio_1h > 2.5 and ratio_5m > 2.5 and side_1h == side_5m:
                side_emoji = "Whale Buying 🟢" if side_1h == "Buy" else "Whale Selling 🔴"
                time_sl = datetime.now(sri_lanka_tz).strftime('%I:%M %p')
                
                # TradingView Link
                tv_symbol = symbol.replace('/', '')
                tv_link = f"https://www.tradingview.com/chart/?symbol=KRAKEN:{tv_symbol}"
                
                msg = (f"🚨 --- {symbol} FAST ALERT --- 🚨\n\n"
                       f"ක්‍රියාව: {side_emoji}\n"
                       f"මිල: ${price}\n"
                       f"1h Ratio: {ratio_1h:.2f}x\n"
                       f"5m Ratio: {ratio_5m:.2f}x\n"
                       f"චාට් එක: {tv_link}\n\n"
                       f"වේලාව: {time_sl}")
                
                send_telegram_msg(msg)
                print(f"Signal sent for {symbol} at {time_sl}")
            
            # API එකට බරක් නොවීමට තත්පර 1ක විරාමයක්
            time.sleep(1)

        except Exception as e:
            print(f"Error on {symbol}: {e}")

# සෑම විනාඩි 2කට වරක්ම සම්පූර්ණ ලිස්ට් එකම පරීක්ෂා කරයි
while True:
    monitor_market()
    current_time = datetime.now(sri_lanka_tz).strftime('%I:%M %p')
    print(f"සම්පූර්ණ පරීක්ෂාව අවසන්: {current_time}. විනාඩි 2කින් නැවත ආරම්භ වේ...")
    time.sleep(120)
