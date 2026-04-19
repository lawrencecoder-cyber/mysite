import httpx
import os

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

BASE_URL = "https://finnhub.io/api/v1/quote"

async def fetch_stock(symbol):
    async with httpx.AsyncClient() as client:
        r = await client.get(BASE_URL, params={
            "symbol": symbol,
            "token": FINNHUB_API_KEY
        })
        return {symbol: r.json()}

async def fetch_multiple(symbols):
    results = {}
    async with httpx.AsyncClient() as client:
        tasks = [
            client.get(BASE_URL, params={
                "symbol": s,
                "token": FINNHUB_API_KEY
            }) for s in symbols
        ]

        responses = await asyncio.gather(*tasks)

        for s, r in zip(symbols, responses):
            results[s] = r.json()

    return results
