from __future__ import annotations

from typing import Any, Dict


def sales_note_prompt(data: Dict[str, Any]) -> str:
    inp = data.get("input", {}) or {}
    sources = data.get("sources", {}) or {}
    site = (data.get("metrics", {}) or {}).get("site", {}) or {}

    return f"""
    You are generating a sales note.

    STRICT RULES (NO EXCEPTIONS):
    - Do NOT invent facts.
    - Do NOT suggest marketing, SEO, growth or product improvements unless explicitly supported by provided data.
    - If data is missing, you MUST state that no conclusions can be drawn.
    - In case of missing data, Quick wins can ONLY be about providing access or data.

    Input:
    - domain: {inp.get("client_domain")}
    - market: {inp.get("market")}
    - language: {inp.get("language")}
    - mode: {inp.get("mode")}
    - competitors: {inp.get("competitors")}

    Sources:
    - semrush_overview_screenshot: {"provided" if sources.get("semrush_overview_screenshot") else "not provided"}
    - blocked: {bool(site.get("blocked"))}

    Write EXACTLY 10–15 lines in this structure:

    Facts (3 lines)  
    Insights (3 lines)  
    Quick wins (3 lines)  
    CTA (1 line)

    If semrush_overview_screenshot is NOT provided:
    - Facts must state that performance data is unavailable.
    - Insights must describe implications of missing data, NOT opportunities.
    - Quick wins must ONLY describe steps to obtain data.
    """.strip()


def report_md_prompt(data: Dict[str, Any]) -> str:
    inp = data.get("input", {}) or {}
    sources = data.get("sources", {}) or {}
    site = (data.get("metrics", {}) or {}).get("site", {}) or {}
    outputs = data.get("outputs", {}) or {}

    return f"""
    Write a one-page markdown report.

    STRICT RULES:
    - Do NOT invent facts.
    - Do NOT describe opportunities, improvements or strategies without concrete data.
    - If data is missing, clearly state that analysis is limited.

    Use this structure:

    # Summary
    # What we observed
    # Risks / blockers
    # Opportunities
    # Next steps

    Context:
    - domain: {inp.get("client_domain")}
    - market: {inp.get("market")}
    - language: {inp.get("language")}
    - mode: {inp.get("mode")}
    - competitors: {inp.get("competitors")}

    Evidence:
    - screenshots count: {len(outputs.get("screenshots") or [])}
    - semrush_overview_screenshot: {"provided" if sources.get("semrush_overview_screenshot") else "not provided"}
    - blocked: {bool(site.get("blocked"))}

    Rules:
    - If semrush data is not provided, the Opportunities section MUST focus only on enabling analysis, not business growth.
    - If blocked is true, the report MUST focus on access restriction as the primary blocker.
    """.strip()

