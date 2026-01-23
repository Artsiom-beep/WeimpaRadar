from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, Tuple

from radar_py.schema.v0_1 import new_data_v0_1
from radar_py.utils.domain import slug_domain
from radar_py.utils.fs import ensure_dir


def init_run(req: Dict[str, Any]) -> Tuple[Dict[str, Any], Path, Path, Path]:
    client_domain = req.get("client_domain") or req.get("url") or ""
    if not client_domain:
        raise ValueError("client_domain is required")

    market = req.get("market", "Global")
    language = req.get("language", "en")
    mode = req.get("mode", "sales")

    competitors = req.get("competitors") or []
    if isinstance(competitors, str):
        competitors = [competitors]
    competitors = [slug_domain(c) for c in competitors if c]

    run_id = req.get("run_id")
    if not run_id:
        run_id = f"{time.strftime('%Y-%m-%d')}__{slug_domain(client_domain)}__{mode}__{language}"

    run_dir = ensure_dir(Path("runs") / run_id)
    screenshots_dir = ensure_dir(run_dir / "screenshots")
    uploads_dir = ensure_dir(run_dir / "uploads")

    data = new_data_v0_1(
        run_id=run_id,
        client_domain=slug_domain(client_domain),
        market=market,
        language=language,
        mode=mode,
        competitors=competitors,
    )

    return data, run_dir, screenshots_dir, uploads_dir
