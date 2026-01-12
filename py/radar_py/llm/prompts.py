from __future__ import annotations

from typing import Any, Dict


def _reason(v: Dict[str, Any]) -> str:
    r = (v or {}).get("reason")
    return r or "нет данных на предоставленном скрине"


def sales_note_prompt(data: Dict[str, Any]) -> str:
    inp = data.get("input", {}) or {}
    sources = data.get("sources", {}) or {}
    site = (data.get("metrics", {}) or {}).get("site", {}) or {}
    semrush = (data.get("metrics", {}) or {}).get("semrush", {}) or {}
    notes = data.get("notes", {}) or {}
    semrush_comp = notes.get("semrush_competitors", {}) or {}
    comp_notes = notes.get("competitors", {}) or {}

    return f"""
You are generating a sales note.

STRICT:
- Plain text only.
- Exactly 10 lines.
- No "..." anywhere.
- Never invent facts.
- Only use statements supported by EVIDENCE below.
- If something is missing, say it is unavailable and include the reason.

EVIDENCE:
- domain: {inp.get("client_domain")}
- market: {inp.get("market")}
- language: {inp.get("language")}
- mode: {inp.get("mode")}
- competitors list: {inp.get("competitors")}
- blocked: {bool(site.get("blocked"))}
- semrush_files_count: {len((sources.get("semrush_files") or []))}
- semrush_pdf_file: {"provided" if sources.get("semrush_pdf_file") else "not provided"}

Semrush metrics object:
{semrush}

Semrush competitor extraction:
{semrush_comp}

Competitor notes:
{comp_notes}

Structure (EXACTLY 10 lines):
Facts (3 lines)
Insights (3 lines)
Quick wins (3 lines)
CTA (1 line)

Rule:
- If a semrush metric value is null, you MUST state it is unavailable and include its reason.
""".strip()


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

    return f"""
Write a one-page markdown report.

STRICT:
- No "..." anywhere.
- Never invent facts.
- Only use statements supported by EVIDENCE below.
- If you cannot support a statement, write: "No data: <reason>".

Use this structure:

# Summary
# What we observed
# Risks / blockers
# Opportunities
# Next steps

EVIDENCE:
- domain: {inp.get("client_domain")}
- market: {inp.get("market")}
- language: {inp.get("language")}
- mode: {inp.get("mode")}
- competitors list: {inp.get("competitors")}
- blocked: {bool(site.get("blocked"))}
- screenshots count: {len(outputs.get("screenshots") or [])}
- semrush_files_count: {len((sources.get("semrush_files") or []))}
- semrush_pdf_file: {"provided" if sources.get("semrush_pdf_file") else "not provided"}

Semrush metrics:
{semrush_lines}

Semrush competitor extraction:
{semrush_comp}

Competitor notes:
{comp_notes}

Rules:
- If competitor notes exist: you may compare using only those notes.
- If competitors list is not empty but competitor notes missing: write "No data: competitor screenshots/notes not captured".
""".strip()
