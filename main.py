import requests
import os
from flask import Flask
from threading import Thread

# --- Render සඳහා සර්වර් එක ---
app = Flask('')
@app.route('/')
def home(): return "Testing Bot..."

# --- මැසේජ් එක යවන කොටස ---
TOKEN = '8332489688:AAEsjcVC2AHRVCeKMb6oBGddk1_1BwwZCX0' # මෙය නිවැරදිදැයි බලන්න
CHAT_ID = '1164598763' # @userinfobot එකෙන් ගත් අංකය මෙතනට දාන්න

def send_test():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text=🚨 TEST: Render Server එකෙන් පණිවිඩය ලැබුණා! ✅"
    r = requests.get(url)
    print(r.json()) # මෙතනින් අපිට Error එක මොකක්ද කියලා Render Logs වල බලාගන්න පුළුවන්

if __name__ == "__main__":
    print("Test message යැවීමට උත්සාහ කරයි...")
    send_test()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
