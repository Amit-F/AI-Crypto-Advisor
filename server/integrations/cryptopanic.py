import os
import httpx

BASE_URL = os.getenv(
    "CRYPTOPANIC_BASE_URL",
    "https://cryptopanic.com/api/developer/v2/posts/",
)
API_KEY = os.getenv("CRYPTOPANIC_API_KEY")


async def fetch_market_news(assets: list[str]) -> dict:
    if not API_KEY:
        return {
            "title": "Crypto news unavailable",
            "summary": "Missing CryptoPanic API key.",
            "source": "cryptopanic",
        }

    params = {
        "auth_token": API_KEY,
        "currencies": ",".join(assets),
        "kind": "news",
        "filter": "hot",
        "public": "true",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(BASE_URL, params=params)
        r.raise_for_status()
        data = r.json()

    results = data.get("results", [])
    if not results:
        return {
            "title": "No major crypto news today",
            "summary": "CryptoPanic returned no articles.",
            "source": "cryptopanic",
        }

    top = results[0]

    # print("cryptopanic top keys:", top.keys())
    # print("cryptopanic top sample:", top)

    slug = top.get("slug")
    post_id = top.get("id")

    # CryptoPanic web URL
    url = top.get("url")

    if url is not None:
        1 == 1
    elif slug:
        url = f"https://cryptopanic.com/news/?search={slug}%22/"
    elif post_id:
        url = f"https://cryptopanic.com/news/{post_id}/"
    # print(url)


    return {
        "title": top.get("title"),
        "summary": f"{top.get('source', {}).get('domain', '')} · {top.get('published_at', '')}",
        "url": url,
        "source": "cryptopanic",
    }
