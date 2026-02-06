from __future__ import annotations

import re
from urllib.parse import urlsplit


def slug_domain(s: str) -> str:
    """
    Нормализует домен/URL к виду "example.com"
    (без схемы, путей, query, фрагментов, порта, кредов).
    """
    t = (s or "").strip()
    t = t.split(",")[0].strip()
    t = t.split()[0].strip()

    raw = t
    if "://" not in raw:
        raw = "https://" + raw

    try:
        parts = urlsplit(raw)
        host = (parts.hostname or "").strip().lower().strip(".")
    except Exception:
        host = ""

    if host:
        return host

    # fallback для совсем кривого ввода
    u = t.strip().lower()
    u = u.replace("https://", "").replace("http://", "")
    u = u.split("@")[-1]
    u = re.split(r"[/?#]", u, 1)[0]
    u = u.split(":")[0]
    return u.strip("/").strip(".")
