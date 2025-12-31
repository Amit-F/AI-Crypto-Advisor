import os
import httpx


def _get_hf_token() -> str | None:
    return os.getenv("HF_TOKEN")


def _get_hf_model() -> str:
    # You can override this in Render env vars if you want.
    return os.getenv("HF_MODEL", "openai/gpt-oss-120b:fastest")


def _get_hf_router_base() -> str:
    return os.getenv("HF_ROUTER_BASE_URL", "https://router.huggingface.co/v1")


async def fetch_ai_insight(preferences: dict) -> dict:
    """
    Uses Hugging Face Inference Providers OpenAI-compatible endpoint.
    Endpoint: POST {HF_ROUTER_BASE}/chat/completions
    """
    hf_token = _get_hf_token()
    hf_model = _get_hf_model()
    hf_router_base = _get_hf_router_base()

    if not hf_token:
        return {
            "text": "AI insight unavailable (missing Hugging Face token).",
            "source": "huggingface",
            "model": hf_model,
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

    url = f"{hf_router_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json",
    }
    body = {
        "model": hf_model,
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
                "model": hf_model,
            }

        return {"text": text, "source": "huggingface", "model": hf_model}

    except httpx.HTTPStatusError as e:
        details = (e.response.text or "")[:500]
        return {
            "text": "AI insight unavailable (provider error).",
            "source": "huggingface",
            "model": hf_model,
            "error": f"{e.response.status_code}: {details}",
        }
    except Exception as e:
        return {
            "text": "AI insight unavailable (provider error).",
            "source": "huggingface",
            "model": hf_model,
            "error": str(e)[:200],
        }
