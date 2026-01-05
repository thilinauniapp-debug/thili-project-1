import requests
import time
import os
from flask import Flask
from threading import Thread
from datetime import datetime
import pytz

# --- RENDER SERVER SETUP ---
app = Flask('')

@app.route('/')
def home():
    return "Testing 2: Bot is sending signals!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- TELEGRAM TESTING CONFIG ---
# ඔයාගේ TOKEN සහ CHAT ID එක නිවැරදිව මෙතනට දාන්න
TOKEN = '8332489688:AAEsjcVC2AHRVCeKMb6oBGddk1_1BwwZCX0'
CHAT_ID = '1164598763'
sri_lanka_tz = pytz.timezone('Asia/Colombo')

def send_test_msg():
    print("Testing 2 logic started...")
    while True:
        try:
            time_now = datetime.now(sri_lanka_tz).strftime('%I:%M:%p')
            msg = f"🛠️ *Testing 2:* බොට් සාර්ථකව වැඩ කරයි! \n⏰ වේලාව: {time_now}"
            
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=Markdown"
            response = requests.get(url)
            
            if response.status_code == 200:
                print(f"Message sent successfully at {time_now}")
            else:
                print(f"Failed to send message: {response.text}")
                
        except Exception as e:
            print(f"Error occurred: {e}")
            
        # විනාඩියෙන් විනාඩියට මැසේජ් එකක් එවන්න
        time.sleep(60)

if __name__ == "__main__":
    # මැසේජ් යවන කොටස වෙනම thread එකක රන් කිරීම
    t = Thread(target=send_test_msg)
    t.start()
    
    # සර්වර් එක පණගැන්වීම
    run_web_server()
