from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

from radar_py.commands.site_screens import cmd_site_screens
from radar_py.commands.semrush_screens import cmd_semrush_screens
from radar_py.export.csv_v0_1 import write_data_csv_v0_1
from radar_py.llm.generate import generate_sales_and_report
from radar_py.llm.openai_client import chat_text
from radar_py.llm.vision_semrush import extract_semrush_metrics, extract_semrush_competitors
from radar_py.schema.v0_1 import new_data_v0_1
from radar_py.semrush.pdf_to_images import render_pdf_to_pngs
from radar_py.utils.fs import ensure_dir, write_json


def _slug_domain(s: str) -> str:
    t = (s or "").strip().lower()
    t = t.replace("https://", "").replace("http://", "").strip()
    t = t.split(",")[0].strip()
    t = t.split()[0].strip()
    return t.strip("/")


def _collect_semrush_upload_images(uploads_dir: Path) -> List[Path]:
    out: List[Path] = []
    for pat in ("semrush_*.png", "semrush_*.jpg", "semrush_*.jpeg"):
        out.extend(sorted(uploads_dir.glob(pat)))

    uniq: List[Path] = []
    seen = set()
    for p in out:
        rp = str(p.resolve())
        if rp not in seen:
            seen.add(rp)
            uniq.append(p)
    return uniq


def _copy_into_screenshots(files: List[Path], screenshots_dir: Path) -> List[Path]:
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    out: List[Path] = []
    for p in files:
        try:
            dst = screenshots_dir / p.name
            dst.write_bytes(p.read_bytes())
            out.append(dst)
        except Exception:
            continue
    return out


