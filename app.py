from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
from datetime import datetime

app = Flask(__name__)
CORS(app)

# REPLACE THESE WITH YOUR DARAJA KEYS FROM developer.safaricom.co.ke
CONSUMER_KEY = "YOUR_CONSUMER_KEY"
CONSUMER_SECRET = "YOUR_CONSUMER_SECRET"
SHORTCODE = "174379"  # Sandbox - use your Till for live
PASSKEY = "YOUR_PASSKEY"
CALLBACK_URL = "https://livehub.onrender.com/callback"

def get_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    return r.json().get('access_token')

@app.route('/pay', methods=['POST'])
def pay():
    data = request.json
    phone = data.get('phone')  # 254712345678
    amount = data.get('amount') # 150, 300, 500
    ref = data.get('creator', 'LiveHub')

    token = get_token()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode((SHORTCODE + PASSKEY + timestamp).encode()).decode()

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": ref,
        "TransactionDesc": f"Payment for {ref}"
    }
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    res = requests.post(url, json=payload, headers=headers)
    return jsonify(res.json())

@app.route('/callback', methods=['POST'])
def callback():
    print("CALLBACK RECEIVED:", request.json)
    # Here you would unlock the number/chat in your database
    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"})

@app.route('/')
def home():
    return "LiveHub M-Pesa API is running"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
