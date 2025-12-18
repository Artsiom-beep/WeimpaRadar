import time


def state_sig(page) -> str:
    try:
        return page.evaluate(
            "() => (document.title + '|' + location.hash + '|' + document.body.innerText.slice(0, 1200))"
        )
    except Exception:
        return str(time.time())
