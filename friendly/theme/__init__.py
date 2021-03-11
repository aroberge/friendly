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


def validate_color(color):
    valid_characters = set("0123456789abcdefABCDEF")
    if color is None:
        return None
    if isinstance(color, str) and color.startswith("#") and len(color) == 7:
        for char in color[1:]:
            if char not in valid_characters:
                break
        else:
            return color
    print("Invalid color")
    return None


def init_rich_console(
    style="dark", color_system="auto", force_jupyter=None, background=None
):
    global CURRENT_THEME
    background = validate_color(background)
    if style == "light":
        theme = "amical"
        if background is None:
            amical.AmicalStyle.background_color = amical.BACKGROUND
        else:
            amical.AmicalStyle.background_color = background
    else:
        theme = "brunante"
        if background is None:
            brunante.BrunanteStyle.background_color = brunante.BACKGROUND
        else:
            brunante.BrunanteStyle.background_color = background
    CURRENT_THEME = theme

    console = friendly_rich.init_console(
        style=style, theme=theme, color_system=color_system, force_jupyter=force_jupyter
    )
    return console
