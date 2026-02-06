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
- domain: {{client_domain}}
- market: {{market}}
- language: {{language}}
- mode: {{mode}}
- competitors list: {{competitors}}
- blocked: {{blocked}}
- screenshots count: {{screenshots_count}}
- semrush_files_count: {{semrush_files_count}}
- semrush_pdf_file: {{semrush_pdf_file_status}}

Semrush metrics:
{{semrush_metrics_lines}}

Semrush competitor extraction:
{{semrush_competitors_json}}

Competitor notes:
{{competitor_notes_json}}

Rules:
- If competitor notes exist: you may compare using only those notes.
- If competitors list is not empty but competitor notes missing: write "No data: competitor screenshots/notes not captured".
