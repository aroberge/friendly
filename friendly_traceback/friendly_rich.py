"""Friendly-rich

All Rich-related imports and redefinitions are done here.

"""

rich_available = True
try:
    from rich import box
    from rich.console import Console
    from rich.markdown import Markdown, Heading, CodeBlock
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.text import Text
    from rich.theme import Theme
except ImportError:
    rich_available = False
    Markdown = None
    Console = None


def init_console():
    if not rich_available:
        return None

    def _patch_heading(self, console, options):
        """By default, all headings are centered by Rich; I prefer to have
           them left-justified, except for <h1>
        """
        text = self.text
        text.justify = "left"
        if self.level == 1:
            text.justify = "center"
            # Draw a border around h1s
            yield Panel(text, box=box.DOUBLE, style="markdown.h1.border")
        else:
            # Indent only h2 headers
            if self.level == 2:
                yield Text("    ") + text
            else:
                yield text

    Heading.__rich_console__ = _patch_heading

    def _patch_code_block(self, console, options):
        code = str(self.text).rstrip()
        syntax = Syntax(code, self.lexer_name, theme=self.theme)
        yield syntax

    CodeBlock.__rich_console__ = _patch_code_block

    dark_background_theme = Theme(
        {
            "markdown.h1.border": "bold yellow",
            "markdown.h1": "bold red",
            "markdown.h2": "bold red underline",  # Exception message; location header
            "markdown.h3": "bold green",  # likely cause
            "markdown.h4": "bold red",  # warning header
            "markdown.link": "bold yellow underline",
            "markdown.code": "deep_sky_blue1",
        }
    )
    return Console(theme=dark_background_theme)


console = init_console()
