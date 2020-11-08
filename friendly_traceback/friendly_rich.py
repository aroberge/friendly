"""Friendly-rich

All Rich-related imports and redefinitions are done here.

"""
import sys

rich_available = True
try:
    from rich import pretty
    from rich.console import Console
    from rich.markdown import Markdown, Heading, CodeBlock
    from rich.panel import Panel  # noqa
    from rich.syntax import Syntax
    from rich.text import Text
    from rich.theme import Theme
    from . import brunante
    import pygments.styles

    # Monkeypatching pygments; inspired by
    # https://gist.github.com/crowsonkb/4e2eb4439e3fe514cc4755b217f164d5
    sys.modules["pygments.styles.brunante"] = brunante
    pygments.styles.STYLE_MAP["brunante"] = "brunante::BrunanteStyle"
except ImportError:
    rich_available = False
    Markdown = None
    Console = None
    brunante = None


def init_console(theme="dark"):
    if not rich_available:
        return None

    def _patch_heading(self, console, options):
        """By default, all headings are centered by Rich; I prefer to have
        them left-justified, except for <h3>
        """
        text = self.text
        text.justify = "left"
        if self.level == 3:
            yield Text("    ") + text
        else:
            yield text

    Heading.__rich_console__ = _patch_heading

    def _patch_code_block(self, console, options):
        code = str(self.text).rstrip()
        if self.lexer_name == "default":
            self.lexer_name = "python"
        if theme == "light":
            syntax = Syntax(code, self.lexer_name, theme="tango")
        else:
            syntax = Syntax(code, self.lexer_name, theme="brunante")
        yield syntax

    CodeBlock.__rich_console__ = _patch_code_block

    _theme = {
        "markdown.h1": "bold #B22518",
        "markdown.h2": "bold #009999 underline",  # Exception message; location header
        "markdown.h3": "bold #CF6A4C",  # likely cause
        "markdown.h4": "bold #CF6A4C",  # warning header
        "markdown.link": "bold #DAEFA3 underline",
        "markdown.code": "#CDA869",
    }
    if brunante is not None:
        _theme.update(**brunante.my_style)

    dark_background_theme = Theme(_theme)
    light_background_theme = Theme(
        {
            "markdown.h1": "bold #B22518",
            "markdown.h2": "bold #B22518 underline",  # Exception message; location header
            "markdown.h3": "bold #0000cf",  # likely cause
            "markdown.h4": "bold #CF6A4C",  # warning header
            "markdown.link": "bold #3465a4 underline",
            "markdown.item.bullet": "#3465a4",
            "markdown.code": "#0000cf",
        }
    )
    if theme == "light":
        console = Console(theme=light_background_theme)
    else:
        console = Console(theme=dark_background_theme)

    # Rich has no version attribute that we can check
    try:
        # indent_guide need Rich version 9.1+
        pretty.install(console=console, indent_guides=True)
    except Exception:
        pretty.install(console=console)
    return console
