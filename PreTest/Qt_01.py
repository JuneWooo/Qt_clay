# coding:utf-8

import requests
import json
import base64
import hmac
import hashlib
import datetime
import time

base_url = 'https://api.sandbox.gemini.com'
endpoint = '/v1/order/new'
url = base_url + endpoint

gemini_api_key = "account-t42SsogOoFUkGDXV9dka"
gemini_api_secret = "3DjirJRLL2TGmn5niFEWP5dnaQ5d".encode()

ct = datetime.datetime.now()
payload_nonce = str(int(time.mktime(ct.timetuple())*1000))

# 订单的具体信息
payload = {
    'request': "/v1/order/new",
    'nonce': payload_nonce,
    'symbol': "btcusd",
    'amount': "5",
    'price': "3633.00",
    'side': "buy",
    'type': "exchange limit",
    "options": ["maker-or-cancel"]
}

# 加密内容
encode_payload = json.dumps(payload).encode()
b64 = base64.b64encode(encode_payload)
signature = hmac.new(gemini_api_secret, b64, hashlib.sha384).hexdigest()

# 构造请求头
request_headers = {
    'Content-Type': "text/plain",
    'Content-Lenght': "0",
    'X-GEMINI-APIKEY': gemini_api_key,
    'X-GEMINI-PAYLOAD': b64,
    'X-GEMINI-SIGNATURE': signature,
    'Cache-Control': 'no-cache'
}

resp = requests.post(url, data=None, headers=request_headers)

new_order = resp.json()
print(new_order)