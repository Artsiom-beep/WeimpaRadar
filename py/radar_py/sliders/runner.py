from radar_py.sliders.dots import try_dots
from radar_py.sliders.nav_tabs import try_nav_tabs
from radar_py.sliders.arrow import try_arrow


def run_slider_strategies(page, out_dir, limit: int):
    meta = {
        "slider_detected": False,
        "method": None,
    }

    # порядок важен: от более точных к более грубым
    for fn in (try_dots, try_nav_tabs, try_arrow):
        res = fn(page, out_dir, limit)
        if res:
            meta["slider_detected"] = True
            meta["method"] = res.get("method")
            if "selector" in res:
                meta["selector"] = res.get("selector")
            return _Result(files=res["files"], meta=meta)

    return _Result(files=[], meta=meta)


class _Result:
    def __init__(self, files: list[str], meta: dict):
        self.files = files
        self.meta = meta
