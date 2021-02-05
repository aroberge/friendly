"""Friendly-rich

All Rich-related imports and redefinitions are done here.

"""
try:
    from rich import pretty  # noqa
    from rich.console import Console  # noqa
    from rich.markdown import Markdown, Heading, CodeBlock  # noqa
    from rich.panel import Panel  # noqa
    from rich.syntax import Syntax  # noqa
    from rich.text import Text  # noqa
    from rich.theme import Theme  # noqa
    from . import brunante

except ImportError:
    Markdown = None
    Console = None
    brunante = None


def init_console(style="dark"):
    def _patch_heading(self, console, options):  # noqa
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

    def _patch_code_block(self, console, options):  # noqa
        code = str(self.text).rstrip()
        if self.lexer_name == "default":
            self.lexer_name = "python"
        if style == "light" or style == "tango":
            syntax = Syntax(code, self.lexer_name, theme="tango", word_wrap=True)
        else:
            syntax = Syntax(code, self.lexer_name, theme=style, word_wrap=True)
        yield syntax

    CodeBlock.__rich_console__ = _patch_code_block

    _theme = {
        "markdown.h1": "bold #B22518",
        "markdown.h2": "bold #009999",  # Exception message; location header
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
            "markdown.h2": "bold #B22518",  # Exception message; location header
            "markdown.h3": "bold #0000cf",  # likely cause
            "markdown.h4": "bold #CF6A4C",  # warning header
            "markdown.link": "bold #3465a4 underline",
            "markdown.item.bullet": "#3465a4",
            "markdown.code": "#0000cf",
        }
    )
    if style == "light" or style == "tango":
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
