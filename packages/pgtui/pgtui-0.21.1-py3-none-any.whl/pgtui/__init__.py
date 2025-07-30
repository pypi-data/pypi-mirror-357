from importlib import metadata

from textual.widgets import Tabs

try:
    __version__ = metadata.version("pgtui")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"


# Monkey patch Tabs so they are not focusable
Tabs.can_focus = False
