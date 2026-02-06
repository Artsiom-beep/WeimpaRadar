import time

from radar_py.utils.sig import state_sig
from radar_py.utils.shots import save_viewport, cleanup_files


NAV_SELECTORS = [
    "nav a",
    "nav button",
    "[role='navigation'] a",
    "[role='navigation'] button",
]


def try_nav_tabs(page, out_dir, limit: int) -> dict | None:
    if limit < 2:
        return None

    for sel in NAV_SELECTORS:
        try:
            loc = page.locator(sel)
            cnt = loc.count()
            if cnt < 3:
                continue

            idxs: list[int] = []
            for i in range(min(cnt, 50)):
                try:
                    el = loc.nth(i)
                    if not el.is_visible():
                        continue
                    txt = (el.inner_text() or "").strip()
                    if 2 <= len(txt) <= 24:
                        idxs.append(i)
                except Exception:
                    continue

            if len(idxs) < 3:
                continue

            idxs = idxs[:limit]

            page.evaluate("() => window.scrollTo(0, 0)")
            time.sleep(0.4)

            files: list[str] = []
            save_viewport(page, out_dir, "slide_01.png")
            files.append("slide_01.png")
            last = state_sig(page)

            shot_index = 2
            for i in idxs[1:]:
                if shot_index > limit:
                    break
                try:
                    loc.nth(i).click(timeout=5_000, force=True)
                except Exception:
                    continue

                time.sleep(0.9)
                try:
                    page.wait_for_load_state("networkidle", timeout=2_000)
                except Exception:
                    pass

                now = state_sig(page)
                if now == last:
                    continue

                last = now
                name = f"slide_{shot_index:02d}.png"
                save_viewport(page, out_dir, name)
                files.append(name)
                shot_index += 1

            if len(files) >= 2:
                return {
                    "method": "nav_tabs",
                    "selector": sel,
                    "files": files,
                }

            cleanup_files(out_dir, files)
        except Exception:
            continue

    return None
