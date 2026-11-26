"""The plugin from the command line, its reads alone (the platform's page asks every hook, its changes among them):

    python -m plugin_platform_pi status
    python -m plugin_platform_pi command [FOLDER]

`status` prints its Main as the page reads it (JSON), exiting 1 when it is not valid. `command` prints the lines that
start Pi in FOLDER (else the folder last opened) against what Use… keeps: the model servers are asked through
the platform, so without it the command says so and ends 1. Install, Uninstall, Use… and Open… are asked from the
page alone (liminal-libs 1.99.0: a harness's changes are page-only). The exit code is 0 when the answer is ok."""
from __future__ import annotations

import json
import sys

from liminal_libs.machines.ai import Refusal
from liminal_libs.machines.plugin import CommandError

from . import MACHINE

USAGE = "python -m plugin_platform_pi status | command [FOLDER]"


def said(answer: dict) -> int:
    """A hook's answer printed: its words, then its lines; 0 when it is ok."""
    print(answer.get("said", ""))
    for line in answer.get("lines") or []:
        print(f"  {line}")
    return 0 if answer.get("ok", True) else 1


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    what, rest = (argv[0], argv[1:]) if argv else ("status", [])
    m = MACHINE
    try:
        if what == "status" and not rest:
            page = m.status()
            print(json.dumps(page, indent=1, ensure_ascii=False))
            return 0 if page.get("valid") else 1
        if what == "command" and len(rest) <= 1:
            return said(m.command(rest[0] if rest else None))
    except Refusal as e:
        print(f"refused: {e}", file=sys.stderr)
        return 1
    except (ValueError, LookupError, CommandError) as e:
        print(f"refused: {e}", file=sys.stderr)
        return 1
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
