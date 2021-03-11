"""Friendly-rich

All Rich-related imports and redefinitions are done here.

"""

from rich import pretty  # noqa
from rich.console import Console  # noqa
from rich.markdown import Markdown, Heading, CodeBlock  # noqa
from rich.panel import Panel  # noqa
from rich.syntax import Syntax  # noqa
from rich.text import Text  # noqa
from rich.theme import Theme  # noqa
from . import amical
from . import brunante


dark_background_theme = Theme(brunante.my_style)
light_background_theme = Theme(amical.my_style)


def init_console(
    style="dark", theme="brunante", color_system="auto", force_jupyter=None
):
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
        syntax = Syntax(code, self.lexer_name, theme=theme, word_wrap=True)
        yield syntax

    CodeBlock.__rich_console__ = _patch_code_block

    if style == "light":
        console = Console(
            theme=light_background_theme,
            color_system=color_system,
            force_jupyter=force_jupyter,
        )
    else:
        console = Console(
            theme=dark_background_theme,
            color_system=color_system,
            force_jupyter=force_jupyter,
        )

    pretty.install(console=console, indent_guides=True)
    return console
