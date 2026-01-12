from __future__ import annotations

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
    """
    Пытается найти текст и проскроллить к нему.
    Если не нашлось — возвращает False.
    """
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
    # запасные признаки
    try:
        if page.get_by_text("Log in").count() > 0 and page.get_by_text("Password").count() > 0:
            return True
    except Exception:
        pass
    return False


def _wait_for_login(page, out_dir: Path, name_prefix: str, timeout_s: int = 600) -> None:
    """
    Если Semrush попросил логин — ждём, пока пользователь залогинится в открытом окне.
    """
    if not _needs_login(page):
        return

    _scroll_top(page)
    _shot_viewport(page, out_dir, f"{name_prefix}__login_needed.png")

    t0 = time.time()
    while time.time() - t0 < timeout_s:
        if not _needs_login(page):
            return
        page.wait_for_timeout(1000)

    # если не залогинились — просто идём дальше (пайплайн потом попросит manual upload)
    return


def _semrush_urls(domain: str, database: str) -> Dict[str, str]:
    """
    URL-паттерны Semrush. Semrush иногда меняет параметры, поэтому:
    - делаем максимально простые ссылки
    - если Semrush сам редиректит — это нормально
    """
    d = _slug_domain(domain)
    db = (database or "pl").lower()

    # Domain Overview
    domain_overview = f"https://www.semrush.com/analytics/overview/?q={d}&searchType=domain"

    # Organic Research overview + competitors tab
    organic_overview = f"https://www.semrush.com/analytics/organic/overview/?q={d}&db={db}"
    organic_competitors = f"https://www.semrush.com/analytics/organic/competitors/?q={d}&db={db}"

    return {
        "domain_overview": domain_overview,
        "organic_overview": organic_overview,
        "organic_competitors": organic_competitors,
    }


def _capture_one_domain(page, out_dir: Path, *, domain: str, database: str, seq_start: int) -> Tuple[List[str], int]:
    """
    Делает набор скринов по одному домену.
    Возвращает (files, next_seq)
    """
    files: List[str] = []
    d = _slug_domain(domain)
    urls = _semrush_urls(d, database)

    seq = seq_start

    def n(label: str) -> str:
        nonlocal seq
        seq += 1
        return f"semrush_{seq:02d}__{d}__{label}.png"

    # 1) Domain Overview (верх)
    _goto(page, urls["domain_overview"])
    _wait_for_login(page, out_dir, f"semrush_{seq_start:02d}__{d}", timeout_s=600)
    _scroll_top(page)
    files.append(_shot_viewport(page, out_dir, n("domain_overview__top")))

    # 2) Organic Research -> Overview (верх + блоки)
    _goto(page, urls["organic_overview"])
    _wait_for_login(page, out_dir, f"semrush_{seq_start:02d}__{d}", timeout_s=600)
    _scroll_top(page)
    files.append(_shot_viewport(page, out_dir, n("organic_overview__top")))

    # Top Keywords
    if _scroll_to_text(page, "Top Keywords"):
        files.append(_shot_viewport(page, out_dir, n("organic_overview__top_keywords")))

    # Top Pages
    if _scroll_to_text(page, "Top Pages"):
        files.append(_shot_viewport(page, out_dir, n("organic_overview__top_pages")))

    # Main Organic Competitors
    if _scroll_to_text(page, "Main Organic Competitors"):
        files.append(_shot_viewport(page, out_dir, n("organic_overview__main_organic_competitors")))

    # 3) Organic Research -> Competitors (таб)
    _goto(page, urls["organic_competitors"])
    _wait_for_login(page, out_dir, f"semrush_{seq_start:02d}__{d}", timeout_s=600)
    _scroll_top(page)
    files.append(_shot_viewport(page, out_dir, n("organic_competitors__top")))

    # Таблица конкурентов обычно ниже
    if _scroll_to_text(page, "Competitors"):
        files.append(_shot_viewport(page, out_dir, n("organic_competitors__section")))

    return files, seq


def cmd_semrush_screens(req: Dict[str, Any]) -> Dict[str, Any]:
    """
    Делает Semrush-скрины и складывает в out_dir (обычно runs/<run_id>/uploads).

    req:
      - client_domain (обязательно)
      - competitor_domain (опционально)
      - database: "pl" (по умолчанию)
      - out_dir: куда сохранять (обязательно)
      - user_data_dir: профиль браузера (по умолчанию runs/_semrush_profile)
      - headless: False (по умолчанию)
    """
    client_domain = req.get("client_domain") or ""
    if not client_domain:
        return {"ok": False, "error": "client_domain is required"}

    competitor_domain = req.get("competitor_domain") or None
    database = (req.get("database") or "pl").lower()

    out_dir = Path(req.get("out_dir") or "")
    if not str(out_dir).strip():
        return {"ok": False, "error": "out_dir is required"}

    user_data_dir = Path(req.get("user_data_dir") or (Path("runs") / "_semrush_profile"))
    headless = bool(req.get("headless", False))

    out_dir = _ensure_dir(out_dir)
    user_data_dir = _ensure_dir(user_data_dir)

    files: List[str] = []
    meta: Dict[str, Any] = {
        "database": database,
        "client_domain": _slug_domain(client_domain),
        "competitor_domain": _slug_domain(competitor_domain) if competitor_domain else None,
        "headless": headless,
        "user_data_dir": str(user_data_dir.as_posix()),
    }

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=False,
            channel="chrome",
            viewport={"width": 1440, "height": 900},
        )

        page = context.new_page()
        page.set_default_timeout(60_000)
        page.set_default_navigation_timeout(60_000)

        seq = 0

        # Клиент
        f1, seq = _capture_one_domain(page, out_dir, domain=client_domain, database=database, seq_start=seq)
        files.extend(f1)

        # Конкурент
        if competitor_domain:
            f2, seq = _capture_one_domain(page, out_dir, domain=competitor_domain, database=database, seq_start=seq)
            files.extend(f2)

        try:
            context.close()
        except Exception:
            pass

    return {"ok": True, "files": files, "meta": meta}
