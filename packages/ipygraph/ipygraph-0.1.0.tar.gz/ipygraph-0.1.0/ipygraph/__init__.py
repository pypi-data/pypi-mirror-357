"""
ipygraph
~~~~~~~~
A tiny desktop landing page (PyWebview + React + particles.js).

Import and call :pyfunc:`ipygraph.run` to open the window, or just
execute ``python -m ipygraph`` / run the ``ipygraph`` console-script.

:copyright: 2025 Your Name
:license:   MIT, see LICENSE for details.
"""

from importlib.metadata import version as _pkg_version

from .app import run  # re-export for convenience

__all__ = ["run", "__version__"]

try:
    __version__: str = _pkg_version(__name__)
except Exception:  # local editable install or missing metadata
    __version__ = "0.0.0"
