from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from playwright.sync_api import sync_playwright


def _slug_domain(s: str) -> str:
    t = (s or "").strip().lower()
    t = t.replace("https://", "").replace("http://", "").strip()
    t = t.split(",")[0].strip()
    t = t.split()[0].strip()
    return t.strip("/")


def _ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def _shot_viewport(page, out_dir: Path, filename: str) -> str:
    _ensure_dir(out_dir)
    path = out_dir / filename
    page.screenshot(path=str(path), full_page=False)
    return filename


def _scroll_top(page) -> None:
    page.evaluate("() => window.scrollTo(0, 0)")
    page.wait_for_timeout(400)


def _scroll_to_text(page, text: str) -> bool:
    try:
        loc = page.get_by_text(text).first
        loc.wait_for(timeout=4000)
        loc.scroll_into_view_if_needed()
        page.wait_for_timeout(600)
        return True
    except Exception:
        return False


def _goto(page, url: str) -> None:
    page.goto(url, wait_until="domcontentloaded")
    try:
        page.wait_for_load_state("networkidle", timeout=12000)
    except Exception:
        pass
    page.wait_for_timeout(400)


def _needs_login(page) -> bool:
    u = (page.url or "").lower()
    if "login" in u:
        return True
    try:
        if page.locator('input[type="password"]').count() > 0:
            return True
    except Exception:
        pass
    return False


def _load_semrush_creds(req: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    # 1) req
    e = (req.get("semrush_email") or "").strip() or None
    p = (req.get("semrush_password") or "").strip() or None
    if e and p:
        return e, p

    # 2) env
    e = (os.environ.get("SEMRUSH_EMAIL") or "").strip() or None
    p = (os.environ.get("SEMRUSH_PASSWORD") or "").strip() or None
    if e and p:
        return e, p

    # 3) json file
    secrets_file = (req.get("semrush_secrets_file") or os.environ.get("SEMRUSH_SECRETS_FILE") or "").strip()
    if not secrets_file:
        return None, None

    try:
        raw = json.loads(Path(secrets_file).read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return None, None
        e = (raw.get("email") or raw.get("user") or "").strip() or None
        p = (raw.get("password") or raw.get("pass") or "").strip() or None
        return e, p
    except Exception:
        return None, None


def _click_login_submit(page) -> None:
    try:
        btn = page.get_by_role("button", name=re.compile(r"(log\s*in|sign\s*in|continue)", re.I)).first
        if btn.count() > 0:
            btn.click()
            return
    except Exception:
        pass

    try:
        loc = page.locator('button[type="submit"], input[type="submit"]').first
        if loc.count() > 0:
            loc.click()
            return
    except Exception:
        pass


def _auto_login(page, email: str, password: str) -> None:
    try:
        email_loc = page.locator(
            'input[type="email"], input[name="email"], input[name="login"], input[autocomplete="email"]'
        ).first
        if email_loc.count() == 0:
            email_loc = page.locator('input[placeholder*="email" i], input[placeholder*="e-mail" i]').first
        if email_loc.count() > 0:
            email_loc.fill(email)
    except Exception:
        pass

    try:
        pass_loc = page.locator(
            'input[type="password"], input[name="password"], input[autocomplete="current-password"]'
        ).first
        if pass_loc.count() > 0:
            pass_loc.fill(password)
    except Exception:
        pass

    try:
        _click_login_submit(page)
    except Exception:
        pass


def _wait_for_login(page, out_dir: Path, name_prefix: str, *, headless: bool, email: Optional[str], password: Optional[str]) -> None:
    if not _needs_login(page):
        return

    _scroll_top(page)
    _shot_viewport(page, out_dir, f"{name_prefix}__login_needed.png")

    if email and password:
        _auto_login(page, email, password)

    if headless:
        # в headless ручной логин невозможен, не зависать на 10 минут
        page.wait_for_timeout(1500)
        return

    t0 = time.time()
    while time.time() - t0 < 600:
        if not _needs_login(page):
            return
        page.wait_for_timeout(1000)


def _semrush_urls(domain: str, database: str) -> Dict[str, str]:
    d = _slug_domain(domain)
    db = (database or "pl").lower()

    domain_overview = f"https://www.semrush.com/analytics/overview/?q={d}&searchType=domain"
    organic_overview = f"https://www.semrush.com/analytics/organic/overview/?q={d}&db={db}"
    organic_competitors = f"https://www.semrush.com/analytics/organic/competitors/?q={d}&db={db}"

    return {
        "domain_overview": domain_overview,
        "organic_overview": organic_overview,
        "organic_competitors": organic_competitors,
    }


def _capture_one_domain(
    page,
    out_dir: Path,
    *,
    domain: str,
    database: str,
    seq_start: int,
    headless: bool,
    email: Optional[str],
    password: Optional[str],
) -> Tuple[List[str], int]:
    files: List[str] = []
    d = _slug_domain(domain)
    urls = _semrush_urls(d, database)

    seq = seq_start

    def n(label: str) -> str:
        nonlocal seq
        seq += 1
        return f"semrush_{seq:02d}__{d}__{label}.png"

    _goto(page, urls["domain_overview"])
    _wait_for_login(page, out_dir, f"semrush_{seq_start:02d}__{d}", headless=headless, email=email, password=password)
    _scroll_top(page)
    files.append(_shot_viewport(page, out_dir, n("domain_overview__top")))

    _goto(page, urls["organic_overview"])
    _wait_for_login(page, out_dir, f"semrush_{seq_start:02d}__{d}", headless=headless, email=email, password=password)
    _scroll_top(page)
    files.append(_shot_viewport(page, out_dir, n("organic_overview__top")))

    if _scroll_to_text(page, "Top Keywords"):
        files.append(_shot_viewport(page, out_dir, n("organic_overview__top_keywords")))

    if _scroll_to_text(page, "Top Pages"):
        files.append(_shot_viewport(page, out_dir, n("organic_overview__top_pages")))

    if _scroll_to_text(page, "Main Organic Competitors"):
        files.append(_shot_viewport(page, out_dir, n("organic_overview__main_organic_competitors")))

    _goto(page, urls["organic_competitors"])
    _wait_for_login(page, out_dir, f"semrush_{seq_start:02d}__{d}", headless=headless, email=email, password=password)
    _scroll_top(page)
    files.append(_shot_viewport(page, out_dir, n("organic_competitors__top")))

    if _scroll_to_text(page, "Competitors"):
        files.append(_shot_viewport(page, out_dir, n("organic_competitors__section")))

    return files, seq


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

    out_dir = _ensure_dir(out_dir)
    user_data_dir = _ensure_dir(user_data_dir)

    email, password = _load_semrush_creds(req)

    files: List[str] = []
    meta: Dict[str, Any] = {
        "database": database,
        "client_domain": _slug_domain(client_domain),
        "competitor_domain": _slug_domain(competitor_domain) if competitor_domain else None,
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
        f1, seq = _capture_one_domain(
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
            f2, seq = _capture_one_domain(
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
