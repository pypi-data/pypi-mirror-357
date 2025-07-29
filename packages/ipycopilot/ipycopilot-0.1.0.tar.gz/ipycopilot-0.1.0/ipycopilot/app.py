# ipycopilot/app.py
"""
Launch the ipycopilot landing-page window.

▫ Prefers Qt (fastest, fewest external deps) but gracefully falls back to
  other back-ends if Qt isn’t available.
▫ Use  python -m ipycopilot --debug  to keep Chromium DevTools open.
"""

from __future__ import annotations

import importlib.resources as pkg_resources
import pathlib
import sys
from typing import Tuple

import webview


def _locate_index_html() -> pathlib.Path:
    """Return the absolute path to static/index.html shipped in this package."""
    return pkg_resources.files(__package__) / "static" / "index.html"


def _choose_gui_order() -> Tuple[str, ...]:
    """
    Return a tuple of back-ends to try in order.
    First Qt, then GTK, then let pywebview decide.
    """
    return ("qt", "gtk", "")  # empty string → pywebview default search order


def run() -> None:
    debug = "--debug" in sys.argv

    html_uri = _locate_index_html().as_uri()

    # Build the window once; we’ll re-use it for each backend attempt.
    window = webview.create_window(
        title="ipycopilot – Coming Soon",
        url=html_uri,
        width=1024,
        height=768,
        resizable=True,
        zoomable=True,
    )

    for gui in _choose_gui_order():
        try:
            webview.start(debug=debug, gui=gui, http_server=False)
            # If we get here, that GUI worked → announce and exit the loop
            backend = gui or webview.platform.name  # name resolved by pywebview
            print(f"[ipycopilot] Using GUI backend: {backend}")
            break
        except (webview.exceptions.UnsupportedGUI, ModuleNotFoundError) as e:
            print(f"[ipycopilot] GUI '{gui or 'default'}' failed: {e}")
            continue
    else:
        # If every backend fails, raise a helpful error
        raise RuntimeError(
            "ipycopilot could not find a working GUI backend.\n"
            "Install one of:\n"
            "  • Qt  →  conda install pyqt pyqtwebengine -c conda-forge\n"
            "  • GTK →  conda install pygobject gtk3          -c conda-forge\n"
            "or switch to a platform that bundles a backend."
        )


# Enables:  python -m ipycopilot.app
if __name__ == "__main__":
    run()
