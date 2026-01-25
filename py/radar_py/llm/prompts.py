from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict


def _reason(v: Dict[str, Any]) -> str:
    r = (v or {}).get("reason")
    return r or "нет данных на предоставленном скрине"


@lru_cache(maxsize=64)
def _load_default(name: str) -> str:
    base = Path(__file__).resolve().parents[1] / "prompts" / "default"
    p = base / name
    return p.read_text(encoding="utf-8")


def _load_template(name: str, override_text: Any | None) -> str:
    if override_text is not None:
        txt = str(override_text)
        if txt.strip():
            return txt
    return _load_default(name)


def _render(tpl: str, ctx: Dict[str, Any]) -> str:
    out = tpl
    for k, v in ctx.items():
        out = out.replace("{{" + k + "}}", str(v))
    return out


def sales_note_prompt(data: Dict[str, Any]) -> str:
    inp = data.get("input", {}) or {}
    sources = data.get("sources", {}) or {}
    site = (data.get("metrics", {}) or {}).get("site", {}) or {}
    semrush = (data.get("metrics", {}) or {}).get("semrush", {}) or {}
    notes = data.get("notes", {}) or {}
    semrush_comp = notes.get("semrush_competitors", {}) or {}
    comp_notes = notes.get("competitors", {}) or {}

    overrides = (data.get("prompts", {}) or {}).get("overrides", {}) or {}
    tpl = _load_template("sales_note.txt", overrides.get("sales_note"))

    ctx = {
        "client_domain": inp.get("client_domain"),
        "market": inp.get("market"),
        "language": inp.get("language"),
        "mode": inp.get("mode"),
        "competitors": inp.get("competitors"),
        "blocked": bool(site.get("blocked")),
        "semrush_files_count": len((sources.get("semrush_files") or [])),
        "semrush_pdf_file_status": "provided" if sources.get("semrush_pdf_file") else "not provided",
        "semrush_metrics_json": json.dumps(semrush, ensure_ascii=False, indent=2),
        "semrush_competitors_json": json.dumps(semrush_comp, ensure_ascii=False, indent=2),
        "competitor_notes_json": json.dumps(comp_notes, ensure_ascii=False, indent=2),
    }

    return _render(tpl, ctx).strip()


def report_md_prompt(data: Dict[str, Any]) -> str:
    inp = data.get("input", {}) or {}
    sources = data.get("sources", {}) or {}
    site = (data.get("metrics", {}) or {}).get("site", {}) or {}
    outputs = data.get("outputs", {}) or {}
    semrush = (data.get("metrics", {}) or {}).get("semrush", {}) or {}
    notes = data.get("notes", {}) or {}
    semrush_comp = notes.get("semrush_competitors", {}) or {}
    comp_notes = notes.get("competitors", {}) or {}

    def m(k: str) -> str:
        v = (semrush or {}).get(k) or {}
        if (v or {}).get("value") is None:
            return f"{k}: unavailable ({_reason(v)})"
        return f"{k}: {(v or {}).get('value')}"

    semrush_lines = "\n".join([
        m("authority_score"),
        m("organic_traffic"),
        m("organic_keywords"),
        m("paid_traffic"),
        m("backlinks"),
    ])

    overrides = (data.get("prompts", {}) or {}).get("overrides", {}) or {}
    tpl = _load_template("report.md", overrides.get("report_md"))

    ctx = {
        "client_domain": inp.get("client_domain"),
        "market": inp.get("market"),
        "language": inp.get("language"),
        "mode": inp.get("mode"),
        "competitors": inp.get("competitors"),
        "blocked": bool(site.get("blocked")),
        "screenshots_count": len(outputs.get("screenshots") or []),
        "semrush_files_count": len((sources.get("semrush_files") or [])),
        "semrush_pdf_file_status": "provided" if sources.get("semrush_pdf_file") else "not provided",
        "semrush_metrics_lines": semrush_lines,
        "semrush_competitors_json": json.dumps(semrush_comp, ensure_ascii=False, indent=2),
        "competitor_notes_json": json.dumps(comp_notes, ensure_ascii=False, indent=2),
    }

    return _render(tpl, ctx).strip()
