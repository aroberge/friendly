"""Syntax colouring based on the availability of pygments
"""
import sys

from pygments import styles

from . import amical
from . import brunante
from . import friendly_rich

CURRENT_THEME = "brunante"

# Monkey-patching pygments; inspired by
# https://gist.github.com/crowsonkb/4e2eb4439e3fe514cc4755b217f164d5
sys.modules["pygments.styles.amical"] = amical
styles.STYLE_MAP["amical"] = "amical::AmicalStyle"

sys.modules["pygments.styles.brunante"] = brunante
styles.STYLE_MAP["brunante"] = "brunante::BrunanteStyle"


def init_rich_console(style="dark", color_system="auto", force_jupyter=None):
    global CURRENT_THEME
    if style == "light":
        theme = "amical"
    else:
        theme = "brunante"
    CURRENT_THEME = theme

    console = friendly_rich.init_console(
        style=style, theme=theme, color_system=color_system, force_jupyter=force_jupyter
    )
    return console
