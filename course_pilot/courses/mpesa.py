import requests
import base64
from datetime import datetime
import os

def get_access_token():
    consumer_key = os.getenv('MPESA_CONSUMER_KEY')
    consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
    
    if not consumer_key or not consumer_secret:
        raise Exception("M-Pesa credentials not configured")
    
    credentials = f"{consumer_key}:{consumer_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    headers = {"Authorization": f"Basic {encoded_credentials}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Failed to get access token: {response.text}")

def stk_push(phone, amount, account_reference, transaction_desc):
    try:
        access_token = get_access_token()
        shortcode = os.getenv('MPESA_BUSINESS_SHORTCODE', '174379')
        passkey = os.getenv('MPESA_PASSKEY')
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()
        
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": shortcode,
            "PhoneNumber": phone,
            "CallBackURL": os.getenv('MPESA_CALLBACK_URL', 'https://example.com/callback'),
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
        
    except Exception as e:
        return {"error": str(e)}