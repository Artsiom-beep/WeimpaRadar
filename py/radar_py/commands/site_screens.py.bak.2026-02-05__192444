from pathlib import Path

from radar_py.browser.session import open_page
from radar_py.capture.full_page import capture_full_page
from radar_py.sliders.runner import run_slider_strategies
from radar_py.utils.url import normalize_url
from radar_py.utils.blocked import looks_blocked


def cmd_site_screens(req: dict) -> dict:
    out_dir = Path(req.get("out_dir", "runs/_tmp/screenshots"))
    out_dir.mkdir(parents=True, exist_ok=True)

    url = normalize_url(req.get("client_domain") or req.get("url") or "")
    if not url:
        return {"ok": False, "error": "missing client_domain/url"}

    # Слайды делаем только если явно попросили (ключ присутствует и > 0)
    if "slide_limit" in req:
        try:
            slide_limit = int(req.get("slide_limit") or 0)
        except Exception:
            slide_limit = 0
    else:
        slide_limit = 0

    slide_limit = max(0, min(slide_limit, 20))

    def _excerpt(s: str, n: int = 700) -> str:
        return " ".join((s or "").split())[:n]

    files: list[str] = []
    meta = {"slider_detected": False, "method": None, "slides_attempted": False}

    with open_page(url) as page:
        try:
            title = page.title() or ""
        except Exception:
            title = ""

        try:
            body_text = page.locator("body").inner_text(timeout=2000) or ""
        except Exception:
            body_text = ""

        meta = {
            "blocked": False,
            "slider_detected": False,
            "method": None,
            "slides_attempted": False,
            "title": title,
            "body_excerpt": _excerpt(body_text),
        }

        if looks_blocked(title, body_text):
            blocked_path = out_dir / "blocked.png"
            page.screenshot(path=str(blocked_path), full_page=False)
            return {
                "ok": True,
                "files": ["blocked.png"],
                "meta": {**meta, "blocked": True},
            }
        # --- end blocked detection ---

        full = capture_full_page(page, out_dir)
        files.append(full)

        if slide_limit > 0:
            slider_result = run_slider_strategies(
                page=page,
                out_dir=out_dir,
                limit=slide_limit,
            )
            if slider_result and getattr(slider_result, "files", None):
                files.extend(slider_result.files)

            sr_meta = getattr(slider_result, "meta", None) or {}
            meta.update(sr_meta)
            meta["slides_attempted"] = True

    return {
        "ok": True,
        "files": files,
        "meta": meta,
    }
