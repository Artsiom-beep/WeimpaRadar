from __future__ import annotations

from typing import Dict

from radar_py.utils.domain import slug_domain


def semrush_urls(domain: str, database: str) -> Dict[str, str]:
    d = slug_domain(domain)
    db = (database or "pl").lower()

    domain_overview = f"https://www.semrush.com/analytics/overview/?q={d}&searchType=domain"
    organic_overview = f"https://www.semrush.com/analytics/organic/overview/?q={d}&db={db}"
    organic_competitors = f"https://www.semrush.com/analytics/organic/competitors/?q={d}&db={db}"

    return {
        "domain_overview": domain_overview,
        "organic_overview": organic_overview,
        "organic_competitors": organic_competitors,
    }
