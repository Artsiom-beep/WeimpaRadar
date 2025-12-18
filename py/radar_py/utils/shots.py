from pathlib import Path


def save_viewport(page, out_dir: Path, name: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out_dir / name), full_page=False)


def save_full(page, out_dir: Path, name: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(out_dir / name), full_page=True)


def cleanup_files(out_dir: Path, names: list[str]) -> None:
    for n in names:
        try:
            (out_dir / n).unlink(missing_ok=True)
        except Exception:
            pass
