import time

from radar_py.utils.sig import state_sig
from radar_py.utils.shots import save_viewport


def try_arrow(page, out_dir, limit: int) -> dict | None:
    if limit < 2:
        return None

    files: list[str] = []

    page.evaluate("() => window.scrollTo(0, 0)")
    time.sleep(0.4)

    save_viewport(page, out_dir, "slide_01.png")
    files.append("slide_01.png")
    last = state_sig(page)

    for i in range(2, limit + 1):
        try:
            page.keyboard.press("ArrowRight")
        except Exception:
            break

        time.sleep(0.9)
        now = state_sig(page)
        if now == last:
            break

        last = now
        name = f"slide_{i:02d}.png"
        save_viewport(page, out_dir, name)
        files.append(name)

    if len(files) < 2:
        return None

    return {
        "method": "ArrowRight",
        "files": files,
    }
