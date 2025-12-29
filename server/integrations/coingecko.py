import httpx
import os

BASE_URL = os.getenv("COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3")

# Map symbols to CoinGecko IDs (extend later if needed)
SYMBOL_TO_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "BNB": "binancecoin",
    "AVAX": "avalanche-2",
    "ADA": "cardano",
}

async def fetch_prices_usd(symbols: list[str]) -> dict:
    ids = [SYMBOL_TO_ID[s] for s in symbols if s in SYMBOL_TO_ID]
    if not ids:
        return {"note": "No supported assets selected", "prices_usd": {}}

    url = f"{BASE_URL}/simple/price"
    params = {"ids": ",".join(ids), "vs_currencies": "usd"}

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    # Convert back to symbols for your UI
    prices = {}
    for sym in symbols:
        cid = SYMBOL_TO_ID.get(sym)
        if cid and cid in data and "usd" in data[cid]:
            prices[sym] = data[cid]["usd"]

    return {"prices_usd": prices, "source": "coingecko"}
