"""Lightweight display shim for basic mode.

This module re-exports the small `ILI9341` helper from
`Calculator/drivers/ili9341.py`. Use this shim so higher-level mode
code can import `modes.basic.display` and we can later move the
implementation without changing call sites.
"""

try:
    from drivers.ili9341 import ILI9341
except Exception:
    # On host/IDE the drivers package won't be present; provide a
    # small fallback stub so imports don't crash during static analysis.
    class ILI9341:
        def __init__(self, *a, **k):
            raise ImportError('drivers.ili9341 not available on host')

__all__ = ["ILI9341"]
