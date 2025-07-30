"""
Launch the ipygraph landing-page window.

• Prefers Qt (fewest external deps) but gracefully falls back to GTK, etc.
• Frozen-binary friendly: detects PyInstaller's _MEIPASS.
• Forces software OpenGL so it runs even on headless/old GPUs.

Run  python -m ipygraph --debug  (or ipygraph --debug) to open DevTools.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------#
# Environment tweaks — MUST come before importing Qt/Webview
# ---------------------------------------------------------------------------#
# import os

# # 1) Tell Qt to use Mesa/llvmpipe software renderer
# os.environ.setdefault("QT_OPENGL", "software")

# # 2) Tell QtWebEngine (Chromium) not to rely on GPU
# os.environ.setdefault(
#     "QTWEBENGINE_CHROMIUM_FLAGS",
#     "--disable-gpu --disable-software-rasterizer",
# )

import os
os.environ["QT_OPENGL"] = "software"
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer"
os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
os.environ["QT_XCB_GL_INTEGRATION"] = "none"


# ---------------------------------------------------------------------------#
# Standard libs
# ---------------------------------------------------------------------------#
import pathlib
import sys
from typing import Tuple
import importlib.resources as pkg_resources

# Third-party
import webview


# ---------------------------------------------------------------------------#
# Helper functions
# ---------------------------------------------------------------------------#
def _locate_index_html() -> pathlib.Path:
    """
    Return the absolute path to static/index.html whether running:
      • from site-packages (pip install)
      • from source tree (editable install)
      • inside a PyInstaller bundle (sys._MEIPASS).
    """
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller extracts package to this temp dir
        base = pathlib.Path(sys._MEIPASS) / "ipygraph" / "static"
        return base / "index.html"

    # Non-frozen import; importlib.resources is fine
    return pkg_resources.files("ipygraph") / "static" / "index.html"


def _choose_gui_order() -> Tuple[str, ...]:
    """Try Qt first, then GTK, then let PyWebview auto-detect."""
    return ("qt", "gtk", "")  # "" → default search order


# ---------------------------------------------------------------------------#
# Main entry point
# ---------------------------------------------------------------------------#
def run() -> None:
    debug = "--debug" in sys.argv

    html_uri = _locate_index_html().as_uri()

    # Create the window object once; reused by webview.start()
    webview.create_window(
        title="ipygraph – Coming Soon",
        url=html_uri,
        width=1024,
        height=768,
        resizable=True,
        zoomable=True,
    )

    for gui in _choose_gui_order():
        try:
            webview.start(debug=debug, gui=gui, http_server=False)
            backend = gui or webview.platform.name
            print(f"[ipygraph] Using GUI backend: {backend}")
            break
        except (webview.exceptions.UnsupportedGUI, ModuleNotFoundError) as exc:
            print(f"[ipygraph] GUI '{gui or 'auto'}' failed: {exc}")
            continue
    else:
        raise RuntimeError(
            "ipygraph could not find a working GUI backend.\n"
            "Install one of:\n"
            "  • Qt  →  conda install pyqt pyqtwebengine -c conda-forge\n"
            "  • GTK →  conda install pygobject gtk3          -c conda-forge"
        )


# Enables:  python -m ipygraph.app
if __name__ == "__main__":
    run()
