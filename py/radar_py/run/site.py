from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict

from radar_py.commands.site_screens import cmd_site_screens


def capture_client_site(
    req: Dict[str, Any],
    data: Dict[str, Any],
    screenshots_dir: Path,
) -> None:
    """
    1) Снимает скрины сайта клиента.
    2) Заполняет:
       - outputs.screenshots
       - sources.site_screenshots
       - notes.client_site_meta
       - metrics.timings_ms.site_screens
       - metrics.site.*
    """
    t0 = time.perf_counter()

    ss_req: Dict[str, Any] = {
        "cmd": "site_screens",
        "client_domain": data["input"]["client_domain"],
        "out_dir": str(screenshots_dir),
    }

    # Слайды делаем только если ключ присутствует (как в текущем cmd_site_screens)
    if "slide_limit" in req:
        ss_req["slide_limit"] = req.get("slide_limit")

    ss_res = cmd_site_screens(ss_req)

    data["metrics"]["timings_ms"]["site_screens"] = int((time.perf_counter() - t0) * 1000)

    files = (ss_res.get("files") or []) if isinstance(ss_res, dict) else []
    meta = (ss_res.get("meta") or {}) if isinstance(ss_res, dict) else {}

    shot_paths = [str((screenshots_dir / f).as_posix()) for f in files]

    data["outputs"]["screenshots"] = shot_paths
    data["sources"]["site_screenshots"] = shot_paths
    data["notes"]["client_site_meta"] = meta or None

    site = data["metrics"]["site"]
    site["slider_detected"] = meta.get("slider_detected")
    site["slider_method"] = meta.get("method")
    site["slides_attempted"] = meta.get("slides_attempted")
    site["blocked"] = bool(meta.get("blocked"))

    if site["blocked"] and meta.get("blocked_reason"):
        data.setdefault("notes", {})["site_blocked_reason"] = str(meta.get("blocked_reason"))
