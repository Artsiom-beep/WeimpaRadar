from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple

from radar_py.llm.openai_client import chat_text
from radar_py.llm.prompts import sales_note_prompt, report_md_prompt


def generate_sales_and_report(
    data: Dict[str, Any],
    run_dir: str | Path,
) -> Tuple[str, str]:
    run_dir = Path(run_dir)

    sales_text = chat_text(
        messages=[
            {"role": "system", "content": "You are a precise B2B analyst. Never invent facts."},
            {"role": "user", "content": sales_note_prompt(data)},
        ],
        temperature=0.0,
    )

    report_text = chat_text(
        messages=[
            {"role": "system", "content": "You write concise markdown reports. Never invent facts."},
            {"role": "user", "content": report_md_prompt(data)},
        ],
        temperature=0.0,
    )

    sales_path = run_dir / "sales_note.txt"
    report_path = run_dir / "report.md"

    sales_path.write_text(sales_text, encoding="utf-8")
    report_path.write_text(report_text, encoding="utf-8")

    return str(sales_path.as_posix()), str(report_path.as_posix())
