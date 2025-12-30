import time
import random
import httpx

# Subreddits that frequently contain meme-y crypto content
SUBREDDITS = [
    "CryptoCurrencyMemes",
    "cryptomemes",
    "CryptoCurrency",
]

# In-memory cache (process-local)
_CACHE = {
    "fetched_at": 0.0,
    "posts": [],  # list[dict]
}

CACHE_TTL_SECONDS = 600  # 10 minutes

def _is_image_url(url: str) -> bool:
    u = (url or "").lower()
    return u.endswith(".jpg") or u.endswith(".jpeg") or u.endswith(".png") or u.endswith(".gif")

async def _fetch_posts() -> list[dict]:
    # pick a subreddit randomly to vary content
    sub = random.choice(SUBREDDITS)
    url = f"https://www.reddit.com/r/{sub}/hot.json?limit=50"

    headers = {
        # Reddit wants a meaningful UA; keep it simple
        "User-Agent": "AI-Crypto-Advisor/1.0 (coding task; contact: none)",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()
        data = r.json()

    children = (data.get("data") or {}).get("children") or []
    posts = []

    for c in children:
        d = (c.get("data") or {})
        title = d.get("title")
        permalink = d.get("permalink")
        post_url = d.get("url_overridden_by_dest") or d.get("url")
        is_nsfw = bool(d.get("over_18"))
        stickied = bool(d.get("stickied"))

        if stickied or is_nsfw:
            continue

        # prefer direct images, but also support reddit-hosted previews
        image_url = None

        if _is_image_url(post_url):
            image_url = post_url
        else:
            # Try preview image if present
            preview = (d.get("preview") or {}).get("images") or []
            if preview and isinstance(preview, list):
                src = (preview[0].get("source") or {}).get("url")
                if src:
                    # Reddit escapes &amp;
                    image_url = src.replace("&amp;", "&")

        if not image_url:
            continue

        posts.append({
            "title": title or "Crypto meme",
            "image_url": image_url,
            "post_url": f"https://www.reddit.com{permalink}" if permalink else None,
            "subreddit": f"r/{d.get('subreddit')}" if d.get("subreddit") else f"r/{sub}",
            "source": "reddit",
        })

    return posts

async def get_random_meme() -> dict:
    now = time.time()

    # refresh cache if needed
    if (now - _CACHE["fetched_at"] > CACHE_TTL_SECONDS) or (not _CACHE["posts"]):
        try:
            _CACHE["posts"] = await _fetch_posts()
            _CACHE["fetched_at"] = now
        except Exception:
            # Don't break dashboard if Reddit blocks/rate-limits temporarily
            if _CACHE["posts"]:
                # fallback to last cached
                pass
            else:
                return {
                    "title": "Meme unavailable (Reddit fetch failed)",
                    "image_url": None,
                    "post_url": None,
                    "subreddit": None,
                    "source": "reddit",
                }

    return random.choice(_CACHE["posts"])
