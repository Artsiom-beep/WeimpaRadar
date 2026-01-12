from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _metric_null(reason: str = "нет данных на предоставленном скрине") -> Dict[str, Any]:
    return {"value": None, "reason": reason}


def new_data_v0_1(
    run_id: str,
    client_domain: str,
    market: str,
    language: str,
    mode: str,
    competitors: List[str],
) -> Dict[str, Any]:
    return {
        "version": "0.1",
        "run_id": run_id,
        "created_at": iso_now(),
        "input": {
            "client_domain": client_domain,
            "market": market,
            "language": language,
            "mode": mode,
            "competitors": competitors,
        },
        "sources": {
            "site_screenshots": [],
            "semrush_source": "manual",
            "semrush_screenshot_file": None,          # backward compat (1 файл)
            "semrush_overview_screenshot": None,      # backward compat
            "semrush_files": [],                      # новый список файлов (uploads paths)
            "semrush_pdf_file": None,                 # uploads/semrush.pdf
            "blocked_screen_file": None,
            "blocked_screen": None,                   # backward compat
        },
        "metrics": {
            "timings_ms": {},
            "site": {
                "slider_detected": None,
                "slider_method": None,
                "slides_attempted": None,
                "blocked": None,
            },
            "semrush": {
                "authority_score": _metric_null(),
                "organic_traffic": _metric_null(),
                "organic_keywords": _metric_null(),
                "paid_traffic": _metric_null(),
                "backlinks": _metric_null(),
            },
        },
        "outputs": {
            "screenshots": [],
            "sales_note_txt": None,
            "report_md": None,
            "data_json": None,
            "data_csv": None,
        },
        "notes": {
            "client_site_meta": None,
            "semrush_competitors": {"domains": [], "reason": "нет данных на предоставленном скрине"},
            "competitors": {},
        },
    }
