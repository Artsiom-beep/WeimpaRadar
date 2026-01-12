from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict


def _m(data: Dict[str, Any], key: str) -> Dict[str, Any]:
    semrush = ((data.get("metrics") or {}).get("semrush") or {})
    v = semrush.get(key) or {}
    if isinstance(v, dict):
        return v
    return {"value": None, "reason": "нет данных на предоставленном скрине"}


def write_data_csv_v0_1(data: Dict[str, Any], csv_path: str | Path) -> str:
    p = Path(csv_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    inp = data.get("input", {}) or {}
    metrics = data.get("metrics", {}) or {}
    site = metrics.get("site", {}) or {}
    outputs = data.get("outputs", {}) or {}

    screenshots = outputs.get("screenshots") or []
    slides_count = sum(1 for s in screenshots if Path(s).name.startswith("slide_"))

    row = {
        "version": data.get("version"),
        "run_id": data.get("run_id"),
        "created_at": data.get("created_at"),
        "client_domain": inp.get("client_domain"),
        "market": inp.get("market"),
        "language": inp.get("language"),
        "mode": inp.get("mode"),
        "competitors": ",".join(inp.get("competitors") or []),
        "slider_detected": site.get("slider_detected"),
        "slider_method": site.get("slider_method"),
        "slides_attempted": site.get("slides_attempted"),
        "blocked": site.get("blocked"),
        "screenshots_count": len(screenshots),
        "slides_count": slides_count,
        "site_screens_ms": (metrics.get("timings_ms", {}) or {}).get("site_screens"),
        # semrush values
        "semrush_authority_score": _m(data, "authority_score").get("value"),
        "semrush_organic_traffic": _m(data, "organic_traffic").get("value"),
        "semrush_organic_keywords": _m(data, "organic_keywords").get("value"),
        "semrush_paid_traffic": _m(data, "paid_traffic").get("value"),
        "semrush_backlinks": _m(data, "backlinks").get("value"),
        # semrush reasons
        "semrush_authority_score_reason": _m(data, "authority_score").get("reason"),
        "semrush_organic_traffic_reason": _m(data, "organic_traffic").get("reason"),
        "semrush_organic_keywords_reason": _m(data, "organic_keywords").get("reason"),
        "semrush_paid_traffic_reason": _m(data, "paid_traffic").get("reason"),
        "semrush_backlinks_reason": _m(data, "backlinks").get("reason"),
    }

    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        w.writeheader()
        w.writerow(row)

    return str(p.as_posix())
