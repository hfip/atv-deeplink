"""Known tvOS/iOS app URL schemes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class App:
    key: str
    name: str
    scheme: str
    path: str
    required: str
    note: str


APPS: Dict[str, App] = {
    "infuse": App(
        key="infuse",
        name="Infuse",
        scheme="infuse",
        path="/x-callback-url/play",
        required="url",
        note="x-callback-url play endpoint; works on iOS and tvOS",
    ),
    "vlc": App(
        key="vlc",
        name="VLC",
        scheme="vlc-x-callback",
        path="/x-callback-url/stream",
        required="url",
        note="VLC x-callback stream endpoint",
    ),
    "youtube": App(
        key="youtube",
        name="YouTube",
        scheme="youtube",
        path="/watch",
        required="v",
        note="video id, not a full URL",
    ),
}


def get(key: str) -> Optional[App]:
    return APPS.get(key.lower())


def get_by_scheme(scheme: str) -> Optional[App]:
    scheme = scheme.lower()
    for app in APPS.values():
        if app.scheme == scheme:
            return app
    return None


def keys() -> list:
    return sorted(APPS)
