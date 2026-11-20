"""Build and validate deep links."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from urllib.parse import parse_qs, quote, urlencode, urlparse

from .apps import get

KNOWN_SCHEMES = {"http", "https"}


@dataclass
class Problem:
    level: str
    message: str


@dataclass
class Validation:
    url: str
    scheme: str
    host: str
    parameters: Dict[str, List[str]] = field(default_factory=dict)
    problems: List[Problem] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(problem.level == "error" for problem in self.problems)

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "scheme": self.scheme,
            "host": self.host,
            "parameters": self.parameters,
            "ok": self.ok,
            "problems": [{"level": p.level, "message": p.message} for p in self.problems],
        }


def build(app_key: str, target: str) -> str:
    """Build a deep link for a known app.

    The payload is percent-encoded as a query value, so a path with spaces or unicode
    survives the round trip.
    """
    app = get(app_key)
    if app is None:
        raise ValueError("unknown app: %s (known: infuse, vlc, youtube)" % app_key)

    value = target.strip()
    if not value:
        raise ValueError("empty target")

    query = urlencode({app.required: value}, quote_via=quote, safe="")
    path = app.path.lstrip("/")
    return "%s://%s?%s" % (app.scheme, path, query)


def validate(url: str) -> Validation:
    parsed = urlparse(url)
    result = Validation(url=url, scheme=parsed.scheme.lower(), host=parsed.netloc)
    result.parameters = parse_qs(parsed.query, keep_blank_values=True)

    if not parsed.scheme:
        result.problems.append(
            Problem("error", "no URL scheme; an app link looks like app://path?key=value")
        )
        return result

    if " " in url:
        result.problems.append(Problem("error", "raw space in the URL; encode it as %20"))
    if "%25" in url:
        result.problems.append(Problem("warning", "looks double-encoded; check the payload"))

    app = get(parsed.scheme)
    if parsed.scheme in KNOWN_SCHEMES:
        result.problems.append(
            Problem("error", "this is a web URL, not an app deep link (scheme %s)" % parsed.scheme)
        )
    elif app is None:
        result.problems.append(
            Problem(
                "warning",
                "unknown scheme %r; tvOS schemes are per-app and undocumented" % parsed.scheme,
            )
        )
    else:
        if app.required not in result.parameters:
            result.problems.append(
                Problem("error", "%s expects a %r parameter" % (app.name, app.required))
            )
        elif not result.parameters[app.required][0]:
            result.problems.append(Problem("error", "parameter %r is empty" % app.required))

    return result


def decode_target(url: str, key: str = "url") -> Optional[str]:
    """Extract the decoded payload, useful when testing a link by hand."""
    values = parse_qs(urlparse(url).query, keep_blank_values=True).get(key)
    return values[0] if values else None
