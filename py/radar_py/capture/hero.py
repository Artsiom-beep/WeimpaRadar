from pathlib import Path


def capture_hero(page, out_dir: Path, name: str = "hero.png") -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    page.evaluate("() => window.scrollTo(0, 0)")
    path = out_dir / name
    page.screenshot(path=str(path), full_page=False)
    return name
