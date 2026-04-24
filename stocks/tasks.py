import os
import json
import time
import requests
import redis

from celery import shared_task
from django.conf import settings

# =========================
# 🔧 CONFIG
# =========================

REDIS_URL = os.environ.get("REDIS_URL")
r = redis.from_url(REDIS_URL, decode_responses=True)

# Cache TTL (seconds)
CACHE_TTL = 10

# Lock config
LOCK_KEY = "stocks_update_lock"
LOCK_EXPIRE = 12  # seconds

# Example stock symbols (edit as needed)
SYMBOLS = ["AAPL", "TSLA", "MSFT"]

# Finnhub example endpoint (replace with your API)
API_URL = "https://finnhub.io/api/v1/quote"
API_KEY = os.environ.get("FINNHUB_API_KEY")


# =========================
# 🔐 LOCKING (PREVENT DUPLICATES)
# =========================

def acquire_lock():
    return r.set(LOCK_KEY, "1", nx=True, ex=LOCK_EXPIRE)

def release_lock():
    r.delete(LOCK_KEY)


# =========================
# 📦 FETCH STOCK DATA (WITH CACHE)
# =========================

def fetch_stock(symbol):
    """Fetch a single stock from API"""
    response = requests.get(API_URL, params={
        "symbol": symbol,
        "token": API_KEY
    }, timeout=5)

    response.raise_for_status()
    return response.json()


def get_stock_data(symbols):
    """
    Fetch stock data with caching.
    Avoids repeated API calls within TTL.
    """
    cache_key = f"stocks:{','.join(symbols)}"

    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # 🔥 Fetch fresh data
    data = {}
    for symbol in symbols:
        try:
            data[symbol] = fetch_stock(symbol)
            time.sleep(0.2)  # small delay to avoid burst limits
        except Exception as e:
            data[symbol] = {"error": str(e)}

    # Store in Redis cache
    r.setex(cache_key, CACHE_TTL, json.dumps(data))

    return data


# =========================
# 📡 OPTIONAL: SEND TO WEBSOCKETS
# =========================

def broadcast_to_clients(data):
    """
    Send data to WebSocket clients (Django Channels)
    """
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            "stocks_group",
            {
                "type": "send_stock_update",
                "data": data
            }
        )
    except Exception as e:
        print("WebSocket broadcast failed:", e)


# =========================
# 🚀 MAIN CELERY TASK
# =========================

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 5},
)
def update_stocks(self):
    """
    Main task:
    - Prevent duplicates (lock)
    - Use cache
    - Fetch stock data
    - Broadcast to frontend
    """

    if not acquire_lock():
        print("Another worker is already running this task.")
        return

    try:
        print("Fetching stock data...")

        data = get_stock_data(SYMBOLS)

        # Debug log
        print("Stock data:", data)

        # Broadcast to WebSocket clients
        broadcast_to_clients(data)

        return data

    finally:
        release_lock()
