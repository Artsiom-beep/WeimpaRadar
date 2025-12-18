from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict


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
        "screenshots_count": len(screenshots),
        "slides_count": slides_count,
        "site_screens_ms": (metrics.get("timings_ms", {}) or {}).get("site_screens"),
    }

    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row.keys()))
        w.writeheader()
        w.writerow(row)

    return str(p.as_posix())
