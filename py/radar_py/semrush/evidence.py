from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from radar_py.llm.vision_semrush import extract_semrush_competitors, extract_semrush_metrics
from radar_py.semrush.pdf_to_images import render_pdf_to_pngs
from radar_py.utils.domain import slug_domain


def collect_semrush_upload_images(uploads_dir: str | Path) -> List[Path]:
    """
    Ищет semrush_*.png/jpg/jpeg в runs/<run>/uploads.
    Убирает дубликаты и файлы __login_needed.
    """
    uploads_dir = Path(uploads_dir)
    out: List[Path] = []

    for pat in ("semrush_*.png", "semrush_*.jpg", "semrush_*.jpeg"):
        out.extend(sorted(uploads_dir.glob(pat)))

    uniq: List[Path] = []
    seen = set()
    for p in out:
        rp = str(p.resolve())
        if rp in seen:
            continue
        seen.add(rp)
        uniq.append(p)

    uniq = [p for p in uniq if "__login_needed" not in p.name]
    return uniq


def collect_competitor_upload_images(uploads_dir: str | Path, domain: str) -> List[Path]:
    """
    Ищет competitor__<domain>_*.png/jpg/jpeg в runs/<run>/uploads.
    domain нормализуется в slug_domain.
    """
    uploads_dir = Path(uploads_dir)
    d = slug_domain(domain)

    out: List[Path] = []
    for pat in (
        f"competitor__{d}_*.png",
        f"competitor__{d}_*.jpg",
        f"competitor__{d}_*.jpeg",
    ):
        out.extend(sorted(uploads_dir.glob(pat)))

    return out


def copy_into_screenshots(files: List[Path], screenshots_dir: str | Path) -> List[Path]:
    """
    Копирует файлы (байт-в-байт) в screenshots_dir, сохраняя имена.
    Возвращает пути в screenshots_dir.
    """
    screenshots_dir = Path(screenshots_dir)
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


def ingest_semrush_pdf(uploads_dir: str | Path, screenshots_dir: str | Path) -> Tuple[List[Path], Optional[Path], Optional[str]]:
    """
    Если есть uploads/semrush.pdf — рендерит страницы в screenshots_dir.
    Возвращает: (page_images, pdf_path_or_None, error_reason_or_None)
    """
    uploads_dir = Path(uploads_dir)
    screenshots_dir = Path(screenshots_dir)

    pdf_path = uploads_dir / "semrush.pdf"
    if not pdf_path.exists():
        return ([], None, None)

    pages, reason = render_pdf_to_pngs(pdf_path, screenshots_dir)
    return (pages or [], pdf_path, reason)


def merge_semrush_metrics(base: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Логика как раньше: заполняем только те метрики, где base.value is None.
    """
    for k, v in (candidate or {}).items():
        if not isinstance(v, dict):
            continue
        if (base.get(k) or {}).get("value") is None and v.get("value") is not None:
            base[k] = {"value": v.get("value"), "reason": None}
    return base


def extract_semrush_from_images(
    images: List[Path],
    *,
    base_metrics: Optional[Dict[str, Any]] = None,
    client_domain: Optional[str] = None,
    competitors_limit: int = 30,
) -> Tuple[Dict[str, Any], List[str]]:
    """
    1) Мерджит метрики Semrush по множеству картинок.
    2) Собирает union доменов конкурентов по множеству картинок.

    client_domain: если задан, будет выкинут из списка конкурентов.
    """
    merged_metrics: Dict[str, Any] = base_metrics or {}
    client_d = slug_domain(client_domain or "") if client_domain else ""

    all_domains: List[str] = []

    for img in images:
        if not img.exists():
            continue

        m = extract_semrush_metrics(img)
        if isinstance(m, dict):
            merged_metrics = merge_semrush_metrics(merged_metrics, m)

        c = extract_semrush_competitors(img, limit=int(competitors_limit or 30))
        for d in (c.get("domains") or []):
            if not isinstance(d, str):
                continue
            dd = slug_domain(d)
            if not dd:
                continue
            if client_d and dd == client_d:
                continue
            if dd not in all_domains:
                all_domains.append(dd)

    return merged_metrics, all_domains
