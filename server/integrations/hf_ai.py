import os
import httpx

HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "openai/gpt-oss-120b:fastest")
HF_ROUTER_BASE = os.getenv("HF_ROUTER_BASE_URL", "https://router.huggingface.co/v1")


async def fetch_ai_insight(preferences: dict) -> dict:
    """
    Uses Hugging Face Inference Providers OpenAI-compatible endpoint.
    Endpoint: POST {HF_ROUTER_BASE}/chat/completions
    """
    if not HF_TOKEN:
        return {
            "text": "AI insight unavailable (missing Hugging Face token).",
            "source": "huggingface",
        }

    assets = preferences.get("assets", [])
    investor_type = preferences.get("investor_type", "crypto investor")
    content_types = preferences.get("content_types", [])

    prompt = (
        "Write ONE short daily crypto insight (2-4 sentences). "
        "Be practical and NOT financial advice. "
        f"User type: {investor_type}. "
        f"Interested assets: {', '.join(assets) if assets else 'general crypto'}. "
        f"Preferred content: {', '.join(content_types) if content_types else 'market news'}. "
        "Include one simple risk-management tip."
    )

    url = f"{HF_ROUTER_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
    }
    body = {
        "model": HF_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 180,
    }

    try:
        async with httpx.AsyncClient(timeout=45) as client:
            r = await client.post(url, headers=headers, json=body)
            r.raise_for_status()
            data = r.json()

        text = (
            (data.get("choices") or [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        text = (text or "").strip()
        if not text:
            return {
                "text": "AI insight unavailable (empty response).",
                "source": "huggingface",
                "model": HF_MODEL,
            }

        return {"text": text, "source": "huggingface", "model": HF_MODEL}

    except httpx.HTTPStatusError as e:
        # return a short error string inside payload to debug without crashing dashboard
        details = e.response.text[:500]
        return {
            "text": "AI insight unavailable (provider error).",
            "source": "huggingface",
            "model": HF_MODEL,
            "error": f"{e.response.status_code}: {details}",
        }
    except Exception as e:
        return {
            "text": "AI insight unavailable (provider error).",
            "source": "huggingface",
            "model": HF_MODEL,
            "error": str(e)[:200],
        }
