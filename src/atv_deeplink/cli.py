"""Command line interface for atv-deeplink."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Iterable, Optional

from . import __version__
from .apps import APPS, get, keys
from .links import build, decode_target, validate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="atv-deeplink",
        description="Build and check deep links for Apple TV apps (Infuse, VLC, YouTube).",
    )
    subparsers = parser.add_subparsers(dest="command")

    build_parser_ = subparsers.add_parser("build", help="build a deep link")
    build_parser_.add_argument("app", choices=keys(), help="target app")
    build_parser_.add_argument("target", help="URL or path the app should open")

    check_parser = subparsers.add_parser("check", help="validate one or more links")
    check_parser.add_argument("url", nargs="+")

    subparsers.add_parser("apps", help="list known apps")

    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("-V", "--version", action="version", version="atv-deeplink " + __version__)
    return parser


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command is None:
        parser.print_help()
        return 2

    if args.command == "apps":
        if args.json:
            print(json.dumps({key: APPS[key].__dict__ for key in keys()}, indent=2))
        else:
            for key in keys():
                app = APPS[key]
                print(
                    "%-8s %-8s %s://%s?%s=..."
                    % (key, app.name, app.scheme, app.path.lstrip("/"), app.required)
                )
                print("         %s" % app.note)
        return 0

    if args.command == "build":
        try:
            url = build(args.app, args.target)
        except ValueError as error:
            print("error: %s" % error, file=sys.stderr)
            return 2
        if args.json:
            print(
                json.dumps(
                    {"url": url, "target": decode_target(url, get(args.app).required)},
                    ensure_ascii=False,
                )
            )
        else:
            print(url)
        return 0

    validations = [validate(url) for url in args.url]
    failures = sum(1 for result in validations if not result.ok)

    if args.json:
        print(
            json.dumps([result.to_dict() for result in validations], indent=2, ensure_ascii=False)
        )
    else:
        for result in validations:
            status = "ok" if result.ok else "error"
            print("%-5s %s" % (status, result.url))
            for problem in result.problems:
                print("      %-7s %s" % (problem.level, problem.message))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
