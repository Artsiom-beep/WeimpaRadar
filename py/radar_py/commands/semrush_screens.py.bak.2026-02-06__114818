from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from playwright.sync_api import sync_playwright

from radar_py.semrush.capture import capture_one_domain
from radar_py.semrush.login import load_semrush_creds
from radar_py.utils.domain import slug_domain


def cmd_semrush_screens(req: Dict[str, Any]) -> Dict[str, Any]:
    client_domain = req.get("client_domain") or ""
    if not client_domain:
        return {"ok": False, "error": "client_domain is required"}

    competitor_domain = req.get("competitor_domain") or None
    database = (req.get("database") or "pl").lower()

    out_dir = Path(req.get("out_dir") or "")
    if not str(out_dir).strip():
        return {"ok": False, "error": "out_dir is required"}

    user_data_dir = Path(req.get("user_data_dir") or (Path("runs") / "_semrush_profile"))
    headless = bool(req.get("headless", True))

    out_dir.mkdir(parents=True, exist_ok=True)
    user_data_dir.mkdir(parents=True, exist_ok=True)

    email, password = load_semrush_creds(req)

    files: List[str] = []
    meta: Dict[str, Any] = {
        "database": database,
        "client_domain": slug_domain(client_domain),
        "competitor_domain": slug_domain(competitor_domain) if competitor_domain else None,
        "headless": headless,
        "user_data_dir": str(user_data_dir.as_posix()),
        "has_creds": bool(email and password),
    }

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=headless,
            viewport={"width": 1440, "height": 900},
            args=["--disable-dev-shm-usage"],
        )

        page = context.new_page()
        page.set_default_timeout(60_000)
        page.set_default_navigation_timeout(60_000)

        seq = 0

        f1, seq = capture_one_domain(
            page,
            out_dir,
            domain=client_domain,
            database=database,
            seq_start=seq,
            headless=headless,
            email=email,
            password=password,
        )
        files.extend(f1)

        if competitor_domain:
            f2, seq = capture_one_domain(
                page,
                out_dir,
                domain=competitor_domain,
                database=database,
                seq_start=seq,
                headless=headless,
                email=email,
                password=password,
            )
            files.extend(f2)

        try:
            context.close()
        except Exception:
            pass

    return {"ok": True, "files": files, "meta": meta}
