from __future__ import annotations

import os
from typing import List, Dict

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def _client() -> OpenAI:
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def chat_text(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
) -> str:
    client = _client()
    res = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return (res.choices[0].message.content or "").strip()
