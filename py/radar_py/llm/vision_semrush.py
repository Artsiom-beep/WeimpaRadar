from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from radar_py.llm.openai_client import vision_json


_METRIC_KEYS = [
    "authority_score",
    "organic_traffic",
    "organic_keywords",
    "paid_traffic",
    "backlinks",
]


def _null_reason() -> Dict[str, Any]:
    return {"value": None, "reason": "нет данных на предоставленном скрине"}


def extract_semrush_metrics(semrush_image_path: str | Path) -> Dict[str, Any]:
    p = Path(semrush_image_path)
    if not p.exists():
        return {k: _null_reason() for k in _METRIC_KEYS}

    prompt = """
You are extracting Semrush metrics from a screenshot.

Return STRICTLY a JSON object with EXACTLY these 5 keys:
- authority_score
- organic_traffic
- organic_keywords
- paid_traffic
- backlinks

Each key maps to an object:
{ "value": <number|string|null>, "reason": <string|null> }

Rules:
- Only use values that are clearly visible in the screenshot.
- If a value is not visible / cropped / unreadable / missing, set:
  value = null
  reason = "нет данных на предоставленном скрине"
- If value is present, reason must be null.
- Do not include any extra keys.
- Do not guess. Do not estimate. Do not compute.
""".strip()

    raw = vision_json(image_path=p, prompt=prompt, temperature=0.0)

    out: Dict[str, Any] = {}
    for k in _METRIC_KEYS:
        v = raw.get(k) if isinstance(raw, dict) else None
        if not isinstance(v, dict):
            out[k] = _null_reason()
            continue

        value = v.get("value", None)
        if value is None:
            out[k] = _null_reason()
        else:
            out[k] = {"value": value, "reason": None}

    return out


_DOMAIN_RE = re.compile(r"^[a-z0-9-]+(\.[a-z0-9-]+)+$")


def _split_domains(s: str) -> List[str]:
    t = (s or "").strip().lower()
    if not t:
        return []

    t = t.replace("https://", "").replace("http://", "")
    t = t.split("/")[0].strip()

    parts = re.split(r"[\s,;|]+", t)
    out: List[str] = []
    for p in parts:
        d = (p or "").strip().strip(".")
        if not d:
            continue
        if _DOMAIN_RE.match(d):
            out.append(d)

    uniq: List[str] = []
    for d in out:
        if d not in uniq:
            uniq.append(d)
    return uniq


def extract_semrush_competitors(semrush_image_path: str | Path, *, limit: int = 12) -> Dict[str, Any]:
    p = Path(semrush_image_path)
    if not p.exists():
        return {"domains": [], "reason": "нет данных на предоставленном скрине"}

    limit = max(1, min(int(limit or 12), 30))

    prompt = f"""
You are extracting competitor domains from a Semrush screenshot.

Return STRICTLY a JSON object with EXACTLY these keys:
- domains: an array of strings
- reason: a string or null

Rules:
- Extract ONLY competitor domain names that are clearly visible.
- Domain format examples: "example.com", "brightcall.ai".
- Do NOT output URLs. Do NOT output company names.
- Output at most {limit} domains.
- If no competitor domains are visible (cropped / unreadable / missing section):
  domains = []
  reason = "нет данных на предоставленном скрине"
- If at least one domain is present:
  reason must be null.
- Do not guess. Do not infer. Do not add extra keys.
""".strip()

    raw = vision_json(image_path=p, prompt=prompt, temperature=0.0)

    domains: List[str] = []
    if isinstance(raw, dict) and isinstance(raw.get("domains"), list):
        for item in raw.get("domains"):
            if not isinstance(item, str):
                continue
            for d in _split_domains(item):
                if d and d not in domains:
                    domains.append(d)

    domains = domains[:limit]
    if domains:
        return {"domains": domains, "reason": None}

    return {"domains": [], "reason": "нет данных на предоставленном скрине"}
