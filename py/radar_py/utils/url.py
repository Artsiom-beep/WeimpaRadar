from urllib.parse import urlparse


def normalize_url(domain_or_url: str) -> str:
    s = (domain_or_url or "").strip()
    if not s:
        return ""
    if "://" not in s:
        s = "https://" + s
    p = urlparse(s)
    if not p.netloc and p.path:
        s = "https://" + p.path
    return s