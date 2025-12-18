from __future__ import annotations

import re

_PATTERNS = [
    r"captcha",
    r"verify you are human",
    r"are you human",
    r"just a moment",
    r"checking your browser",
    r"access denied",
    r"attention required",
    r"cloudflare",
    r"incapsula",
    r"perimeterx",
    r"bot detection",
]

def looks_blocked(title: str, body_text: str) -> bool:
    t = (title or "").lower()
    b = (body_text or "").lower()
    blob = t + "\n" + b
    return any(re.search(p, blob) for p in _PATTERNS)
