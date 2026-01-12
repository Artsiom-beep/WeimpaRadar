from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:
    load_dotenv = None  # type: ignore

from openai import OpenAI

if load_dotenv:
    try:
        load_dotenv()
    except Exception:
        pass


def _client() -> OpenAI:
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def _default_text_model() -> str:
    return os.environ.get("OPENAI_TEXT_MODEL") or "gpt-4o-mini"


def _default_vision_model() -> str:
    return os.environ.get("OPENAI_VISION_MODEL") or "gpt-4o-mini"


def chat_text(
    messages: List[Dict[str, Any]],
    model: Optional[str] = None,
    temperature: float = 0.2,
) -> str:
    client = _client()
    res = client.chat.completions.create(
        model=model or _default_text_model(),
        messages=messages,
        temperature=temperature,
    )
    return (res.choices[0].message.content or "").strip()


def _b64_image_data_url(image_path: str | Path) -> str:
    p = Path(image_path)
    b = p.read_bytes()
    ext = p.suffix.lower().lstrip(".") or "png"
    if ext == "jpg":
        ext = "jpeg"
    return f"data:image/{ext};base64,{base64.b64encode(b).decode('ascii')}"


def vision_json(
    *,
    image_path: str | Path,
    prompt: str,
    model: Optional[str] = None,
    temperature: float = 0.0,
) -> Dict[str, Any]:
    """
    Calls a vision-capable model on an image and expects a JSON object back.
    Returns {} if parsing fails.
    """
    client = _client()
    data_url = _b64_image_data_url(image_path)

    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": "Return ONLY valid JSON. No markdown. No extra text."},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        },
    ]

    res = client.chat.completions.create(
        model=model or _default_vision_model(),
        messages=messages,
        temperature=temperature,
    )

    txt = (res.choices[0].message.content or "").strip()
    try:
        return json.loads(txt)
    except Exception:
        return {}
