# course_pilot/courses/mpesa.py
import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
MPESA_ENV = "sandbox"  # or "production" later

def get_access_token():
    """
    Generate M-Pesa access token
    """
    if MPESA_ENV == "sandbox":
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    else:
        url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    r = requests.get(url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    token = r.json().get("access_token")
    return token

def stk_push(phone_number, amount, account_reference, transaction_desc):
    """
    Trigger an M-Pesa STK push
    """
    token = get_access_token()
    
    if MPESA_ENV == "sandbox":
        stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        business_short_code = "174379"  # sandbox shortcode
        passkey = os.getenv("MPESA_PASSKEY")  # from Safaricom sandbox
    else:
        stk_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        business_short_code = "YOUR_PROD_SHORTCODE"
        passkey = os.getenv("MPESA_PASSKEY")

    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password_str = f"{business_short_code}{passkey}{timestamp}"
    password = base64.b64encode(password_str.encode()).decode("utf-8")

    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": business_short_code,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://yourfrontend.com/mpesa/callback/",  # set later
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(stk_url, json=payload, headers=headers)
    return response.json()
