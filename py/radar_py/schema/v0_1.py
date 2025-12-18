from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
            "semrush_overview_screenshot": None,
            "blocked_screen": None,
        },
        "metrics": {
            "timings_ms": {},
            "site": {
                "slider_detected": None,
                "slider_method": None,
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
            "competitors": {},
        },
    }
