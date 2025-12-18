from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict

from radar_py.commands.site_screens import cmd_site_screens
from radar_py.schema.v0_1 import new_data_v0_1
from radar_py.utils.fs import ensure_dir, write_json
from radar_py.export.csv_v0_1 import write_data_csv_v0_1
from radar_py.llm.generate import generate_sales_and_report




def _slug_domain(s: str) -> str:
    return (
        s.strip()
        .lower()
        .replace("https://", "")
        .replace("http://", "")
        .strip("/")
    )


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
    competitors = [c for c in competitors if c]

    run_id = req.get("run_id")
    if not run_id:
        run_id = f"{time.strftime('%Y-%m-%d')}__{_slug_domain(client_domain)}__{mode}__{language}"

    run_dir = ensure_dir(Path("runs") / run_id)
    screenshots_dir = ensure_dir(run_dir / "screenshots")
    ensure_dir(run_dir / "uploads")

    data = new_data_v0_1(
        run_id=run_id,
        client_domain=_slug_domain(client_domain),
        market=market,
        language=language,
        mode=mode,
        competitors=competitors,
    )

    t0 = time.perf_counter()

    ss_req: Dict[str, Any] = {
        "cmd": "site_screens",
        "client_domain": client_domain,
        "out_dir": str(screenshots_dir),
    }

    # Слайды только по явному запросу: ключ slide_limit присутствует
    if "slide_limit" in req:
        ss_req["slide_limit"] = req.get("slide_limit")

    ss_res = cmd_site_screens(ss_req)

    data["metrics"]["timings_ms"]["site_screens"] = int((time.perf_counter() - t0) * 1000)

    if not ss_res.get("ok"):
        data["metrics"]["site"]["blocked"] = True
        data_path = run_dir / "data.json"
        data["outputs"]["data_json"] = str(data_path.as_posix())
        write_json(data_path, data)
        return {
            "ok": False,
            "error": ss_res.get("error", "site_screens failed"),
            "run_id": run_id,
            "data_path": str(data_path.as_posix()),
        }

    files = ss_res.get("files") or []
    meta = ss_res.get("meta") or {}

    data["outputs"]["screenshots"] = [str((screenshots_dir / f).as_posix()) for f in files]
    data["metrics"]["site"]["slider_detected"] = meta.get("slider_detected")
    data["metrics"]["site"]["slider_method"] = meta.get("method")
    data["metrics"]["site"]["slides_attempted"] = meta.get("slides_attempted", False)
    data["metrics"]["site"]["blocked"] = bool(meta.get("blocked"))

    # --- semrush manual upload ---
    semrush_path = run_dir / "uploads" / "semrush_overview.png"
    if semrush_path.exists():
        data["sources"]["semrush_overview_screenshot"] = str(semrush_path.as_posix())
    else:
        data["sources"]["semrush_overview_screenshot"] = None
    # --- end semrush manual upload ---

    # --- copy semrush into screenshots (requirement) ---
    if semrush_path.exists():
        semrush_screen = screenshots_dir / "semrush_domain_overview.png"
        try:
            semrush_screen.write_bytes(semrush_path.read_bytes())
            semrush_rel = str(semrush_screen.as_posix())
            if semrush_rel not in data["outputs"]["screenshots"]:
                data["outputs"]["screenshots"].append(semrush_rel)
        except Exception:
            pass
    # --- end copy semrush ---

    # --- blocked screen manual upload ---
    blocked_path = run_dir / "uploads" / "blocked_screen.png"
    if blocked_path.exists():
        data["sources"]["blocked_screen"] = str(blocked_path.as_posix())
    else:
        data["sources"]["blocked_screen"] = None
    # --- end blocked screen manual upload ---

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
