from __future__ import annotations

import httpx

from pangram_breaker.config import LLMConfig


def chat(llm: LLMConfig, prompt: str, system: str | None = None) -> str:
    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    url = f"{llm.base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {llm.api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": llm.model,
        "messages": messages,
    }

    resp = httpx.post(url, json=body, headers=headers, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]
