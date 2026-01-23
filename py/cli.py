import json
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from radar_py.commands.site_screens import cmd_site_screens
from radar_py.commands.run import cmd_run
from radar_py.commands.semrush_screens import cmd_semrush_screens


def _force_utf8_stdio() -> None:
    for s in (sys.stdin, sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def main() -> None:
    _force_utf8_stdio()

    raw = sys.stdin.read()
    req = json.loads(raw) if raw.strip() else {}

    cmd = req.get("cmd")

    if cmd == "site_screens":
        res = cmd_site_screens(req)
    elif cmd == "semrush_screens":
        res = cmd_semrush_screens(req)
    elif cmd == "run":
        res = cmd_run(req)
    else:
        res = {"ok": False, "error": f"unknown cmd: {cmd}"}

    out = json.dumps(res, ensure_ascii=False)

    try:
        sys.stdout.write(out)
    except UnicodeEncodeError:
        sys.stdout.buffer.write(out.encode("utf-8", errors="replace"))

    sys.stdout.flush()


if __name__ == "__main__":
    main()
