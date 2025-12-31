import os
import httpx


def _get_cryptopanic_base_url() -> str:
    # Prefer Render env var if set, otherwise default.
    return os.getenv("CRYPTOPANIC_BASE_URL", "https://cryptopanic.com/api/developer/v2/posts/")


def _get_cryptopanic_api_key() -> str | None:
    return os.getenv("CRYPTOPANIC_API_KEY")


def _build_fallback_news(title: str, summary: str) -> dict:
    return {
        "title": title,
        "summary": summary,
        "source": "cryptopanic",
        "url": "https://cryptopanic.com/news/",
    }


def _cryptopanic_web_url_from_post(top: dict) -> str:
    """
    CryptoPanic developer endpoint does not always include a direct URL.
    We'll create a reasonable web link.
    """
    url = top.get("url")
    if url:
        return url

    slug = top.get("slug")
    post_id = top.get("id")
    title = (top.get("title") or "").strip()

    if post_id:
        # Often works even if not perfect; otherwise fallback to search.
        return f"https://cryptopanic.com/news/{post_id}/"
    if slug:
        return f"https://cryptopanic.com/news/?search={slug}"
    if title:
        # Safe, simple fallback: search by title
        return f"https://cryptopanic.com/news/?search={title}"

    return "https://cryptopanic.com/news/"


async def fetch_market_news(assets: list[str]) -> dict:
    api_key = _get_cryptopanic_api_key()
    if not api_key:
        return _build_fallback_news(
            "Crypto news unavailable",
            "Missing CryptoPanic API key.",
        )

    params = {
        "auth_token": api_key,
        "currencies": ",".join(assets) if assets else "",
        "kind": "news",
        "filter": "hot",
        "public": "true",
    }

    base_url = _get_cryptopanic_base_url()

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(base_url, params=params)
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPError:
        return _build_fallback_news(
            "Crypto news unavailable",
            "CryptoPanic request failed (network/provider error).",
        )

    results = data.get("results", [])
    if not results:
        return _build_fallback_news(
            "No major crypto news today",
            "CryptoPanic returned no articles.",
        )

    top = results[0]
    web_url = _cryptopanic_web_url_from_post(top)

    # Your previous summary used source.domain and published_at; keep that idea:
    domain = (top.get("source") or {}).get("domain", "")
    published_at = top.get("published_at", "")

    return {
        "title": top.get("title") or "Top crypto news",
        "summary": f"{domain} · {published_at}".strip(" ·"),
        "url": web_url,
        "source": "cryptopanic",
    }
