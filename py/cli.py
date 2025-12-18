import json
import sys

from radar_py.commands.site_screens import cmd_site_screens
from radar_py.commands.run import cmd_run


def main() -> None:
    raw = sys.stdin.read()
    req = json.loads(raw) if raw.strip() else {}

    cmd = req.get("cmd")

    if cmd == "site_screens":
        res = cmd_site_screens(req)
    elif cmd == "run":
        res = cmd_run(req)
    else:
        res = {"ok": False, "error": f"unknown cmd: {cmd}"}

    sys.stdout.write(json.dumps(res, ensure_ascii=False))
    sys.stdout.flush()


if __name__ == "__main__":
    main()
