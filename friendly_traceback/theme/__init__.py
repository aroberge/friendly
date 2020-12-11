"""Syntax colouring based on the availability of pygments
"""
import sys

try:
    import pygments
    from pygments.styles import get_style_by_name
    from . import brunante

    pygments_available = True
except ImportError:
    pygments_available = False


rich_available = False
current_style = "default"
current_rich_style = "dark"

if pygments_available:
    # Monkeypatching pygments; inspired by
    # https://gist.github.com/crowsonkb/4e2eb4439e3fe514cc4755b217f164d5
    sys.modules["pygments.styles.brunante"] = brunante
    pygments.styles.STYLE_MAP["brunante"] = "brunante::BrunanteStyle"

    try:
        from . import friendly_rich

        rich_available = True
    except ImportError:
        pass


def set_theme(style):

    global current_style, current_rich_style
    if not pygments_available:
        print("Cannot set theme: pygments is not installed.")
        return

    if style == "light":
        style = "tango"
        current_rich_style = "light"  # noqa
    elif style == "dark":
        style = "brunante"

    try:
        get_style_by_name(style)
        current_style = current_rich_style = style
    except Exception:
        print("Could not find pygment style", style)
        try:
            current_style = get_style_by_name("brunante")
            current_style = current_rich_style = style
            print("Using dark style brunante instead.")
        except Exception:
            pass
    return current_style


if rich_available:

    def init_rich_console():
        return friendly_rich.init_console(current_rich_style)
