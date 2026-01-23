from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

from radar_py.semrush.login import goto, scroll_top, shot_viewport, wait_for_login
from radar_py.semrush.urls import semrush_urls
from radar_py.utils.domain import slug_domain


def scroll_to_text(page, text: str) -> bool:
    try:
        loc = page.get_by_text(text).first
        loc.wait_for(timeout=4000)
        loc.scroll_into_view_if_needed()
        page.wait_for_timeout(600)
        return True
    except Exception:
        return False


def capture_one_domain(
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
    d = slug_domain(domain)
    urls = semrush_urls(d, database)

    seq = seq_start

    def n(label: str) -> str:
        nonlocal seq
        seq += 1
        return f"semrush_{seq:02d}__{d}__{label}.png"

    goto(page, urls["domain_overview"])
    wait_for_login(page, out_dir, f"semrush_{seq_start:02d}__{d}", headless=headless, email=email, password=password)
    scroll_top(page)
    files.append(shot_viewport(page, out_dir, n("domain_overview__top")))

    goto(page, urls["organic_overview"])
    wait_for_login(page, out_dir, f"semrush_{seq_start:02d}__{d}", headless=headless, email=email, password=password)
    scroll_top(page)
    files.append(shot_viewport(page, out_dir, n("organic_overview__top")))

    if scroll_to_text(page, "Top Keywords"):
        files.append(shot_viewport(page, out_dir, n("organic_overview__top_keywords")))

    if scroll_to_text(page, "Top Pages"):
        files.append(shot_viewport(page, out_dir, n("organic_overview__top_pages")))

    if scroll_to_text(page, "Main Organic Competitors"):
        files.append(shot_viewport(page, out_dir, n("organic_overview__main_organic_competitors")))

    goto(page, urls["organic_competitors"])
    wait_for_login(page, out_dir, f"semrush_{seq_start:02d}__{d}", headless=headless, email=email, password=password)
    scroll_top(page)
    files.append(shot_viewport(page, out_dir, n("organic_competitors__top")))

    if scroll_to_text(page, "Competitors"):
        files.append(shot_viewport(page, out_dir, n("organic_competitors__section")))

    return files, seq
