from pathlib import Path


def capture_full_page(page, out_dir: Path, name: str = "full_page.png") -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    page.screenshot(path=str(path), full_page=True)
    return name
