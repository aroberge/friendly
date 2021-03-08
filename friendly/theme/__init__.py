"""Syntax colouring based on the availability of pygments
"""
import sys

from pygments import styles

from . import brunante
from . import friendly_rich

CURRENT_THEME = "brunante"

# Monkey-patching pygments; inspired by
# https://gist.github.com/crowsonkb/4e2eb4439e3fe514cc4755b217f164d5
sys.modules["pygments.styles.brunante"] = brunante
styles.STYLE_MAP["brunante"] = "brunante::BrunanteStyle"


def init_rich_console(style="dark"):
    global CURRENT_THEME
    if style == "light":
        theme = "tango"
    else:
        theme = "brunante"
    CURRENT_THEME = theme
    return friendly_rich.init_console(style=style, theme=theme)
