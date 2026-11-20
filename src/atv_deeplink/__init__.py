"""atv-deeplink - build and validate Apple TV deep links."""

from .apps import APPS, App, get, get_by_scheme, keys
from .links import Problem, Validation, build, decode_target, validate

__version__ = "0.1.0"

__all__ = [
    "APPS",
    "App",
    "Problem",
    "Validation",
    "build",
    "decode_target",
    "get",
    "get_by_scheme",
    "keys",
    "validate",
    "__version__",
]
