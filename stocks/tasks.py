from celery import shared_task
import asyncio
from .services import fetch_multiple
from .redis_pubsub import broadcast

SYMBOLS = ["AAPL", "TSLA", "EURUSD", "GBPUSD"]

@shared_task
def update_stocks():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    data = loop.run_until_complete(fetch_multiple(SYMBOLS))

    broadcast(data)