def _merge_semrush_metrics(base: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in (candidate or {}).items():
        if not isinstance(v, dict):
            continue
        if (base.get(k) or {}).get("value") is None and v.get("value") is not None:
            base[k] = {"value": v.get("value"), "reason": None}
    return base


def _competitor_note_prompt(*, language: str, domain: str, title: str, body_excerpt: str, blocked: bool) -> str:
    lang = (language or "en").lower()

    if lang == "ru":
        return f"""
Ты пишешь короткую заметку про сайт конкурента.

СТРОГО:
- Только plain text.
- 3–5 строк.
- Используй только то, что видно в title и body_excerpt.
- Никаких догадок.
- Если данных мало: "Нет данных: ..." и причина.

domain: {domain}
blocked: {blocked}
title: {title}
body_excerpt: {body_excerpt}
""".strip()

    return f"""
You write a short note about a competitor website.

STRICT:
- Plain text only.
- 3–5 lines.
- Use only what is visible in title and body_excerpt.
- No guessing.
- If insufficient: "No data: ..." with a reason.

domain: {domain}
blocked: {blocked}
title: {title}
body_excerpt: {body_excerpt}
""".strip()


def cmd_run(req: Dict[str, Any]) -> Dict[str, Any]:
    client_domain = req.get("client_domain") or req.get("url") or ""
    if not client_domain:
        return {"ok": False, "error": "client_domain is required"}

    market = req.get("market", "Global")
    language = req.get("language", "en")
    mode = req.get("mode", "sales")

    competitors = req.get("competitors") or []
    if isinstance(competitors, str):
        competitors = [competitors]
    competitors = [_slug_domain(c) for c in competitors if c]

    run_id = req.get("run_id")
    if not run_id:
        run_id = f"{time.strftime('%Y-%m-%d')}__{_slug_domain(client_domain)}__{mode}__{language}"

    run_dir = ensure_dir(Path("runs") / run_id)
    screenshots_dir = ensure_dir(run_dir / "screenshots")
    uploads_dir = ensure_dir(run_dir / "uploads")

    data = new_data_v0_1(
        run_id=run_id,
        client_domain=_slug_domain(client_domain),
        market=market,
        language=language,
        mode=mode,
        competitors=competitors,
    )

    # --- Semrush auto screenshots (opens browser, remembers login in runs/_semrush_profile) ---
    if bool(req.get("semrush_auto")):
        database = (req.get("semrush_db") or req.get("database") or "pl").lower()
        comp = competitors[0] if competitors else None

        try:
            cmd_semrush_screens(
                {
                    "cmd": "semrush_screens",
                    "client_domain": client_domain,
                    "competitor_domain": comp,
                    "database": database,
                    "out_dir": str(uploads_dir),
                    "headless": False,
                    "user_data_dir": str((Path("runs") / "_semrush_profile").as_posix()),
                }
            )
        except Exception:
            # если Semrush-автоскрины не получились — продолжаем дальше (manual evidence still works)
            pass

    # --- site screenshots (never hard-fail the whole run) ---
    t0 = time.perf_counter()
    ss_req: Dict[str, Any] = {
        "cmd": "site_screens",
        "client_domain": client_domain,
        "out_dir": str(screenshots_dir),
    }
    if "slide_limit" in req:
        ss_req["slide_limit"] = req.get("slide_limit")

    ss_res = cmd_site_screens(ss_req)
    data["metrics"]["timings_ms"]["site_screens"] = int((time.perf_counter() - t0) * 1000)

    files = (ss_res.get("files") or []) if isinstance(ss_res, dict) else []
    meta = (ss_res.get("meta") or {}) if isinstance(ss_res, dict) else {}
    data["notes"]["client_site_meta"] = meta or None

    shot_paths = [str((screenshots_dir / f).as_posix()) for f in files]
    data["outputs"]["screenshots"] = shot_paths
    data["sources"]["site_screenshots"] = shot_paths

    data["metrics"]["site"]["slider_detected"] = meta.get("slider_detected")
    data["metrics"]["site"]["slider_method"] = meta.get("method")
    data["metrics"]["site"]["slides_attempted"] = meta.get("slides_attempted")
    data["metrics"]["site"]["blocked"] = bool(meta.get("blocked")) or (not bool(ss_res.get("ok", True)))

    # --- blocked screen manual upload ---
    blocked_upload = uploads_dir / "blocked_screen.png"
    data["sources"]["blocked_screen_file"] = str(blocked_upload.as_posix()) if blocked_upload.exists() else None
    data["sources"]["blocked_screen"] = data["sources"]["blocked_screen_file"]

    # --- Semrush evidence: many images + optional PDF ---
    semrush_upload_images = _collect_semrush_upload_images(uploads_dir)
    data["sources"]["semrush_files"] = [str(p.as_posix()) for p in semrush_upload_images]

    semrush_pdf = uploads_dir / "semrush.pdf"
    data["sources"]["semrush_pdf_file"] = str(semrush_pdf.as_posix()) if semrush_pdf.exists() else None

    semrush_images_in_screens: List[Path] = []
    semrush_images_in_screens.extend(_copy_into_screenshots(semrush_upload_images, screenshots_dir))

    # PDF -> PNG pages in screenshots/
    pdf_page_imgs: List[Path] = []
    if semrush_pdf.exists():
        pages, _reason = render_pdf_to_pngs(semrush_pdf, screenshots_dir)
        pdf_page_imgs = pages or []

    semrush_images_in_screens.extend(pdf_page_imgs)

    for p in semrush_images_in_screens:
        sp = str(p.as_posix())
        if sp not in data["outputs"]["screenshots"]:
            data["outputs"]["screenshots"].append(sp)

    data["sources"]["semrush_source"] = "manual"
    data["sources"]["semrush_screenshot_file"] = str(semrush_upload_images[0].as_posix()) if semrush_upload_images else None
    data["sources"]["semrush_overview_screenshot"] = data["sources"]["semrush_screenshot_file"]

    # --- Semrush metrics: merge from many images ---
    merged = data["metrics"]["semrush"]
    for img in semrush_images_in_screens:
        m = extract_semrush_metrics(img)
        merged = _merge_semrush_metrics(merged, m)
    data["metrics"]["semrush"] = merged

    # --- Competitors: union from many images ---
    client_d = data["input"]["client_domain"]
    all_domains: List[str] = []
    for img in semrush_images_in_screens:
        c = extract_semrush_competitors(img, limit=30)
        for d in (c.get("domains") or []):
            if not isinstance(d, str):
                continue
            dd = _slug_domain(d)
            if not dd:
                continue
            if dd == client_d:
                continue
            if dd not in all_domains:
                all_domains.append(dd)

    if all_domains:
        data["notes"]["semrush_competitors"] = {"domains": all_domains[:30], "reason": None}
        if not competitors:
            competitors = all_domains[:8]
            data["input"]["competitors"] = competitors
    else:
        data["notes"]["semrush_competitors"] = {"domains": [], "reason": "нет данных на предоставленном скрине"}

    # --- Capture 1 competitor and generate a short note ---
    if competitors:
        comp_domain = _slug_domain(competitors[0])
        comp_dir = ensure_dir(screenshots_dir / f"competitor__{comp_domain}")

        comp_res = cmd_site_screens(
            {
                "cmd": "site_screens",
                "client_domain": comp_domain,
                "out_dir": str(comp_dir),
            }
        )

        comp_files = (comp_res.get("files") or []) if isinstance(comp_res, dict) else []
        comp_meta = (comp_res.get("meta") or {}) if isinstance(comp_res, dict) else {}

        comp_shots = [str((comp_dir / f).as_posix()) for f in comp_files]
        for sp in comp_shots:
            if sp not in data["outputs"]["screenshots"]:
                data["outputs"]["screenshots"].append(sp)

        title = (comp_meta.get("title") or "").strip()
        body_excerpt = (comp_meta.get("body_excerpt") or "").strip()
        blocked = bool(comp_meta.get("blocked"))

        note = chat_text(
            messages=[
                {"role": "system", "content": "Never invent facts. Use only the provided evidence."},
                {"role": "user", "content": _competitor_note_prompt(
                    language=language,
                    domain=comp_domain,
                    title=title,
                    body_excerpt=body_excerpt,
                    blocked=blocked,
                )},
            ],
            temperature=0.0,
        )

        data["notes"]["competitors"][comp_domain] = {
            "note": (note or "").strip(),
            "screenshots": comp_shots,
            "site_meta": comp_meta,
        }

    # --- write artifacts ---
    sales_path, report_path = generate_sales_and_report(data, run_dir)
    data["outputs"]["sales_note_txt"] = sales_path
    data["outputs"]["report_md"] = report_path

    data_path = run_dir / "data.json"
    data["outputs"]["data_json"] = str(data_path.as_posix())
    write_json(data_path, data)

    csv_path = run_dir / "data.csv"
    data["outputs"]["data_csv"] = write_data_csv_v0_1(data, csv_path)
    write_json(data_path, data)

    return {
        "ok": True,
        "run_id": run_id,
        "paths": {
            "run_dir": str(run_dir.as_posix()),
            "screenshots_dir": str(screenshots_dir.as_posix()),
            "data_json": str(data_path.as_posix()),
            "data_csv": str(csv_path.as_posix()),
        },
        "site_screens": ss_res,
    }
