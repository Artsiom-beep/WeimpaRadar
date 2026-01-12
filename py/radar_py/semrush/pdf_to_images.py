from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


def render_pdf_to_pngs(pdf_path: str | Path, out_dir: str | Path, *, prefix: str = "semrush_pdf_page") -> Tuple[List[Path], str | None]:
    """
    Делает PNG по страницам PDF.
    Возвращает: (paths, error_reason)
    """
    pdf_path = Path(pdf_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not pdf_path.exists():
        return ([], "pdf file not found")

    try:
        import fitz  # type: ignore
    except Exception:
        fitz = None  # type: ignore

    if fitz is None:
        return ([], "pymupdf is not installed (pip install pymupdf)")

    try:
        doc = fitz.open(str(pdf_path))
        paths: List[Path] = []
        zoom = 2.0
        mat = fitz.Matrix(zoom, zoom)
        for i in range(doc.page_count):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            out = out_dir / f"{prefix}_{i+1:02d}.png"
            pix.save(str(out))
            paths.append(out)
        doc.close()
        return (paths, None)
    except Exception as e:
        return ([], f"failed to render pdf: {e}")
