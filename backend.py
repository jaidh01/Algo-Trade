from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import pyotp
import threading
import time
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

# ===== CONFIG =====
# API_KEY = "g2DoeWJ2 "
# CLIENT_CODE = "K105156"
# MPIN = "3369"
# TOTP_SECRET = "YET4GAPXZTBBWE2RWZCK2RLZ6A"
API_KEY = os.getenv("X_API_KEY")
CLIENT_CODE = os.getenv("X_CLIENT_CODE")
MPIN = os.getenv("X_MPIN")
TOTP_SECRET = os.getenv("X_TOTP_SECRET")

# ===== GLOBAL STATE =====
live_data = {
    "NIFTY": None,
    "SENSEX": None
}
ws_started = False


def start_websocket():
    global live_data

    try:
        obj = SmartConnect(api_key=API_KEY)

        data = obj.generateSession(
            CLIENT_CODE,
            MPIN,
            pyotp.TOTP(TOTP_SECRET).now()
        )

        if not data or not data.get("status"):
            print("❌ Login Failed:", data)
            return

        authToken = data['data']['jwtToken']
        feedToken = obj.getfeedToken()

        sws = SmartWebSocketV2(authToken, API_KEY, CLIENT_CODE, feedToken)

        # ===== CALLBACKS =====
        def on_open(wsapp):
            print("✅ WebSocket Connected")

            token_list = [
                {
                    "exchangeType": 1,  # NSE
                    "tokens": ["99926000"]  # NIFTY
                },
                {
                    "exchangeType": 3,  # BSE
                    "tokens": ["99919000"]  # SENSEX
                }
            ]

            sws.subscribe("stream_1", 1, token_list)

        # def on_data(wsapp, message):
        #     global live_data
        #     print("RAW DATA:", message) 
        #     live_data = message

        def on_data(wsapp, message):
            global live_data

            token = message.get("token")

            if token == "99926000":
                live_data["NIFTY"] = message
            elif token == "99919000":
                live_data["SENSEX"] = message

        def on_error(wsapp, error):
            print("❌ WS Error:", error)

        def on_close(wsapp):
            print("🔴 WS Closed")

        sws.on_open = on_open
        sws.on_data = on_data
        sws.on_error = on_error
        sws.on_close = on_close

        sws.connect()

    except Exception as e:
        print("🔥 Exception:", e)

obj = None

def get_obj():
    global obj

    if obj is not None:
        return obj  # ✅ reuse existing session

    obj = SmartConnect(api_key=API_KEY)

    data = obj.generateSession(
        CLIENT_CODE,
        MPIN,
        pyotp.TOTP(TOTP_SECRET).now()
    )

    if not data or not data.get("status"):
        print("Login Failed")
        return None

    print("✅ Logged in once")

    return obj

# def get_obj():
#     global obj, session_created

#     if session_created:
#         return obj

#     obj = SmartConnect(api_key=API_KEY)

#     data = obj.generateSession(
#         CLIENT_CODE,
#         MPIN,
#         pyotp.TOTP(TOTP_SECRET).now()
#     )

#     if not data or not data.get("status"):
#         print("Login Failed")
#         return None

#     session_created = True
#     return obj

def get_last_trading_day():
    today = datetime.now()

    # Monday → go back to Friday
    if today.weekday() == 0:
        return today - timedelta(days=3)
    # Sunday → Friday
    elif today.weekday() == 6:
        return today - timedelta(days=2)
    # Saturday → Friday
    elif today.weekday() == 5:
        return today - timedelta(days=1)
    else:
        return today

# def fetch_candle_data():
#     obj = get_obj()
#     if not obj:
#         return []

#     try:
#         last_day = get_last_trading_day()

#         from_date = last_day.strftime("%Y-%m-%d") + " 09:15"
#         to_date = last_day.strftime("%Y-%m-%d") + " 15:35"

#         params = {
#             "exchange": "NSE",
#             "symboltoken": "99926000",
#             "tradingsymbol": "NIFTY",   # 🔥 ADD THIS
#             "interval": "ONE_MINUTE",
#             "fromdate": from_date,
#             "todate": to_date
#         }

#         data = obj.getCandleData(params)

#         print("API RESPONSE:", data)

#         if not data or not data.get("data"):
#             return []

#         return data["data"]

#     except Exception as e:
#         print("Error:", e)
#         return []


def fetch_candle_data(symbol, token, exchange):
    obj = get_obj()
    if not obj:
        return []

    last_day = get_last_trading_day()

    from_date = last_day.strftime("%Y-%m-%d") + " 09:15"
    to_date = last_day.strftime("%Y-%m-%d") + " 15:35"

    params = {
        "exchange": exchange,
        "symboltoken": token,
        "tradingsymbol": symbol,
        "interval": "ONE_MINUTE",
        "fromdate": from_date,
        "todate": to_date
    }

    data = obj.getCandleData(params)

    if not data or not data.get("data"):
        return []

    return data["data"]
    
def fetch_index_data():
    obj = get_obj()
    if not obj:
        return {}

    nifty = obj.ltpData("NSE", "NIFTY", "26000")
    banknifty = obj.ltpData("NSE", "BANKNIFTY", "26009")

    return {
        "NIFTY": nifty['data'],
        "BANKNIFTY": banknifty['data']
    }

def start_background():
    global ws_started

    if ws_started:
        return  # 🚀 prevents multiple threads + rate limit

    # thread = threading.Thread(target=start_websocket)
    # thread = threading.Thread(target=fetch_index_data)
    # thread.daemon = True
    # thread.start()

    ws_started = True

obj = None
session_created = False



# from SmartApi import SmartConnect
# from SmartApi.smartWebSocketV2 import SmartWebSocketV2
# import pyotp
# import threading

# # ===== GLOBAL STORE =====
# live_data = {}

# def start_websocket():

#     obj = SmartConnect(api_key=API_KEY)
#     data = obj.generateSession(
#         CLIENT_CODE,
#         PASSWORD,
#         pyotp.TOTP(TOTP_SECRET).now()
#     )

#     authToken = data['data']['jwtToken']
#     feedToken = obj.getfeedToken()

#     ws = SmartWebSocketV2(authToken, API_KEY, CLIENT_CODE, feedToken)

#     def on_open(ws):
#         print("Connected")

#         token_list = [
#             {
#                 "exchangeType": 1,
#                 "tokens": ["2885"]  # RELIANCE
#             }
#         ]

#         ws.subscribe("stream_1", 1, token_list)

#     def on_data(ws, message):
#         global live_data
#         live_data = message   # store latest tick

#     ws.on_open = on_open
#     ws.on_data = on_data

#     ws.connect()

# # Run in background thread
# def start_background():
#     thread = threading.Thread(target=start_websocket)
#     thread.daemon = True
#     thread.start()