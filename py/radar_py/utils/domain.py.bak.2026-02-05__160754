from __future__ import annotations


def slug_domain(s: str) -> str:
    """
    Нормализует домен/URL к виду "example.com" без схемы и путей.
    Поведение соответствует текущим реализациям _slug_domain в коде.
    """
    t = (s or "").strip().lower()
    t = t.replace("https://", "").replace("http://", "").strip()
    t = t.split(",")[0].strip()
    t = t.split()[0].strip()
    return t.strip("/")
