from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from radar_py.llm.openai_client import vision_json

_DEFAULT_REASON_RU = "нет данных на предоставленном скрине"
_DEFAULT_REASON_EN = "not visible in the provided screenshot"


def extract_competitor_note(image_path: str | Path, *, language: str, domain: str) -> Dict[str, Any]:
    p = Path(image_path)
    if not p.exists():
        return {"note": None, "reason": _DEFAULT_REASON_RU if (language or "").lower() == "ru" else _DEFAULT_REASON_EN}

    lang = (language or "en").lower()

    if lang == "ru":
        prompt = f"""
Ты извлекаешь короткую заметку о сайте конкурента со СКРИНШОТА.

Верни СТРОГО JSON с ровно 2 ключами:
- note: string или null
- reason: string или null

Правила:
- note = 3–5 строк plain text.
- Используй ТОЛЬКО то, что видно на скрине (текст, заголовки, оффер).
- Никаких догадок, никаких "..." .
- Если данных мало/ничего не видно:
  note = null
  reason = "{_DEFAULT_REASON_RU}"
- Если note заполнен:
  reason = null

domain: {domain}
""".strip()
    else:
        prompt = f"""
You extract a short competitor website note from a SCREENSHOT.

Return STRICTLY JSON with EXACTLY 2 keys:
- note: string or null
- reason: string or null

Rules:
- note = 3–5 lines of plain text.
- Use ONLY what is visible on the screenshot (text/headlines/offer).
- No guessing. No "..." .
- If insufficient/unclear:
  note = null
  reason = "{_DEFAULT_REASON_EN}"
- If note is present:
  reason = null

domain: {domain}
""".strip()

    raw = vision_json(image_path=p, prompt=prompt, temperature=0.0)

    if not isinstance(raw, dict):
        return {"note": None, "reason": _DEFAULT_REASON_RU if lang == "ru" else _DEFAULT_REASON_EN}

    note = raw.get("note")
    reason = raw.get("reason")

    if isinstance(note, str) and note.strip():
        return {"note": note.strip(), "reason": None}

    if isinstance(reason, str) and reason.strip():
        return {"note": None, "reason": reason.strip()}

    return {"note": None, "reason": _DEFAULT_REASON_RU if lang == "ru" else _DEFAULT_REASON_EN}
